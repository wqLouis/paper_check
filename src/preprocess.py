import flet as ft
import sqlite3 as sql
import os
import json
from src.core import preference
from src.core import pattributes
import src.ocr as ocr

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

def send_to_ocr(datatable: ft.DataTable, progress_bar: ft.ProgressBar, page: ft.Page, btn: ft.ElevatedButton) -> None:
    
    selected_papers: dict ={
        "year" : [],
        "sbj" : [],
        "type" : [],
        "path" : []
    }
    
    if datatable.rows is not None:
        for i in datatable.rows:
            selected: bool = False
            for (j, cell) in enumerate(i.cells):
                selected = True if j == 0 and cell.content.value == True else selected # type: ignore
                if selected:
                    if j == 1:
                        selected_papers["year"].append(cell.content.value) # type: ignore
                    elif j == 2:
                        selected_papers["sbj"].append(cell.content.value) # type: ignore
                    elif j == 3:
                        selected_papers["type"].append(cell.content.value) # type: ignore
                    elif j == 4:
                        selected_papers["path"].append(cell.content.spans[0].url) # type: ignore
    
    for (index, i) in enumerate(selected_papers["path"]):
        if os.path.splitext(os.path.basename(i))[1] == ".pdf":
            progress_bar.value = 0
            result_str: str = "\n".join(ocr.pdf_ocr(i, page_progress_bar=progress_bar, page=page, btn=btn))
            
            file_name: str = f"/{os.path.splitext(os.path.basename(i))[0]}.json"
            
            with open(f"{preference.setting_dict["temp_path"]}{file_name}", mode="w") as f:
                json.dump(result_str, f, indent=4)