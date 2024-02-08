# Global Imports
import json
import os

# Local Imports

# Decorators
def check_db(func):
    def wrapper(month, *args, **kwargs):
        try:
            if not os.path.exists(f"./data/{month}"):
                os.mkdir(f"./data/{month}")
            if not os.path.exists(f"./data/{month}/db.json"):
                with open (f"./data/{month}/db.json", 'w') as output:
                    print('{}', end='', file=output)
            return func(month, *args, **kwargs)
        except Exception as e:
            return False, e
    return wrapper



def loadProfile(profile_path):
    with open(profile_path, 'r') as f:
        return json.load(f)