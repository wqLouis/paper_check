import os
import shutil
import sqlite3 as sql

import fitz as pdf
import flet as ft
import numpy as np

from src.config import config


def ocr_to_str(imgs: list[np.ndarray]) -> str:
    from paddleocr import PPStructureV3  # avoid too long loading time on start

    ocr = PPStructureV3()
    md = []

    for i in imgs:
        page = ocr.predict(i)
        for j in page:
            md.append(j.markdown)

    md = ocr.concatenate_markdown_pages(md)

    return str(md)


def page_content():
    content_area = ft.Column(
        controls=[ft.Text("Register past papers into database", size=24)]
    )

    def pick_file_result(e: ft.FilePickerResultEvent):
        files = (
            list(
                map(lambda f: (os.path.splitext(f.name)[0].split("_"), f.path), e.files)
            )
            if e.files
            else []
        )
        print(files)
        if files == []:
            return

        db_path = (config.get("general") or {}).get("db_path")
        if not db_path:
            raise Exception("Broken config")
        con = sql.connect(db_path)
        cur = con.cursor()

        for i in files:
            file = i[0]
            path = i[1]

            if not file[0].isdigit():
                continue
            if file[1] not in ((config.get("general") or {}).get("forms") or []):
                continue
            if file[2] not in ((config.get("general") or {}).get("subjects") or []):
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
                continue  # check if repeated

            content: str | None = None
            if os.path.splitext(path)[1].lower() in [".doc", ".docx"]:
                print("currently not support docx or doc\nFuck you Microsoft :(")
            if os.path.splitext(path)[1].lower() == ".pdf":
                doc = pdf.open(path)
                img = [doc.load_page(i).get_pixmap() for i in range(len(doc))]
                img = [
                    np.frombuffer(i.samples, dtype=np.uint8).reshape(
                        i.height, i.width, i.n
                    )
                    for i in img
                ]
                doc.close()
                del doc
                content = ocr_to_str(imgs=img)
                print(content)

            if content is None or content == "":
                continue

            paper_path = (config.get("general") or {}).get("paper_path")
            if paper_path is None:
                raise Exception("Broken config")
            try:
                shutil.copy2(path, paper_path + os.path.basename(path))
            except BaseException as err:
                raise err

            query = "INSERT INTO papers (year, form, subject, content, path) VALUES (?, ?, ?, ?, ?);"
            try:
                cur.execute(
                    query, (file + [content] + [paper_path + os.path.basename(path)])
                )
            except BaseException as err:
                raise err

        con.commit()
        con.close()

    file_picker = ft.FilePicker(on_result=pick_file_result)
    btn = ft.ElevatedButton(
        text="select folder",
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
    )
    log_text = ft.Text("")
    log = ft.Column(controls=[log_text], scroll=ft.ScrollMode.ADAPTIVE)

    content_area.controls.append(file_picker)
    content_area.controls.append(btn)
    content_area.controls.append(log)

    return content_area


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Register"))
