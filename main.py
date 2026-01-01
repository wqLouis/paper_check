import flet as ft

import src.bar as bar

main_page: ft.Page | None = None


def main(page: ft.Page):
    global main_page
    main_page = page
    page.title = "Paper Check"
    title_bar = bar.Bar(page=page)
    page.controls = [title_bar.bar]
    page.update()


def setup():
    pass


if __name__ == "__main__":
    ft.app(main)
