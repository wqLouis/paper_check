import os
import sqlite3 as sql

import flet as ft

from src.config import config


def check_db():
    db_path = (config.get("general") or {}).get("db_path")
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
    if os.path.exists(db_path):
        try:
            init_db()
        except BaseException as e:
            raise e


def init_db():
    db_path = (config.get("general") or {}).get("db_path")
    if db_path is None:
        raise Exception("Broken config")

    with sql.connect(db_path) as con:
        del db_path
        cur = con.cursor()
        query = """CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY,
                    year INTEGER NOT NULL,
                    form TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    path TEXT NOT NULL,
                    notes TEXT
                    );"""
        try:
            cur.execute(query)
            con.commit()
        except BaseException as e:
            raise e


def build_table():
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Select")),
            ft.DataColumn(ft.Text("id")),
            ft.DataColumn(ft.Text("year")),
            ft.DataColumn(ft.Text("form")),
            ft.DataColumn(ft.Text("subject")),
            ft.DataColumn(ft.Text("path")),
            ft.DataColumn(ft.Text("notes")),
            ft.DataColumn(ft.Text("content")),
        ]
    )

    db_path = (config.get("general") or {}).get("db_path")
    if not db_path:
        raise Exception("Broken config")

    with sql.connect(db_path) as con:
        cur = con.cursor()
        rows: list[ft.DataRow] = []

        result = cur.execute("SELECT * FROM papers;").fetchall()
        for i in result:
            rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(content=ft.Checkbox())]
                    + [ft.DataCell(content=ft.Text(str(j))) for j in i[:4]]
                    + [
                        ft.DataCell(
                            content=ft.ElevatedButton(
                                text=os.path.basename(i[5]),
                                url=f"file:///{os.path.abspath(i[5])}",
                            )
                        )
                    ]
                    + [ft.DataCell(content=ft.Text(str(i[6])))]
                    + [
                        ft.DataCell(
                            content=ft.ElevatedButton(
                                text=os.path.basename(i[4]),
                                url=f"file:///{os.path.abspath(i[4])}",
                            )
                        )
                    ]
                )
            )
        table.rows = rows

    return ft.Row([table], scroll=ft.ScrollMode.ADAPTIVE)


def page_content():
    content_area = ft.Column(
        controls=[ft.Text("View database", size=24)], scroll=ft.ScrollMode.ADAPTIVE
    )

    table = build_table()

    def select_all(e):
        pass

    search_area = ft.Row(
        spacing=12,
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[
            ft.TextField(label="id"),
            ft.TextField(label="year"),
            ft.TextField(label="form"),
            ft.TextField(label="subject"),
            ft.TextField(label="notes"),
            ft.IconButton(icon=ft.Icons.SEARCH),
            ft.Checkbox(label="Select all", on_change=select_all),
            ft.ElevatedButton(text="To check =>"),
        ],
    )

    content_area.controls.append(search_area)
    content_area.controls.append(table)
    return content_area


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Database"))
