import json


class Config:
    def __init__(self):
        with open('config.json', 'r') as f:
            self.store = json.load(f)

    def get_item(self, key):
        return self.store[key]
