import os
import pathlib
import sqlite3 as sql

import flet as ft

from src.config import config


def check_db():
    db_path = (config.get("general") or {}).get("db_path")
    if db_path is None:
        raise Exception("Broken config")
    db_path = pathlib.Path(db_path)
    if not db_path.exists:
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
    if db_path.exists:
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


def build_table(
    params: dict | None = None,
    set_selected: dict | None = None,
    selected: dict[str, bool] = {},
):
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

        result = (
            cur.execute(
                """
            SELECT * FROM papers
            WHERE (:id = '' OR id = :id)
            AND (:form = '' OR form = :form)
            AND (:subject = '' OR subject = :subject)
            AND (:notes = '' OR notes = :notes)
            AND (:from_year = '' OR year >= :from_year)
            AND (:to_year = '' OR year <= :to_year);""",
                params,
            ).fetchall()
            if params is not None
            else cur.execute("SELECT * FROM papers;").fetchall()
        )
        for i in result:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            content=ft.Checkbox(
                                value=False
                                if set_selected is None
                                else True
                                if set_selected.get(str(i[0]))
                                else False,
                                on_change=lambda e: selected.update(
                                    {str(i[0]): True if e.data == "true" else False}
                                ),
                            )
                        )
                    ]
                    + [ft.DataCell(content=ft.Text(str(j))) for j in i[:4]]
                    + [
                        ft.DataCell(
                            content=ft.ElevatedButton(
                                text=pathlib.Path(i[5]).name,
                                url=f"file:///{pathlib.Path(i[5]).resolve()}",
                            )
                        )
                    ]
                    + [ft.DataCell(content=ft.Text(str(i[6])))]
                    + [
                        ft.DataCell(
                            content=ft.ElevatedButton(
                                text=pathlib.Path(i[4]).name,
                                url=f"file:///{pathlib.Path(i[4]).resolve()}",
                            )
                        )
                    ]
                )
            )
        table.rows = rows

    return table


def page_content():
    content_area = ft.Column(
        controls=[ft.Text("View database", size=24)], scroll=ft.ScrollMode.ADAPTIVE
    )

    table = build_table()

    selected = {
        i.cells[1].content.value or ""
        if isinstance(i.cells[1].content, ft.Text)
        else "": False
        for i in table.rows or []
    }

    table.rows = build_table(selected=selected).rows

    def select_all(e: ft.ControlEvent):
        checkboxes = [i.cells[0].content for i in table.rows or []]
        ids = [i.cells[1].content for i in table.rows or []]
        for checkbox, id in zip(checkboxes, ids):
            if isinstance(checkbox, ft.Checkbox):
                checkbox.value = True if e.data == "true" else False
            if isinstance(id, ft.Text):
                selected[id.value or ""] = True if e.data == "true" else False

        table.update()

    def search(_):
        text_fields = [i for i in search_area.controls[:6]]
        params = {}
        for i in text_fields:
            if isinstance(i, ft.TextField):
                params[i.label] = i.value if i.value is not None else ""

        table.rows = build_table(
            params=params, set_selected=selected, selected=selected
        ).rows
        table.update()

    def check_page(e):
        """Redirect to another check page"""
        import src.page.check_page.check_page as check_page

        nonlocal content_area
        content_area.controls = [check_page.page_content(selected=selected)]
        content_area.update()

    search_area = ft.Row(
        spacing=12,
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[
            ft.TextField(label="id", width=100),
            ft.TextField(label="from_year", width=100),
            ft.TextField(label="to_year", width=100),
            ft.TextField(label="form", width=100),
            ft.TextField(label="subject", width=100),
            ft.TextField(label="notes", width=100),
            ft.IconButton(icon=ft.Icons.SEARCH, on_click=search),
            ft.Checkbox(label="Select all", on_change=select_all),
            ft.ElevatedButton(text="To check =>", on_click=check_page),
        ],
    )

    content_area.controls.append(search_area)
    content_area.controls.append(table)
    return content_area


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Database"))
