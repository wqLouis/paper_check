"""This is a script for reading and writing config files"""

import pathlib

import toml

config: dict = {
    "general": {
        "ocr_model_path": "./",
        "db_path": "./db/paper.db",
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
        "paper_path": "./db/papers/",
        "markdown_path": "./db/md/",
        "reports_path": "./reports/",
    },
    "paddle ocr": {},
}
fallback_config = config.copy()
config_path = pathlib.Path("./config.toml")
page_path: str = "./src/page/*.py"


def commit():
    with open(config_path, "w+") as f:
        toml.dump(config, f)


def check_config():
    broken_path = []
    invalid_config = []
    for key, val in config.items():
        if isinstance(val, dict):
            for k, v in val.items():
                if isinstance(v, dict):
                    invalid_config.append(".".join([key, k]))
                if (
                    isinstance(k, str)
                    and k.split("_")[-1] == "path"
                    and isinstance(v, str)
                ):
                    if not pathlib.Path(v).exists():
                        broken_path.append(".".join([key, k]) + f"    path:{v}")
    if len(broken_path) + len(invalid_config) > 0:
        raise Exception(("\n".join(broken_path)) + "\n" + "\n".join(invalid_config))


# init function
def init():
    global config

    try:
        config_path.parent.mkdir(exist_ok=True, parents=True)
    except BaseException as e:
        raise e
    if not config_path.exists():
        commit()

    try:
        with open(config_path, "r") as f:
            config = toml.load(f)
        try:
            check_config()
        except BaseException as e:
            print(e)
            config = fallback_config
    except toml.decoder.TomlDecodeError:
        config = fallback_config
    except BaseException as e:
        raise e


init()
