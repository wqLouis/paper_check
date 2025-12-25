import flet as ft

bar: ft.Container


def init_bar(title_bar: ft.Container):
    global bar
    bar = title_bar


def getbar():
    return bar
