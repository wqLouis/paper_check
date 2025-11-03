from typing import TypeVar
import os
import flet as ft
import sqlite3 as sql
import json


T = TypeVar("T")


class preference:

    model_path: str = "./models"
    pfile_target_path: str = "./db/papers"
    db_path: str = "./db"
    ocr_model: str = "./models/ocr"

    setting_dict: dict = {  # Will be used to replace original preference
        "model_path": "./models",
        "pfile_target_path": "./db/papers",
        "db_path": "./db",
        "ocr_path": "./models/ocr",
        "temp_path": "./db/temp",
        "preference_path": "./preference",
        "plugins_path": "./plugins"
    }

    def check_dir_valid(self, text_field: ft.TextField, page: ft.Page) -> bool:
        if text_field.value is None:
            return False

        if os.path.isdir(text_field.value or "") or os.path.exists(text_field.value or "") or text_field.value == "DEBUG":
            try:
                self.setting_dict[text_field.label] = text_field.value or ""
                text_field.error_text = None
            except KeyError:
                return False
            return True
        else:
            text_field.error_text = "Invalid directory"
            page.update()
            return False

    def construct_textfield(self) -> list[ft.TextField]:
        result: list[ft.TextField] = []

        for key in self.setting_dict:
            result.append(
                ft.TextField(
                    label=key,
                    value=self.setting_dict[key],
                    read_only=True if key == "preference_path" else False,
                )
            )

        return result

    def save_on_disk(self):
        with open(
            f"{self.setting_dict["preference_path"]}/preference.json", mode="w"
        ) as f:
            json.dump(self.setting_dict, f, indent=4)
        load() # Sync new preference


class pattributes:
    """
    types available for past papers
    """

    types: set[str] = set(["DSE", "ALV", "CE", "OTHERS"])
    sbjs: set[str] = set(["MATH", "PHY", "CHEM", "BIO", "ICT", "OTHERS"])

    attribute_dict: dict = {
        "types" : "set(str)",
        "sbjs" : "set(str)",
        "year" : "intFromTo"
    }
    subattribute_dict: dict ={
        "sbjs" : sbjs,
        "types" : types
    }

def unwrap(value: T | Exception) -> T:
    """
    unwrap function return value and raise error

    Args:
        value:
            return variable of the function

    Returns:
        the value itself
    """
    if isinstance(value, Exception):
        raise value
    else:
        return value


def init_db() -> Exception | sql.Connection:
    """
    Initialize sqlite database with basic structures
    """

    if not os.path.exists(preference.db_path):
        try:
            os.mkdir(preference.db_path)
        except Exception as e:
            return e

    if not os.path.exists(preference.pfile_target_path):
        try:
            os.mkdir(preference.pfile_target_path)
        except Exception as e:
            return e

    con: sql.Connection = sql.connect(preference.db_path)
    cur: sql.Cursor = con.cursor()

    table_count: int = int(
        cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table';"
        ).fetchone()[0]
    )
    if table_count > 0:
        return con
    try:
        cur.execute(
            """
        CREATE TABLE psource(
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            pfile_path TEXT NOT NULL,
            pyear INTEGER NOT NULL,
            psbj TEXT,
            ptype TEXT
        );
        """
        )
        cur.execute(
            """
        CREATE TABLE qsource(
            qid INTEGER PRIMARY KEY AUTOINCREMENT,
            qstr TEXT NOT NULL,
            pid INTEGER NOT NULL,
            FOREIGN KEY (pid) REFERENCES psource(pid)
        );
        """
        )

        con.commit()

        return con
    except Exception as e:
        con.close()
        return e

def sync_preference() -> None:
    preference.model_path = preference.setting_dict["model_path"]
    preference.pfile_target_path = preference.setting_dict["pfile_target_path"]
    preference.db_path = preference.setting_dict["db_path"]
    preference.ocr_model = preference.setting_dict["ocr_path"]


def load():
    if os.path.exists(f"{preference.setting_dict["preference_path"]}/preference.json"):
        with open(
            f"{preference.setting_dict["preference_path"]}/preference.json", mode="r"
        ) as f:
            preference.setting_dict = json.load(f)
        sync_preference()


load()