import flet as ft

def main(page: ft.Page) -> None:
    page.title = "Paper Check"

    def examine_page(event: ft.ControlEvent) -> None:
        pass

    def analysis_page(event: ft.ControlEvent) -> None:
        pass

    def register_page(event: ft.ControlEvent) -> None:
        pass

    examine_btn: ft.MenuItemButton = ft.MenuItemButton(content = ft.Text("Examine"), on_click = examine_page) # type: ignore
    analysis_btn: ft.MenuItemButton = ft.MenuItemButton(content = ft.Text("Analysis"), on_click = analysis_page)
    register_btn: ft.MenuItemButton = ft.MenuItemButton(content = ft.Text("Register Paper"), on_click = register_page)

    menu_bar: ft.MenuBar = ft.MenuBar(
        controls = [
        examine_btn,
        analysis_btn,
        register_btn],
        expand = True
    )
    
    page.add(ft.Container(content = ft.Row([ft.Text("Paper Check"),menu_bar])))
    page.update()



ft.app(main)
