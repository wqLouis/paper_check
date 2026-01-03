import flet as ft

import src.bar as bar
import src.page.db as db

main_page: ft.Page | None = None


def main(page: ft.Page):
    page.title = "Paper Check"
    page.scroll = ft.ScrollMode.ADAPTIVE
    title_bar = bar.Bar(page=page)
    page.controls = [title_bar.bar]
    page.update()


def setup():
    db.check_db()


if __name__ == "__main__":
    ft.app(main)
