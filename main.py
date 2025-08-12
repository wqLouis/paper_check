import flet as ft
import os
from src.core import preference

def main(page: ft.Page) -> None:
    page.title = "Paper Check"
    page.theme = ft.Theme(font_family = "Cascadia Code")

    content_area: ft.Column = ft.Column()

    def examine_page(event: ft.ControlEvent) -> None:
        pass

    def analysis_page(event: ft.ControlEvent) -> None:
        pass

    def register_page(event: ft.ControlEvent) -> None:
        pass

    def settings_page(event: ft.ControlEvent) -> None:
        content_area.controls.clear()

        model_path: ft.TextField = ft.TextField(label = "Embedding model path", value = preference.model_path)
        pfile_path_target: ft.TextField = ft.TextField(label = "Past paper location", value = preference.pfile_target_path)
        db_path: ft.TextField = ft.TextField(label = "Past paper database path", value = preference.db_path)

        def save_preference(event: ft.ControlEvent) -> None:
            model_path.error_text = ""
            pfile_path_target.error_text = ""

            status_text.value = "Saved!"

            # Check value is valid
            if os.path.isdir(model_path.value if model_path.value != None else ""):
                preference.model_path = model_path.value if model_path.value != None else ""
            else:
                model_path.error_text = "Invalid file path"
                status_text.value = "Error on save"

            if os.path.isdir(pfile_path_target.value if pfile_path_target.value != None else ""):
                preference.pfile_target_path = pfile_path_target.value if pfile_path_target.value != None else ""
            else:
                pfile_path_target.error_text = "Invalid directory"
                status_text.value = "Error on save"

            if os.path.isdir(db_path.value if db_path.value != None else ""):
                preference.db_path = db_path.value if db_path.value != None else ""
            else:
                db_path.error_text = "Invalid directory"
                status_text.value = "Error on save"
            
            page.update()

        save_btn: ft.ElevatedButton = ft.ElevatedButton(text = "Save", icon = ft.Icons.SAVE, on_click = save_preference)
        status_text: ft.Text = ft.Text(value = "", size = 16)

        content_area.controls.append(model_path)
        content_area.controls.append(pfile_path_target)
        content_area.controls.append(db_path)
        content_area.controls.append(ft.Row(controls = [save_btn, status_text]))

        page.update()

    examine_btn: ft.MenuItemButton = ft.MenuItemButton(content = ft.Text("Examine"), on_click = examine_page)
    analysis_btn: ft.MenuItemButton = ft.MenuItemButton(content = ft.Text("Analysis"), on_click = analysis_page)
    register_btn: ft.MenuItemButton = ft.MenuItemButton(content = ft.Text("Register Paper"), on_click = register_page)
    settings_btn: ft.IconButton = ft.IconButton(content = ft.Icon(name = ft.Icons.SETTINGS), on_click = settings_page)

    menu_bar: ft.MenuBar = ft.MenuBar(
        controls = [
        examine_btn,
        analysis_btn,
        register_btn],
        expand = True
    )

    page.add(ft.Container(content = ft.Row([ft.Text("Paper Check"),menu_bar, settings_btn])), content_area)
    page.update()

ft.app(main)
