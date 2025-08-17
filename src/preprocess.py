import flet as ft
import sqlite3 as sql
import os
from src.core import preference
from src.core import pattributes

def get_data_from_psource(pyear: int | None, psbj: str | None, ptype: str | None, page_num: int, items_per_page: int) -> list[ft.DataRow]:

    con: sql.Connection = sql.connect("D:\\vsproject\\paper_check\\db\\past_papers.db")
    query: str = """
    select * from psource
    where   (pyear = ? or ? is null) and
            (psbj = ? or ? is null) and
            (ptype = ? or ? is null)
    limit ? offset ?
    """

    cur: sql.Cursor = con.cursor()
    db_data = cur.execute(query, (pyear, pyear, psbj, psbj, ptype, ptype, items_per_page, page_num*items_per_page)).fetchall()

    data_rows: list[ft.DataRow] = []

    for i in db_data:
        data_rows.append(
            ft.DataRow(
                [
                    ft.DataCell(content=ft.Checkbox()),
                    ft.DataCell(content=ft.Text(value=str(i[2]))),
                    ft.DataCell(content=ft.Text(value=str(i[3]))),
                    ft.DataCell(content=ft.Text(value=str(i[4]))),
                    ft.DataCell(content=ft.Text(spans=[ft.TextSpan(text="CLICK TO OPEN FILE", url=os.path.abspath(str(i[1])))]))
                ]
            )
        )
    
    return data_rows

def construct_select_options() -> ft.ResponsiveRow:
    option_row: ft.ResponsiveRow = ft.ResponsiveRow()
    
    for i in pattributes.attribute_dict:
        if pattributes.attribute_dict[i] == "intFromTo":
            option_row.controls.append(
                ft.TextField(label=f"From {i}", col={"md": 2, "lg": 2})
            )
            option_row.controls.append(
                ft.TextField(label=f"To {i}", col={"md": 2, "lg": 2})
            )
        if pattributes.attribute_dict[i] == "set(str)":
            dropdown: ft.Dropdown = ft.Dropdown(label=i, options=[], col={"md": 2, "lg": 2})

            if dropdown.options is not None:
                for j in pattributes.subattribute_dict[i]:
                    dropdown.options.append(
                        ft.DropdownOption(
                            text=str(j)
                        )
                    )
            option_row.controls.append(
                dropdown
            )
    return option_row