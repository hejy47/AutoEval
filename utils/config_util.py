import yaml
import json
import os
import config
from types import SimpleNamespace

class DictToObject:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DictToObject(value))
            else:
                setattr(self, key, value)

def load_config_to_obj(config_path):
    conf = load_config(config_path)
    conf_obj = DictToObject(conf)
    process_config(conf_obj)
    return conf_obj

def process_config(conf):
    if conf.save.en:
        conf.save.root = os.path.join(conf.save.pub.dir, conf.save.pub.subdir)
    if conf.llm.model in config.LLM_MODEL_REDIRECTION:
        conf.llm.model = config.LLM_MODEL_REDIRECTION[conf.llm.model]

def load_config(config_path):
    user_config = None
    if config_path.endswith(".yaml"):
        user_config = load_yaml_config(config_path)
    elif config_path.endswith(".json"):
        user_config = load_json_config(config_path)
    
    if user_config is not None:
        merged_config = merge_configs(config.DEFAULT_PROBLEM_CONFIG, user_config)
        return merged_config
    else:
        return config.DEFAULT_PROBLEM_CONFIG

def load_yaml_config(config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config

def load_json_config(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

def merge_configs(defaults, user_config):
    if isinstance(defaults, dict) and isinstance(user_config, dict):
        merged = defaults.copy()
        for key, value in user_config.items():
            if key in merged:
                merged[key] = merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    return user_config if user_config is not None else defaults