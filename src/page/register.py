import pathlib
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
        log_update("File uploaded!")

        files = (
            list(map(lambda f: (pathlib.Path(f.name).name.split("_"), f.path), e.files))
            if e.files
            else []
        )

        log_update(files)

        if files == []:
            return

        db_path = (config.get("general") or {}).get("db_path")
        if not db_path:
            raise Exception("Broken config")
        con = sql.connect(db_path)
        cur = con.cursor()

        for i in files:
            file = i[0]
            path = pathlib.Path(i[1])

            if not file[0].isdigit():
                continue
            if file[1] not in ((config.get("general") or {}).get("forms") or []):
                continue
            if file[2] not in ((config.get("general") or {}).get("subjects") or []):
                continue
            if len(file) < 4:
                file.append("N/A")

            if (
                len(
                    cur.execute(
                        "SELECT id FROM papers WHERE year = ? AND form = ? AND subject = ? AND notes = ?;",
                        file,
                    ).fetchall()
                )
                > 0
            ):
                log_update(f"Found repeated passing: {path}")
                continue  # check if repeated

            content: str | None = None
            if path.suffix.lower() in [".doc", ".docx"]:
                print("currently not support docx or doc\nFuck you Microsoft :(")
            if path.suffix.lower() == ".pdf":
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
                log_update(f"Started ocr on {path}")
                content = ocr_to_str(imgs=img)
                log_update("Ocr finished")

            if content is None or content == "":
                continue

            paper_path = (config.get("general") or {}).get("paper_path")
            if paper_path is None:
                raise Exception("Broken config")
            paper_path = pathlib.Path(paper_path)
            try:
                shutil.copy2(
                    path,
                    paper_path / path.name,
                )
            except BaseException as err:
                raise err

            query = "INSERT INTO papers (year, form, subject, notes, content, path) VALUES (?, ?, ?, ?, ?, ?);"
            try:
                markdown_path = (config.get("general") or {}).get("markdown_path")

                if markdown_path is None:
                    raise Exception("Broken config")

                markdown_path = pathlib.Path(markdown_path) / f"{path.stem}.md"

                with open(markdown_path, "w+") as f:
                    f.write(content)

                cur.execute(
                    query,
                    (file + [markdown_path] + [paper_path.resolve() / path.name]),
                )
            except BaseException as err:
                raise err

        con.commit()
        con.close()

    file_picker = ft.FilePicker(on_result=pick_file_result)
    btn = ft.ElevatedButton(
        text="select folder",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=True, allowed_extensions=["pdf", "doc", "docx"]
        ),
    )
    log_text = ft.Text("")

    def log_update(val):
        if not isinstance(val, str):
            try:
                val = str(val)
            except BaseException as e:
                val = repr(e)
        if log_text.value is None:
            log_text.value = ""
        log_text.value += val + "\n"
        log.update()

    log = ft.Column(controls=[log_text], scroll=ft.ScrollMode.ADAPTIVE)

    content_area.controls.append(file_picker)
    content_area.controls.append(btn)
    content_area.controls.append(log)

    return content_area


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Register"))
