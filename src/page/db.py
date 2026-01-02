import sqlite3 as sql
import os
import flet as ft

from src.config import config


def check_db():
    db_path = config.get("db_path")
    if db_path is None:
        raise Exception("Broken config")
    if not os.path.exists(db_path):
        try:
            init_db()
        except BaseException as e:
            raise e
        try:
            sql.connect(db_path)
        except BaseException:
            try:
                os.remove(db_path)
                init_db()
            except BaseException as e:
                raise e


def init_db():
    db_path = config.get("db_path")
    if db_path is None:
        raise Exception("Broken config")

    with sql.connect(db_path) as con:
        del db_path
        cur = con.cursor()
        query = """CREATE TABLE [IF NOT EXISTS] papers (
                    id INTEGER PRIMARY KEY,
                    year INTEGER NOT NULL,
                    form TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    path TEXT NOT NULL,
                    )"""
        try:
            cur.execute(query)
        except BaseException as e:
            raise e


def page_content():
    return ft.Text("View database", size=24)


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Database"))
