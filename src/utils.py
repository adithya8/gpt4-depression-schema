import json
import os

def get_api_key(api_key_file, api_key_name='default'):
    
    if os.path.exists(api_key_file):
        keys = json.load(open(api_key_file))
        if api_key_name in keys:
            return keys[api_key_name]
        else:
            raise ValueError("API Key name {} not found in the api key file".format(api_key_name))
    else:
        raise ValueError("API Key file not found at {}".format(api_key_file))