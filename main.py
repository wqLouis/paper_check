import flet as ft

import src.bar as bar
import src.page.db as db

main_page: ft.Page | None = None


def main(page: ft.Page):
    # startup checking
    page.title = "Paper Check"
    page.scroll = ft.ScrollMode.ADAPTIVE
    title_bar = bar.Bar(page=page)
    page.controls = [title_bar.bar]
    page.update()


if __name__ == "__main__":
    db.init_db()
    ft.app(main)
