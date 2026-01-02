"""This is a script for reading and writing config files"""

import os

import toml

config: dict = {
    "ocr_model_path": "",
    "db_path": "",
    "forms": ["f1", "f2", "f3", "f4", "f5", "f6"],
    "subjects": [
        "chin",
        "eng",
        "math",
        "phy",
        "chem",
        "bio",
        "cs",
        "econ",
        "bafs",
        "ict",
        "hist",
        "chist",
        "clit",
        "m2",
    ],
    "paper_path" : ""
}
fallback_config = config.copy()
config_path: str = "./config.toml"
page_path: str = "./src/page/*.py"


def commit():
    with open(config_path, "w") as f:
        toml.dump(config, f)


# init function
def init():
    global config

    if not os.path.exists(os.path.dirname(config_path)):
        try:
            os.mkdir(os.path.dirname(config_path))
        except BaseException as e:
            raise e
    if not os.path.exists(config_path):
        commit()

    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
    except toml.decoder.TomlDecodeError:
        config = fallback_config
    except BaseException as e:
        raise e


init()
