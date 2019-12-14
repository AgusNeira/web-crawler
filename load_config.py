import json

def load_config():
    try:
        fi = open('config.json', 'r')
        config = json.loads(fi.read())
        fi.close()
        return config
    except IOError:
        print('Couldn\'t access config file. It may have been deleted')
        print('Visit \'help recover\' or re-clone the project to fix this problem')
