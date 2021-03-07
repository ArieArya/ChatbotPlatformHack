import requests
import math
import time
import json
import os

# Obtain all secrets
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/secrets.txt') as f:
    secret = f.readlines()
secrets = [x.strip() for x in secret]

api_url = secrets[0]
coupon = secrets[1]
rapid_api_key = secrets[2]
rapid_api_host = secrets[3]

def preprocess_train_data(inp_json):
    alt_inp_length = 5
    alt_out_length = 3
    intents = inp_json['intents']
    preprocessed_intents = []

    for intent in intents:
        new_dict = {'tag': intent['tag']}

        # preprocess patterns
        cur_patterns = intent['patterns']
        cur_pattern_length = len(cur_patterns)
        new_patterns = [x for x in cur_patterns]
        if cur_pattern_length < alt_inp_length:
            num_paraphrases = math.ceil(alt_inp_length / cur_pattern_length)

            cur_count = 0
            cur_idx = 0
            while cur_count <= alt_inp_length - cur_pattern_length and cur_idx < len(cur_patterns):
                original_text = cur_patterns[cur_idx]
                if len(original_text) > 10:
                    paraphrase_list = get_alternatives(
                        original_text, num_paraphrases)

                    # remove all empty strings
                    paraphrase_list = [x for x in paraphrase_list if x != '']

                    # append to old list
                    new_patterns.extend(paraphrase_list)

                    cur_count += num_paraphrases
                    time.sleep(1)
                cur_idx += 1

        # preprocess responses
        cur_responses = intent['responses']
        cur_response_length = len(cur_responses)
        new_responses = [x for x in cur_responses]
        if cur_response_length < alt_out_length:
            num_paraphrases = alt_out_length - cur_response_length

            original_text = cur_responses[0]
            paraphrase_list = get_alternatives(original_text, num_paraphrases)

            # remove all empty strings
            paraphrase_list = [x for x in paraphrase_list if x != '']

            # append to old list
            new_responses.extend(paraphrase_list)

        new_dict['patterns'] = new_patterns
        new_dict['responses'] = new_responses

        preprocessed_intents.append(new_dict)

    return {'intents': preprocessed_intents}


def get_alternatives(inp_text, numParaphrases):
    url = api_url
    inp_dict = {
        "text": inp_text,
        "numParaphrases": numParaphrases,
        "coupon": coupon,
        "includeSegs": True,
        "strength": 3,
        "autoflip": 0.1
    }

    payload = json.dumps(inp_dict)

    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': rapid_api_key,
        'x-rapidapi-host': rapid_api_host
    }

    # wait until api channel unoccupied
    while True:
        try:
            response = requests.request("POST", url, data=payload, headers=headers)
            result = response.json()[0]['paraphrases']

            alternatives = []

            for data in result:
                alternatives.append(data['alt'])

            return alternatives

        except:
            time.sleep(2)