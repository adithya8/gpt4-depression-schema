import argparse

def parse_api_run_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expt_name", help="Experiment name in config file to read and operate", type=str)
    parser.add_argument("--save_folder_path", help="Folder Path to save All data to", type=str)
    parser.add_argument("--openai_model_name", help="Name of the OpenAI model to use", default="gpt-3.5-turbo", 
                        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview", "gpt-4-0613"], type=str)
    parser.add_argument("--max_tokens", help="Max tokens to use for the model", default=350, type=int)
    # Add arg for max_replies for chat completion
    parser.add_argument("--cache_path", help="Path to save cache to", type=str)
    parser.add_argument("--temperature", help="Temperature to use for the model", default=0.0, type=float)
    parser.add_argument("--top_p", help="Top p to use for the model", default=1.0, type=float)
    parser.add_argument("--frequency_penalty", help="Frequency penalty to use for the model", default=0.1, type=float)
    parser.add_argument("--presence_penalty", help="Presence penalty to use for the model", default=0.0, type=float)
    parser.add_argument("--data_path", help="Path to load Task data from", type=str)
    parser.add_argument("--api_key_name", help="API Key name to use from .api_key file. Defaults to default", 
                        default="default", type=str)
    parser.add_argument("--demo", help="Run a demo of the experiment", action="store_true") 
    return parser.parse_args()


def parse_response_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expt_name", help="Experiment name in config file to read and operate", type=str)
    parser.add_argument("--save_folder_path", help="Folder Path to save All data to", type=str)
    parser.add_argument("--openai_model_name", help="Name of the OpenAI model to use", default="gpt-3.5-turbo",
                        choices=["gpt-3.5-turbo", "gpt-4"], type=str)
    # parser.add_argument("--data_path", help="Path to load Task data from", type=str)
    return parser.parse_args()