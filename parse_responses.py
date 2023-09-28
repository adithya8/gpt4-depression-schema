# Description: Parse GPT4 responses for analysis

import os
import pandas as pd

from src import parse_response_args, simple_response_parser


if __name__ == "__main__":
    args = parse_response_args()
    
    run_folder_path = args.save_folder_path
    responses_dir = os.path.join(run_folder_path, "expts/responses")
    parsed_dir = os.path.join(run_folder_path, "expts/parsed_responses")
    expt_metainfo = '.'.join(['expt_'+args.openai_model_name, args.expt_name])
    response_file = os.path.join(responses_dir, "{}.csv".format(expt_metainfo))
    
    if not os.path.exists(response_file):
        print ("Response file {} not found".format(response_file))
        exit(1)
    
    response_df = pd.read_csv(response_file)
    response_df.input_text = response_df.input_text.apply(lambda x: eval(x)[-1]['content'])
    
    if args.expt_name in set(['dep_list_evidence_classify_estimate']):
        response_df['parsed_response'] = response_df['response_text'].apply(simple_response_parser)
    else:
        print ("No response parser found for experiment {}".format(args.expt_name))
        exit(1)
        
    parsed_response_df = pd.DataFrame(response_df['parsed_response'].tolist(), index=response_df.index)
    
    parsed_response_df = pd.concat([response_df[['user_id', 'input_text', 'target_value']], parsed_response_df], axis=1)
    
    parse_save_path = os.path.join(parsed_dir, "{}.csv".format(expt_metainfo))
    parsed_response_df.to_csv(parse_save_path, index=False)
    print ("Parsed responses saved to {}".format(parse_save_path))