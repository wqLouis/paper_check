import flet as ft
import os
import glob
import src.core as core
import src.register as register
import src.main_utils as main_utils
from src.core import unwrap
from src.core import unwrap_str
from src.core import preference
from src.core import pattributes


def main(page: ft.Page) -> None:
    page.title = "Paper Check"
    page.theme = ft.Theme(font_family="Cascadia Code")

    content_area: ft.Column = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, width=page.width)

    def examine_page(event: ft.ControlEvent) -> None:
        content_area.controls.clear()
        page.update()

    def analysis_page(event: ft.ControlEvent) -> None:
        pass

    def register_page(event: ft.ControlEvent) -> None:
        content_area.controls.clear()

        register_input_module: ft.Column = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER
        )

        allowed_extensions: list[str] = [".pdf", ".docx"]

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
                    unwrap_str(dir_path) if unwrap_str(dir_path) != ""
                    else file_path[0].path if file_path is not None else ""
                )
                register_input_module.update()

                return
            else:
                error_message.value = "Error on opening file:" + (
                    unwrap_str(dir_path) if unwrap_str(dir_path) != ""
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

        input_row: list[ft.TextField] = [
            ft.TextField(label="Year"),
            ft.TextField(label="Subject"),
            ft.TextField(label="Type"),
        ]

        def manual_register(event: ft.ControlEvent) -> None:
            register_input_module.controls.clear()
            selected_path.value = ""

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
                path: str = unwrap_str(selected_path.value)

                unwrap(
                    register.auto_register_with_folder(
                        path=path, log=log_text, update_control=content_area
                    )
                )
            elif mode_select.value == False:
                path: str = unwrap_str(selected_path.value)

                result: str | Exception = register.register_papers(
                    pfile_path=path,
                    pyear=int(unwrap_str(input_row[0].value)),
                    psbj=unwrap_str(input_row[1].value),
                    ptype=unwrap_str(input_row[2].value),
                )

                log_text.value = unwrap_str(log_text.value)
                log_text.value += f">{path}"

                if str(result) == "":
                    return

                alert_dia = ft.AlertDialog(
                    modal=False,
                    title=ft.Text(value="Error"),
                    content=ft.Text(str(result)),
                    actions=[
                        ft.TextButton(
                            text="Ok", on_click=lambda _: page.close(alert_dia))
                    ],
                )
                page.open(alert_dia)

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

        register_input_module.controls.append(
            ft.Container(
                content=selected_path, width=page.width, alignment=ft.alignment.center
            )
        )
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
            label="Automatic register by file name\nWith format '[Year]_[Subject]_[Type].pdf/.docx'",
            on_change=manual_register,
            value=True,
        )
        log_text: ft.Text = ft.Text(value="Log:\n", size=16)

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
        content_area.controls.append(
            ft.Container(
                log_text,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                margin=32,
                padding=32,
                border_radius=32,
                width=page.width,
            )
        )

        page.update()

    def settings_page(event: ft.ControlEvent) -> None:
        content_area.controls.clear()

        preference_class: preference = preference()
        input_module: list[ft.TextField] = preference_class.construct_textfield()
        content_area.controls += input_module

        def save_preference(event: ft.ControlEvent) -> None:
            status_text.value = "Saved!"
            for i in input_module:
                if preference_class.check_dir_valid(text_field=i, page=page) == False:
                    status_text.value = "Error on save"

            if unwrap_str(status_text.value) == "Saved!":
                preference_class.save_on_disk()

            page.open(ft.AlertDialog(modal=False, title=status_text))

        save_btn: ft.IconButton = ft.IconButton(
            icon=ft.Icons.SAVE,
            icon_size=32,
            padding=8,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            on_click=save_preference,
        )
        status_text: ft.Text = ft.Text(value="", size=16)

        content_area.controls.append(
            ft.Container(
                content=save_btn,
                width=page.width,
                alignment=ft.alignment.center_right,
                margin=ft.margin.symmetric(horizontal=32),
            )
        )

        page.update()

    def preprocess_page(event: ft.ControlEvent) -> None:
        import src.preprocess as preprocess

        def send_to_preprocess(event: ft.ControlEvent) -> None:
            preprocess_btn.disabled = True
            page.update()
            result:tuple[list[list[str]], list[str]] = preprocess.send_to_preprocess(datatable=past_paper_table, progress_bar=ocr_progress_bar, page=page, btn=preprocess_btn) or ([], [])
            for (idx, i) in enumerate(result[0]):
                unwrap(main_utils.examine(i, int(result[1][idx])))
            ocr_progress_bar.value = 0
            preprocess_btn.disabled = False

        def search(event: ft.ControlEvent | None) -> None:
            query_dict: dict = {}
            for i in pattributes.attribute_dict:
                query_dict[i] = None
                if i == "year":
                    query_dict[i] = []

            for i in input_module.controls:
                if isinstance(i, ft.Dropdown):
                    query_dict[i.label] = i.value
                    continue
                if isinstance(i, ft.TextField):
                    if i.value != "":
                        if (unwrap_str(i.value)).isdigit():
                            if i.label == "From year":
                                query_dict["year"].append(
                                    int(unwrap_str(i.value)))
                            if i.label == "To year":
                                query_dict["year"].append(
                                    int(unwrap_str(i.value)))
                        else:
                            i.error_text = "Not digit"

            if past_paper_table.rows is not None:
                past_paper_table.rows.clear()
                if len(query_dict["year"]) > 1:
                    for i in range(query_dict["year"][0], query_dict["year"][1] + 1):
                        past_paper_table.rows += preprocess.get_data_from_psource(pyear=i, psbj=query_dict["sbjs"], ptype=query_dict["types"], page_num=int(
                            page_num.value if page_num.value is not None else "0"), items_per_page=(int(item_per_page.value) if item_per_page.value is not None else 10))
                else:
                    past_paper_table.rows += preprocess.get_data_from_psource(pyear=None, psbj=query_dict["sbjs"], ptype=query_dict["types"], page_num=int(
                        page_num.value if page_num.value is not None else "0"), items_per_page=(int(item_per_page.value) if item_per_page.value is not None else 10))
            content_area.update()

        def add_page_num(event: ft.ControlEvent) -> None:
            if isinstance(page_num.value, str):
                page_num.value = str(int(page_num.value) + 1)
            search(None)
            content_area.update()

        def minus_page_num(event: ft.ControlEvent) -> None:
            if isinstance(page_num.value, str) and int(page_num.value) > 0:
                page_num.value = str(int(page_num.value) - 1)
            search(None)
            content_area.update()

        content_area.controls.clear()

        past_paper_table: ft.DataTable = ft.DataTable(columns=[
            ft.DataColumn(label=ft.Text(value="Select")),
            ft.DataColumn(label=ft.Text(value="Year")),
            ft.DataColumn(label=ft.Text(value="Subject")),
            ft.DataColumn(label=ft.Text(value="Type")),
            ft.DataColumn(label=ft.Text(value="Path"))
        ])

        serach_btn: ft.IconButton = ft.IconButton(
            icon=ft.Icons.SEARCH, col={"sm": 1}, on_click=search)

        input_module: ft.ResponsiveRow = preprocess.construct_select_options()
        input_module.controls.append(serach_btn)
        input_module.alignment = ft.MainAxisAlignment.CENTER
        input_module.width = page.width

        item_per_page: ft.Dropdown = ft.Dropdown(label="Item per page", options=[ft.DropdownOption(
            text="10"), ft.DropdownOption(text="20"), ft.DropdownOption(text="30")], col={"sm":3, "md":5}, width=300)
        page_num: ft.Text = ft.Text(value="0", col={"sm":1}, text_align=ft.TextAlign.CENTER, expand=True)
        preprocess_btn: ft.ElevatedButton = ft.ElevatedButton(text="Preprocess", icon=ft.Icons.ARROW_RIGHT, col={"sm":3}, on_click=send_to_preprocess)
        bottom_input_module: ft.ResponsiveRow = ft.ResponsiveRow(
            controls=[
                item_per_page,
                ft.IconButton(icon=ft.Icons.ARROW_LEFT,
                              on_click=minus_page_num, col={"sm":1}),
                ft.IconButton(icon=ft.Icons.ARROW_RIGHT,
                              on_click=add_page_num, col={"sm":1}),
                page_num,
                preprocess_btn
            ]
        )
        ocr_progress_bar: ft.ProgressBar = ft.ProgressBar(value=0)

        past_paper_table.rows = preprocess.get_data_from_psource(pyear=None, psbj=None, ptype=None, page_num=int(
            page_num.value if page_num.value is not None else "0"), items_per_page=(int(item_per_page.value) if item_per_page.value is not None else 10))
        past_paper_table.width = page.width

        content_area.controls.append(input_module)
        content_area.controls.append(ft.Divider())
        content_area.controls.append(ft.Container(
        past_paper_table, alignment=ft.alignment.center, width=page.width))
        content_area.controls.append(bottom_input_module)
        content_area.controls.append(ocr_progress_bar)
        content_area.update()

    def theme_mode_switch(event: ft.ControlEvent) -> None:

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
    preprocess_btn: ft.MenuItemButton = ft.MenuItemButton(
        content=ft.Text("Preprocess"), on_click=preprocess_page
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
        controls=[examine_btn, analysis_btn,
                  register_btn, preprocess_btn], expand=True
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
