import flet as ft
import sqlite3 as sql
from src.core import preference

def get_data_from_psource(pyear: int | None, psbj: str | None, ptype: str | None) -> list[ft.DataRow]:
    
    con: sql.Connection = sql.connect(preference.db_path)
    query: str = """
    select * from qsource
    where   (pyear = ? or ? is null) and
            (psbj = ? or ? is null) and
            (ptype = ? or ? is null)
    """

    cur: sql.Cursor = con.cursor()
    db_data = cur.execute(query, (pyear, pyear, psbj, psbj, ptype, ptype)).fetchall()
    
    return [ft.DataRow([])]