import glob
import importlib
import os

import flet as ft

import src.bar.bar as bar

config: dict = {"page_path": "./src/page/*.py"}


def title_bar(content: list[ft.MenuItemButton]):
    bar = ft.Container(
        content=ft.Row(
            [
                ft.Text("Paper Check"),
                ft.MenuBar(content, expand=True),
            ]
        )
    )

    return bar


def main(page: ft.Page):
    page.title = "Paper Check"

    if page.controls is None:
        raise Exception

    try:
        pages = [
            "src.page." + os.path.splitext(os.path.basename(i))[0]
            for i in glob.glob(str(config.get("page_path")))
        ]
        modules = [importlib.import_module(i) for i in pages]
        menu_btns: list[ft.MenuItemButton] = [
            i(page=page) for i in [getattr(i, "menu_btn") for i in modules]
        ]  # get menu btn from each page
    except BaseException as e:
        raise e

    bar.init_bar(title_bar=title_bar(menu_btns))
    page.controls.append(bar.getbar())
    page.update()


if __name__ == "__main__":
    ft.app(main)
