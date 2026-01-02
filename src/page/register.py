import os
import shutil
import sqlite3 as sql

import docx
import flet as ft

from main import main_page
from src.config import config


def page_content():
    content_area = ft.Column(
        controls=[ft.Text("Register past papers into database", size=24)]
    )

    def pick_file_result(e: ft.FilePickerResultEvent):
        files = (
            list(map(lambda f: (f.name.split("_"), f.path), e.files)) if e.files else []
        )
        if files == []:
            return

        db_path = config.get("db_path")
        if not db_path:
            raise Exception("Broken config")
        con = sql.connect(db_path)
        cur = con.cursor()

        for i in files:
            file = i[0]
            path = i[1]

            if not file[0].isdigit():
                continue
            if file[1] not in (config.get("forms") or []):
                continue
            if file[2] not in (config.get("subjects") or []):
                continue

            if os.path.splitext(path)[1].lower() not in [".doc", ".docx", ".pdf"]:
                continue

            if (
                len(
                    cur.execute(
                        "SELECT id FROM papers WHERE year = ? AND form = ? AND subject = ?;",
                        file,
                    ).fetchall()
                )
                > 0
            ):
                continue

            content: str | None = None
            if os.path.splitext(path)[1].lower() in [".doc", ".docx"]:
                doc = docx.Document(path)
                content = str([i for i in doc.paragraphs])
                del doc
            if os.path.splitext(path)[1].lower() == ".pdf":
                pass  # pass to ocr to do preprocess
            if content is None:
                continue

            paper_path = config.get("paper_path")
            if paper_path is None:
                raise Exception("Broken config")
            try:
                shutil.copy2(path, paper_path + os.path.basename(path))
            except BaseException as err:
                raise err
            
            query = "INSERT INTO papers (year, form, subject, content, path) VALUES (?, ?, ?, ?, ?);"
            try:
                cur.execute(query, (file + [content] + [paper_path + os.path.basename(path)]))
            except BaseException as err:
                raise err
            
        con.close()

    file_picker = ft.FilePicker(on_result=pick_file_result)
    btn = ft.ElevatedButton(
        text="select folder",
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
    )
    log_text = ft.Text("")
    log = ft.Column(controls=[log_text], scroll=ft.ScrollMode.ADAPTIVE)

    if main_page is not None:
        main_page.overlay.append(file_picker)
        content_area.controls.append(btn)
        content_area.controls.append(log)
    else:
        raise Exception("No main page")

    return content_area


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Register"))
