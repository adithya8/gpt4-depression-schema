import json
import logging
import os
from enum import Enum
import time

from tqdm import tqdm
from pydantic import BaseModel, Field
from openai import OpenAI
import pandas as pd

from src import get_api_key, parse_api_run_args
from prompt_templates import templates

class SymptomOptions(str, Enum):
    depressed_mood = 'Depressed Mood'
    anhedonia = 'Anhedonia'
    insomnia_hypersomnia = 'Insomnia or Hypersomnia'
    fatigue = 'Fatigue'
    poor_appetite_overeating = 'Poor appetite or overeating'
    worthlessness_guilt = 'Worthlessness or guilt'
    difficulty_concentration = 'Difficulty concentration'
    psychomotor_agitation_retardation = 'Psychomotor agitation or retardation'
    suicidal_ideation = 'Suicidal Ideation'

class Symptom(BaseModel):
    name: SymptomOptions
    evidences_and_reasons: list[str] 
    score: int = Field(ge=0, le=3)

class Step(BaseModel):
    symptoms: list[Symptom]

class FinalAssessment(BaseModel):
    combined_score: int = Field(ge=0, le=27)
    category: str = Field(pattern=r"^(None|Mild|Moderate|Moderately Severe|Severe)$")

class AssessmentPacket(BaseModel):
    explicit_symptoms_step: Step
    implicit_symptoms_step: Step
    final_estimate: FinalAssessment

class OAICommunicator:
    def __init__(self, api_key, model_name, max_output_tokens=None, reasoning_parameters:dict=None):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.max_output_tokens = max_output_tokens
        self.reasoning_parameters = reasoning_parameters
    
    def send_message(self, context:list, reasoning_parameters:dict=None, text_format=None):
        
        response = self.client.responses.parse(
                model = self.model_name,
                max_output_tokens = self.max_output_tokens,
                input = context,
                reasoning = self.reasoning_parameters if reasoning_parameters is None else reasoning_parameters,
                text_format = text_format
            )
        
        return response


if __name__ == '__main__':
    
    args = parse_api_run_args()
    
    if args.expt_name not in templates:
        raise ValueError("Experiment name {} not found in templates.\n Choices: {}".format(args.expt_name, list(templates.keys())))
    
    run_folder_path = args.save_folder_path
    # prompts_dir = os.path.join(run_folder_path, "expts/prompts")
    responses_dir = os.path.join(run_folder_path, "expts/responses")
    logs_dir = os.path.join(run_folder_path, "expts/logs")
    
    # makedir if not exists
    os.makedirs(run_folder_path, mode=700, exist_ok=True)
    # os.makedirs(prompts_dir, mode=770, exist_ok=True)
    os.makedirs(responses_dir, mode=700, exist_ok=True)
    os.makedirs(logs_dir, mode=700, exist_ok=True)
        
    prefix = 'demo_' if args.demo else 'expt_'
    expt_metainfo = '.'.join([prefix+args.openai_model_name, args.expt_name])
    log_file_path = os.path.join(run_folder_path, "expts/logs/{}.log".format(expt_metainfo))
    
    logging.basicConfig(level=logging.INFO, filename=log_file_path, 
                format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
    print ("Logging to {}".format(log_file_path))
    logging.info("Starting Experiment {}".format(args.expt_name))

    responses_file_path = os.path.join(responses_dir, "{}.csv".format(expt_metainfo))
    logging.info("Storing responses to {}".format(responses_file_path))

    api_key  = get_api_key('.api_key', api_key_name='gpt5_schema_paper')
    oai_communicator = OAICommunicator(api_key=api_key,
                                       model_name=args.openai_model_name,
                                    max_output_tokens=args.max_tokens, 
                                    reasoning_parameters={
                                                            'summary':'auto', 
                                                            'effort':'minimal'}
                                    )

    # Load instruction
    instruction = templates[args.expt_name]

    # load dataset
    data = pd.read_csv(args.data_path)
    if "dep" in args.expt_name:
        df = data[['user_id', 'dep_text', 'phq_score']]
        df = df.rename(columns={'dep_text': 'input_text', 'phq_score': 'target_value'})
    elif "anx" in args.expt_name:
        df = data[['user_id', 'anx_text', 'gad_score']]
        df = df.rename(columns={'anx_text': 'input_text', 'gad_score': 'target_value'})
    else:
        raise ValueError("Experiments supported are anx and dep")    

    if args.demo:
        df = df.head(5)

    user_ids, input_texts, target_values = df.iloc[:, 0].tolist(), df.iloc[:, 1].tolist(), df.iloc[:, 2].tolist()
    logging.info("Loaded {} rows of data for Inference.".format(len(user_ids)))
    
    query_response_time = []
    start_time = time.time()
    output_list = []
    for idx in tqdm(range(len(user_ids)), desc="Running inference with {}".format(args.openai_model_name)):
        row_id, input_text, target_value = user_ids[idx], input_texts[idx], target_values[idx]
        
        if (pd.isna(input_text)) or (pd.isnull(input_text)):
            continue
        instruction_with_text = instruction.format(text=input_text.strip())
        input_prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": instruction_with_text}
        ]
        query_start_time = time.time()
        response_packet = oai_communicator.send_message(input_prompt, text_format=AssessmentPacket) 
        query_response_time.append(time.time() - query_start_time)
        # import pdb; pdb.set_trace()
        response_text = response_packet.output[1].content[0].text
        output_json = {'user_id': row_id, 'input_text': input_prompt, 'target_value': target_value, 'response_packet': json.dumps(response_packet.dict()),
                       'response_text': response_text.strip(), 'user_text': input_text.strip()}
        output_list.append(output_json)
    end_time = time.time()
    
    total_time = round(end_time - start_time, 2)
    avg_response_time = round(sum(query_response_time)/len(query_response_time), 2)
    logging.info("Total time taken for inference of {} rows: {}".format(len(output_json), total_time))
    logging.info("Average time taken for inference of {} rows: {}".format(len(output_json), avg_response_time))
    
    output_df = pd.DataFrame(output_list)
    output_df.to_csv(responses_file_path, index=False)
    logging.info("Responses saved to {}".format(responses_file_path))
    
    logging.info("Experiment {} completed".format(args.expt_name))
    print ("Experiment {} completed".format(args.expt_name))