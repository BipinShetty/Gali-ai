import os
import json

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.json"))

# get the key from config.json or env

def get_openai_key():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            key = json.load(f).get("OPENAI_API_KEY")
            if key:
                return key
            else:
                print("OPENAI_API_KEY not found in config.json.")
    print(f"config.json not found at: {CONFIG_PATH}")
    return os.getenv("OPENAI_API_KEY")
