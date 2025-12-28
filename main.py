import flet as ft

import src.bar as bar


def main(page: ft.Page):
    page.title = "Paper Check"
    title_bar = bar.Bar(page=page)
    page.controls = [title_bar.bar]
    page.update()


if __name__ == "__main__":
    ft.app(main)
