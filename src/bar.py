import glob
import importlib
import os

import flet as ft

import src.config as config


class Bar:
    page: ft.Page
    bar: ft.Container = ft.Container()

    def update_page(self, func):
        def wrap(e):
            try:
                self.page.controls = [self.bar, func()]
                self.page.update()
            except BaseException as E:
                raise E

        return wrap

    def __init__(self, page: ft.Page) -> None:
        self.page = page

        pages = [
            "src.page." + os.path.splitext(os.path.basename(i))[0]
            for i in glob.glob(str(config.get("page_path")))
        ]
        modules = [importlib.import_module(i) for i in pages]
        menu_btns: list[ft.MenuItemButton] = [
            i() for i in [getattr(i, "menu_btn") for i in modules]
        ]
        page_func = [
            self.update_page(i) for i in [getattr(i, "page_content") for i in modules]
        ]

        for i in zip(menu_btns, page_func):
            i[0].on_click = i[1]

        self.bar.content = ft.Row(
            controls=[ft.Text("Paper Check"), ft.MenuBar(controls=menu_btns)]
        )
