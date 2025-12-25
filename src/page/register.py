import flet as ft

import src.bar.bar as bar

main_page: ft.Page
is_on_page: bool = False


def register(e):
    if main_page.controls is None:
        raise Exception("Main page is none")

    global is_on_page
    if is_on_page:
        return
    else:
        is_on_page = True

    controls = []
    controls.append(ft.Text("Test"))
    content_area = ft.Column(controls=controls)
    main_page.controls = [bar.getbar()] + [content_area]
    main_page.update()


def menu_btn(page: ft.Page):
    global main_page
    main_page = page

    btn = ft.MenuItemButton(content=ft.Text("Register"), on_click=register)

    return btn
