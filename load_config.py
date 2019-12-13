import json

def load_config():
    fi = open('config.json')
    config = json.loads(fi.read())
    fi.close()
    return config
