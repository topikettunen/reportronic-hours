import json
import os.path

absolute_path = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(absolute_path, "../config/config-test.json")
with open(config_path) as f:
    data = json.load(f)

print(data)
