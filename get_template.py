import json


def get_template_json(template_name):
    try:
        template_dir = 'json_templates/' + str(template_name) + '.json'
        with open(template_dir) as file:
            json_template = json.load(file)
        
        return json_template
    
    except:
        return {}
        
