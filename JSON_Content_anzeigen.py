import json

def load_list_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    return data_list

loaded_content_list = load_list_from_json('content.json')
print(loaded_content_list)