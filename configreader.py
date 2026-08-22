import json
import os
import sys
import time
import termcolor

from termcolor import colored

CONFIG_KEYS = [
    "check_info",
    "check_firstname",
    "check_secondname",
    "check_day_of_birth",
    "check_email"
]



def load_config(filename=None):
    if filename is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, 'config.json')

    lines = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip().startswith('#'):
                    lines.append(line)

        raw_config = json.loads("\n".join(lines))
        print(colored("info:", 'green'), colored("config file found", 'white'))

        cleaned_config = {}
        for key in CONFIG_KEYS:
            cleaned_config[key] = raw_config.get(key, None)

        return cleaned_config

    except FileNotFoundError:
        print(colored("error:", 'red'), colored("config file not found", 'white'))
        return {key: None for key in CONFIG_KEYS}

    except json.JSONDecodeError:
        print(colored("error:", 'red'), colored("invalid JSON in config file", 'white'))
        return {key: None for key in CONFIG_KEYS}


config = load_config()
