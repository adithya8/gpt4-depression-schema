import logging
import os
import pandas as pd
from tqdm import tqdm

from src import parse_api_run_args, get_api_key, OpenAICommunicator
from prompt_templates import templates

if __name__ == "__main__":
    args = parse_api_run_args()
    
    if args.expt_name not in templates:
        raise ValueError("Experiment name {} not found in templates.\n Choices: {}".format(args.expt_name, list(templates.keys())))
            
    run_folder_path = args.save_folder_path
    prompts_dir = os.path.join(run_folder_path, "expts/prompts")
    responses_dir = os.path.join(run_folder_path, "expts/responses")
    logs_dir = os.path.join(run_folder_path, "expts/logs")
    
    # makedir if not exists
    os.makedirs(run_folder_path, mode=700, exist_ok=True)
    os.makedirs(prompts_dir, mode=770, exist_ok=True)
    os.makedirs(responses_dir, mode=700, exist_ok=True)
    os.makedirs(logs_dir, mode=700, exist_ok=True)
    
    
    expt_metainfo = '.'.join([args.expt_name, args.openai_model_name])
    log_file_path = os.path.join(run_folder_path, "expts/logs/{}.log".format(expt_metainfo))
    logging.basicConfig(level=logging.INFO, filename=log_file_path, 
                    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
    print ("Logging to {}".format(log_file_path))
    logging.info("Starting Experiment {}".format(args.expt_name))
    
    args_dict = args.__dict__
    logging.info("Args: {}".format(args))
    
    args.api_key = get_api_key(api_key_file=".api_key", api_key_name=args.api_key_name)
    logging.info("API Key loaded")
    
    # prompts_file_path = os.path.join(prompts_dir, "{}.csv".format(expt_metainfo))
    # logging.info("Storing prompts to {}".format(prompts_file_path))
    responses_file_path = os.path.join(responses_dir, "{}.csv".format(expt_metainfo))
    logging.info("Storing responses to {}".format(responses_file_path))
        
    openai_communicator = OpenAICommunicator(args_dict)
    logging.info("OpenAI Communicator initialized")
    
    # Load instruction
    instruction = templates[args.expt_name]
    
    # load dataset
    data = pd.read_csv(args.data_path)
    if "dep" in args.expt_name:
        df = data[['user_id', 'dep_text', 'phq_tot']]
        df = df.rename(columns={'dep_text': 'input_text', 'phq_tot': 'target_value'})
    elif "anx" in args.expt_name:
        df = data[['user_id', 'anx_text', 'gad_tot']]
        df = df.rename(columns={'anx_text': 'input_text', 'gad_tot': 'target_value'})
    else:
        raise ValueError("Experiments supported are anx and dep")    

    user_ids, input_texts, target_values = df.iloc[:, 0].tolist(), df.iloc[:, 1].tolist(), df.iloc[:, 2].tolist()
    
    output_list = []
    for idx in tqdm(range(len(user_ids)), desc="Running inference with {}".format(args.openai_model_name)):
        row_id, input_text, target_value = user_ids[idx], input_texts[idx], target_values[idx]
        
        instruction_with_text = instruction.format(input_text)
        input_prompt = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": instruction_with_text}
        ]
        response_text = openai_communicator.run_inference(input_prompt)
        output_json = {'user_id': row_id, 'input_text': input_prompt, 'target_value': target_value, 'response_text': response_text}
        output_list.append(output_json)
    
    output_df = pd.DataFrame(output_list)
    output_df.to_csv(responses_file_path, index=False)
    logging.info("Responses saved to {}".format(responses_file_path))
    
    logging.info("Experiment {} completed".format(args.expt_name))
    print ("Experiment {} completed".format(args.expt_name))