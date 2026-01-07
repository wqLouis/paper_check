import pathlib

import flet as ft

import src.config as config


def page_content():
    content_area = ft.Column(spacing=24)
    config_textfield = []

    for key, val in config.config.items():
        if isinstance(val, dict):
            config_textfield.append(ft.Text(value=key))
            config_textfield += [
                ft.TextField(label=str(k), value=v) for k, v in val.items()
            ]

    save_btn = ft.IconButton(icon=ft.Icons.SAVE)
    reset_btn = ft.ElevatedButton(text="Reset")

    def write_config(_):
        ok = True
        for i in config_textfield:
            if (
                str(i.label).split("_")[-1] == "path"
                and not pathlib.Path(str(i.value)).exists
            ):
                i.error_text = "path not exist"
                ok = False
        if ok:
            for i in config_textfield:
                config.config[i.label] = i.value
            config.commit()
        content_area.update()

    def reset_config(_):
        for i in zip(config_textfield, config.fallback_config.values()):
            i[0].value = i[1]
            i[0].error_text = ""
        content_area.update()

    save_btn.on_click = write_config
    reset_btn.on_click = reset_config

    content_area.controls = (
        [
            ft.Text("Settings", size=24),
            ft.TextField(
                label="config path",
                value=f"{config.config_path.resolve()}",
                read_only=True,
            ),
        ]
        + config_textfield
        + [ft.Row([save_btn, reset_btn])]
    )

    return content_area


def menu_btn():
    return ft.IconButton(icon=ft.Icons.SETTINGS)
