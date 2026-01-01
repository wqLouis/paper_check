import sqlite3 as sql

import flet as ft

from src.config import config


def check_db():
    pass


def init_db():
    db_path = config.get("db_path")
    if db_path is None:
        raise Exception("Broken config")

    with sql.connect(db_path) as con:
        del db_path
        cur = con.cursor()
        query = """"""
        try:
            cur.execute(query)
        except BaseException as e:
            raise e


def page_content():
    return ft.Text("View database", size=24)


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Database"))
