import datetime
import pathlib
import sqlite3 as sql
from difflib import SequenceMatcher

import fitz as pdf
import flet as ft
import numpy as np

from src.config import config
from src.page.register import ocr_to_str


def find_similarity(ori_paper: str, check_paper: str, path: pathlib.Path):
    ori = [i for i in ori_paper.split("\n") if i.strip()]
    check = [i for i in check_paper.split("\n") if i.strip()]

    score: list[tuple[str, list[tuple[float, str]]]] = []
    for i in ori:
        line_score: list[tuple[float, str]] = []
        for j in check:
            line_score.append((SequenceMatcher(None, i, j).ratio(), j))
        score.append((i, sorted(line_score, key=lambda x: x[0], reverse=True)))
    return score, path


def load_papers(ids: list[str]):
    result: list[str] = []
    db_path = (config.get("general") or {}).get("db_path")
    if not db_path:
        raise Exception("Broken config")
    with sql.connect(db_path) as con:
        cur = con.cursor()
        paths = [
            pathlib.Path(i)
            for i in [
                cur.execute("SELECT content FROM papers WHERE id = ?", i).fetchone()[0]
                for i in ids
            ]
        ]
        for i in paths:
            if not i.exists():
                raise Exception(f"Missing file: {i}")
            with open(i, "r") as f:
                result.append(f.read())
    return list(zip(result, paths))


def logging_text(text: ft.Text):
    def log(log_str):
        if text.value is None:
            text.value = ""
        text.value += f"{log_str}\n"
        text.update()

    return log


def page_content(selected: dict[str, bool] = {}):
    register_to_db: bool = bool(False)

    def checkbox_register_to_db(e):
        nonlocal register_to_db
        register_to_db = True if e.data == "true" else False

    status_text = ft.Text(f"{selected}\n")

    content_area = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
    content_area.controls.append(
        ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.UPLOAD_FILE,
                    content=ft.Text("Upload file to check"),
                    on_click=lambda _: file_picker.pick_files(
                        allow_multiple=False, allowed_extensions=["pdf"]
                    ),
                ),
                ft.Checkbox(
                    label="Also register into db?", on_change=checkbox_register_to_db
                ),
            ]
        )
    )
    content_area.controls.append(status_text)

    log = logging_text(status_text)

    def check_file(e: ft.FilePickerResultEvent):
        status_text.value = "" if status_text.value is None else status_text.value
        log("Started: DO NOT SWITCH TO OTHER PAGE!")
        if e.files is None:
            log("No file selected")
            return
        path = pathlib.Path((e.files or [])[0].path)
        with pdf.open(path) as f:
            imgs = [f.load_page(i).get_pixmap() for i in range(len(f))]
            imgs = [
                np.frombuffer(i.samples, dtype=np.uint8).reshape(i.height, i.width, i.n)
                for i in imgs
            ]

        if not imgs:
            return

        log("OCR: Starting")
        ocred_str = ocr_to_str(imgs=imgs)
        log("OCR: Finished")

        if register_to_db:
            pass

        selected_papers: list[str] = []

        for key, val in selected.items():
            if val:
                selected_papers.append(key)
        papers = load_papers(selected_papers)
        del selected_papers

        log("Checking: Starting")
        result = [find_similarity(ocred_str, *i) for i in papers]
        log("Checking: Finished")
        reports_path = (config.get("general") or {}).get("reports_path")
        if not reports_path:
            raise Exception("Broken config")
        reports_path = pathlib.Path(reports_path) / pathlib.Path(
            str(datetime.datetime.now()) + ".md"
        )
        log("Formating & Saving report...")
        with open(reports_path, "w+") as f:
            f.write(
                f"Report generated in {datetime.datetime.now()}\n{path.stem} checked against: \n{'\n'.join([i[1].stem for i in papers])}\n\n"
            )

            result_dict: dict[str, list] = {}

            for i in result:
                for j in i[0]:
                    if result_dict.get(j[0]) is None:
                        result_dict[j[0]] = []
                    result_dict[j[0]] += [
                        (unpack[0], unpack[1], i[1].stem) for unpack in j[1]
                    ]

            for key, val in result_dict.items():
                sorted_val = sorted(val, key=lambda x: x[0], reverse=True)[:5]
                f.write(f"{key}:\n")
                for idx, i in enumerate(sorted_val):
                    f.write(
                        f"{idx + 1}: {'{:.2f}'.format(i[0])} : {str(i[1])} : from {i[2]}\n"
                    )
                f.write("\n")
        log("Saved, you can quit this page...")

    file_picker = ft.FilePicker(on_result=check_file)
    content_area.controls.append(file_picker)

    return content_area
