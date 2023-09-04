# -*- coding: utf-8 -*-
__author__ = """Yash Kumar Lal, Github@ykl7
                Adithya V Ganesan, Github@adithya8"""

import os
import openai
import pickle
import time
import os
import hashlib
import atexit

class OpenAICommunicator:

    def __init__(self, options):

        atexit.register(self.cleanup)

        openai.api_key = options["api_key"]
        self.model_name = options["openai_model_name"]
        self.max_tokens = options["max_tokens"]
        self.cache_path = options["cache_path"]
        self.temp = options["temperature"]
        self.top_p = options["top_p"]
        self.frequency_penalty = options["frequency_penalty"]
        self.presence_penalty = options["presence_penalty"]
        self.cached_responses = self.load_cache_if_exists()

    def load_cache_if_exists(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'rb') as handle:
                cache_file = pickle.load(handle)
                return cache_file
        else:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            return {}

    def cleanup(self):
        # works similar to a destructor but does not offload builtins.open method.
        print(f"\nFinal cleanup cache saving...", end="...")
        with open(self.cache_path, 'wb') as handle:
            pickle.dump(self.cached_responses, handle)

    def make_openai_api_call(self, prompt):
        
        try:
            if self.model_name in ['gpt-3.5', 'gpt-4']:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=prompt,
                    temperature=self.temp,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty
                )
                return self.parse_chatgpt_api_response(response)
            else:
                # gpt3 API call + response
                response = openai.Completion.create(
                    model=self.model_name,
                    prompt=prompt,
                    temperature=self.temp,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty
                )
                return self.parse_gpt3_api_response(response)
        except openai.error.ServiceUnavailableError:
            print("Service unavailable error hit")
            time.sleep(20)
            return self.make_openai_api_call(prompt)
        except openai.error.RateLimitError:
            print("Rate limit error hit")
            time.sleep(60)
            return self.make_openai_api_call(prompt)

    def parse_gpt3_api_response(self, response):
        choices = response["choices"]
        return choices[0]["text"].strip(), response

    def parse_chatgpt_api_response(self, response):
        choices = response["choices"]
        main_response = choices[0].message
        main_response_message, main_response_role = main_response["content"], main_response["role"]
        # process "finish_reason" to check for "stop" or "length"
        return main_response_message, response

    def run_inference(self, prompt):

        hashed_prompt = hashlib.sha256(str(prompt).encode("utf-8")).hexdigest()
        cache_key = (hashed_prompt, self.model_name, self.max_tokens, self.temp, self.top_p, self.frequency_penalty, self.presence_penalty)
        if cache_key in self.cached_responses:
            print(f"Using cached response")
            response_text = self.cached_responses[cache_key]['text']
        else:
            print(f"Running {self.model_name}")
            response_text, response = self.make_openai_api_call(prompt)
            self.cached_responses[cache_key] = {'text': response_text, 'object': response}
            with open(self.cache_path, 'wb') as handle:
                pickle.dump(self.cached_responses, handle)
            time.sleep(5)

        return response_text