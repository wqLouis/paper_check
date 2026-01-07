import pathlib
import sqlite3 as sql
from difflib import SequenceMatcher

import fitz as pdf
import flet as ft
import numpy as np

from src.config import config
from src.page.register import ocr_to_str


def find_similarity(ori_paper: str, check_paper: str, path: pathlib.Path):
    ori = ori_paper.split("\n")
    check = check_paper.split("\n")

    line_score: list[float] = []
    score: list[list[float]] = []
    for i in ori:
        for j in check:
            line_score.append(SequenceMatcher(None, i, j).ratio())
        score.append(line_score.copy())
        line_score.clear()
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


def page_content(selected: dict[str, bool] = {}):
    register_to_db: bool = bool(False)

    def checkbox_register_to_db(e):
        nonlocal register_to_db
        register_to_db = True if e.data == "true" else False

    content_area = ft.Column()
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

    def check_file(e: ft.FilePickerResultEvent):
        path = pathlib.Path((e.files or [])[0].path)
        with pdf.open(path) as f:
            imgs = [f.load_page(i).get_pixmap() for i in range(len(f))]
            imgs = [
                np.frombuffer(i.samples, dtype=np.uint8).reshape(i.height, i.width, i.n)
                for i in imgs
            ]

        if not imgs:
            return

        print("ocr start")
        ocred_str = ocr_to_str(imgs=imgs)
        print("ocr completed")

        if register_to_db:
            pass

        selected_papers: list[str] = []

        for key, val in selected.items():
            if val:
                selected_papers.append(key)
        papers = load_papers(selected_papers)
        del selected_papers

        result = [find_similarity(ocred_str, *i) for i in papers]
        print(result)

    file_picker = ft.FilePicker(on_result=check_file)
    content_area.controls.append(file_picker)

    return content_area
