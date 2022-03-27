import json

def extract_json():
    file_ = open("settings.json")
    return json.load(file_)