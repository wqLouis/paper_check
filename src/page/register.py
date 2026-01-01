import sqlite3 as sql

import flet as ft

from main import main_page


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
        for i in files:
            pass

    file_picker = ft.FilePicker(on_result=pick_file_result)
    btn = ft.ElevatedButton(
        text="select folder",
        on_click=lambda _: file_picker.pick_files(allow_multiple=True),
    )

    if main_page is not None:
        main_page.overlay.append(file_picker)
        content_area.controls.append(btn)
    else:
        raise Exception("No main page")

    return content_area


def menu_btn():
    return ft.MenuItemButton(content=ft.Text("Register"))
