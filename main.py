import flet as ft
import os
import glob
import src.core as core
import src.register as register
from src.core import unwrap
from src.core import preference


def main(page: ft.Page) -> None:
    page.title = "Paper Check"
    page.theme = ft.Theme(font_family="Cascadia Code")

    content_area: ft.Column = ft.Column(alignment=ft.MainAxisAlignment.CENTER)

    def examine_page(event: ft.ControlEvent) -> None:
        pass

    def analysis_page(event: ft.ControlEvent) -> None:
        pass

    def register_page(event: ft.ControlEvent) -> None:
        content_area.controls.clear()

        register_input_module: ft.Column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER
        )

        allowed_extensions: list[str] = [".pdf", ".doc", ".docx"]

        def on_dialog_result(event: ft.FilePickerResultEvent) -> None:
            dir_path = event.path
            file_path = event.files

            error_message = ft.Text(value="")
            if (
                dir_path is not None
                and os.path.isdir(dir_path)
                or file_path is not None
                and os.path.isfile(file_path[0].path)
            ):
                selected_path.value = (
                    dir_path
                    if dir_path is not None
                    else file_path[0].path if file_path is not None else ""
                )
                register_input_module.update()
                if not (
                    file_path is not None
                    and os.path.splitext(file_path[0].path)[1] not in allowed_extensions
                ):
                    return
            elif file_path is None and dir_path is None:
                return
            else:
                error_message.value = "Error on opening file:" + (
                    dir_path
                    if dir_path is not None
                    else file_path[0].path if file_path is not None else ""
                )

            selected_path.value = "Error"

            if (
                file_path is not None
                and os.path.splitext(file_path[0].path)[1] not in allowed_extensions
            ):
                error_message.value = f"Invalid file extension, only {str(allowed_extensions)}, but {os.path.splitext(file_path[0].path)[1]}"

            alert_dia = ft.AlertDialog(
                modal=False,
                title=ft.Text(value="Error on opening file"),
                content=error_message,
                actions=[
                    ft.TextButton(
                        text="Ok", on_click=lambda _: page.close(alert_dia))
                ],
            )
            page.open(alert_dia)

            register_input_module.update()

        def manual_register(event: ft.ControlEvent) -> None:
            register_input_module.controls.clear()
            selected_path.value = ""
            input_row: list[ft.Control] = [
                ft.TextField(label="Year"),
                ft.TextField(label="Subject"),
                ft.TextField(label="Type"),
            ]

            if event.data == "false":
                upload_files_btn: ft.ElevatedButton = ft.ElevatedButton(
                    text="Choose files...",
                    icon=ft.Icons.FILE_UPLOAD,
                    on_click=lambda _: file_picker.pick_files(),
                )

                register_input_module.controls.append(selected_path)
                register_input_module.controls.append(
                    ft.ResponsiveRow(controls=input_row)
                )
                register_input_module.controls.append(
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(
                                content=upload_files_btn,
                                col={"md": 4, "lg": 5},
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                padding=8,
                                border_radius=32,
                            ),
                            ft.Container(
                                content=submit_btn,
                                col={"md": 4, "lg": 5},
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                padding=8,
                                border_radius=32,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                )

            elif event.data == "true":
                register_input_module.controls.append(selected_path)
                register_input_module.controls.append(
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(
                                content=upload_dir_btn,
                                col={"md": 4, "lg": 5},
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                padding=8,
                                border_radius=32,
                            ),
                            ft.Container(
                                content=submit_btn,
                                col={"md": 4, "lg": 5},
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                padding=8,
                                border_radius=32,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                )

            register_input_module.update()

        def submit(event: ft.ControlEvent) -> None:
            if mode_select.value == True:
                path: str = (
                    selected_path.value
                    if selected_path.value is not None and selected_path is not "Error"
                    else ""
                )

                unwrap(register.auto_register_with_folder(path = path, log = ft.Text()))
            else:
                pass

        file_picker: ft.FilePicker = ft.FilePicker(on_result=on_dialog_result)
        file_picker.allowed_extensions = allowed_extensions
        file_picker.allow_multiple = False  # Unavaliable at this stage

        page.overlay.append(file_picker)

        upload_dir_btn: ft.ElevatedButton = ft.ElevatedButton(
            text="Choose directory...",
            icon=ft.Icons.FILE_UPLOAD,
            on_click=lambda _: file_picker.get_directory_path(),
        )
        submit_btn: ft.ElevatedButton = ft.ElevatedButton(
            text="Submit...", icon=ft.Icons.ARROW_FORWARD, on_click=submit
        )
        selected_path: ft.Text = ft.Text(value="", size=12)

        register_input_module.controls.append(selected_path)
        register_input_module.controls.append(
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=upload_dir_btn,
                        col={"md": 4, "lg": 5},
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        padding=8,
                        border_radius=32,
                    ),
                    ft.Container(
                        content=submit_btn,
                        col={"md": 4, "lg": 5},
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        padding=8,
                        border_radius=32,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )

        discription_text: ft.Text = ft.Text(
            value="Register past paper into database system.\n",
            size=24,
            text_align=ft.TextAlign.CENTER,
        )
        mode_select: ft.Switch = ft.Switch(
            label="Automatic register by file name\nWith format '[Year]_[Subject]_[Type].word/.pdf'",
            on_change=manual_register,
            value=True,
        )
        content_area.controls.append(
            ft.Container(discription_text, expand=True,
                         alignment=ft.alignment.center)
        )
        content_area.controls.append(
            ft.Container(
                mode_select,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border_radius=32,
                alignment=ft.alignment.center,
                padding=8,
                margin=ft.margin.symmetric(horizontal=32),
            )
        )
        content_area.controls.append(register_input_module)

        page.update()

    def settings_page(event: ft.ControlEvent) -> None:
        content_area.controls.clear()

        model_path: ft.TextField = ft.TextField(
            label="Embedding model path", value=preference.model_path
        )
        pfile_path_target: ft.TextField = ft.TextField(
            label="Past paper location", value=preference.pfile_target_path
        )
        db_path: ft.TextField = ft.TextField(
            label="Past paper database path", value=preference.db_path
        )

        def save_preference(event: ft.ControlEvent) -> None:
            model_path.error_text = ""
            pfile_path_target.error_text = ""

            status_text.value = "Saved!"

            # Check value is valid
            if os.path.isdir(model_path.value if model_path.value != None else ""):
                preference.model_path = (
                    model_path.value if model_path.value != None else ""
                )
            else:
                model_path.error_text = "Invalid file path"
                status_text.value = "Error on save"

            if os.path.isdir(
                pfile_path_target.value if pfile_path_target.value != None else ""
            ):
                preference.pfile_target_path = (
                    pfile_path_target.value if pfile_path_target.value != None else ""
                )
            else:
                pfile_path_target.error_text = "Invalid directory"
                status_text.value = "Error on save"

            if os.path.isdir(db_path.value if db_path.value != None else ""):
                preference.db_path = db_path.value if db_path.value != None else ""
            else:
                db_path.error_text = "Invalid directory"
                status_text.value = "Error on save"

            page.update()

        save_btn: ft.ElevatedButton = ft.ElevatedButton(
            text="Save", icon=ft.Icons.SAVE, on_click=save_preference
        )
        status_text: ft.Text = ft.Text(value="", size=16)

        content_area.controls.append(model_path)
        content_area.controls.append(pfile_path_target)
        content_area.controls.append(db_path)
        content_area.controls.append(ft.Row(controls=[save_btn, status_text]))

        page.update()

    def theme_mode_switch(event: ft.ControlEvent) -> None:
        current_theme_mode = ft.ThemeMode.SYSTEM

        if theme_mode_btn.icon == ft.Icons.LIGHT_MODE:
            theme_mode_btn.icon = ft.Icons.DARK_MODE
            page.theme_mode = ft.ThemeMode.DARK
            page.update()
            return

        if theme_mode_btn.icon == ft.Icons.DARK_MODE:
            theme_mode_btn.icon = ft.Icons.LIGHT_MODE
            page.theme_mode = ft.ThemeMode.LIGHT
            page.update()
            return

    examine_btn: ft.MenuItemButton = ft.MenuItemButton(
        content=ft.Text("Examine"), on_click=examine_page
    )
    analysis_btn: ft.MenuItemButton = ft.MenuItemButton(
        content=ft.Text("Analysis"), on_click=analysis_page
    )
    register_btn: ft.MenuItemButton = ft.MenuItemButton(
        content=ft.Text("Register Paper"), on_click=register_page
    )
    settings_btn: ft.IconButton = ft.IconButton(
        content=ft.Icon(name=ft.Icons.SETTINGS), on_click=settings_page
    )

    theme_mode_btn: ft.IconButton = ft.IconButton(
        icon=(
            ft.Icons.LIGHT_MODE
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.Icons.DARK_MODE
        ),
        on_click=theme_mode_switch,
    )

    menu_bar: ft.MenuBar = ft.MenuBar(
        controls=[examine_btn, analysis_btn, register_btn], expand=True
    )

    page.add(
        ft.Container(
            content=ft.Row(
                [ft.Text("Paper Check"), menu_bar,
                 settings_btn, theme_mode_btn]
            )
        ),
        content_area,
    )
    page.update()


ft.app(main)
