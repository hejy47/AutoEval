import os

PROJECT_DIR = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__))))
DATASET_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")

GPT_MODELS = {
    "4o" : "gpt-4o-2024-08-06",
    "4omini" : "gpt-4o-mini-2024-07-18",
    "4t" : "gpt-4-turbo-2024-04-09",
    "3.5" : "gpt-3.5-turbo-0125",
    "4" : "gpt-4-0125-preview",
    "3.5old" : "gpt-3.5-turbo-1106",
    "4old" : "gpt-4-1106-preview"
}

CLAUDE_MODELS = {
    "sonnet3.5": "claude-3-5-sonnet-20240620",
    "3.5sonnet": "claude-3-5-sonnet-20240620",
    "claude3.5sonnet": "claude-3-5-sonnet-20240620",
    "claude3.5": "claude-3-5-sonnet-20240620",

    "opus":"claude-3-opus-20240229",
    "sonnet": "claude-3-sonnet-20240229",
    "haiku": "claude-3-haiku-20240307",
    "claude3_opus":"claude-3-opus-20240229",
    "claude3_sonnet": "claude-3-sonnet-20240229",
    "claude3_haiku": "claude-3-haiku-20240307",
    
    "claude2.1": "claude-2.1",
    "claude2.0": "claude-2.0",
    "claude2": "claude-2.0"
}

LLM_MODEL_REDIRECTION = {
    '4omini' : GPT_MODELS["4omini"],
    '4o' : GPT_MODELS["4o"],
    '4t' : GPT_MODELS["4t"],
    '3.5' : GPT_MODELS["3.5"],
    3.5 : GPT_MODELS["3.5"],
    '4' : GPT_MODELS["4"],
    '4.0' : GPT_MODELS["4"],
    4 : GPT_MODELS["4"],
    "3.5old" : GPT_MODELS["3.5old"],
    "4old" : GPT_MODELS["4old"]
}

LLM_MODEL_REDIRECTION = {**LLM_MODEL_REDIRECTION, **CLAUDE_MODELS}

ALL_RUN_MODES = ["chatgpt", "iverilog", "autoline", "dataset_manager"]

DEFAULT_PROBLEM_CONFIG = {
    "run": {
        "mode": "autoline"
    },
    "save": {
        "en": True,
        "root": os.path.join(OUTPUT_DIR, "default"),
        "pub": {
            "dir": OUTPUT_DIR,
            "subdir": "default"
        },
        "log": {
            "en": True,
            "path": os.path.join(OUTPUT_DIR, "default", "log.txt")
        }
    },
    "load": {
        "prompt": None,
        "template": None
    },
    "llm": {
        "model": "4omini",
        "api_key_path": "config/key_API.json"
    },
    "autoline": {
        "probset": {
            "path": None,
            "mutant_path": None,
            "gptgenRTL_path": None,
            "more_info_paths": [],
            "only": [],
            "exclude": [],
            "exclude_json": None,
            "filter": [{}]
        },
        "checklist": {
            "max": 3
        },
        "debug": {
            "max": 5,
            "reboot": 1,
            "py_rollback": 2
        },
        "onlyrun": None,
        "error_interruption": False,
        "timeout": 60,
        "save_compile": True
    }
}

RUN_MODE = None
PROBLEM_CONFIG_PATH = None