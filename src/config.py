"""This is a script for reading and writing config files"""

import os

import toml

config: dict = {"ocr_model_path": "", "db_path": "", "page_path": "./src/page/*.py"}
config_path: str = "~/.config/paper_check.toml"


def get(key: str):
    return config.get(key)


def put(key: str, value: str) -> bool:
    if key.split("_")[-1] == "path":
        if not os.path.exists(value):
            return False
    if key in config:
        return False

    config[key] = value
    return True


def commit():
    pass


# init function
def init():
    if not os.path.exists(os.path.dirname(config_path)):
        try:
            os.mkdir(os.path.dirname(config_path))
        except BaseException as e:
            raise e
    if not os.path.exists(config_path):
        pass  # create file
    # load to config dict


# init()
