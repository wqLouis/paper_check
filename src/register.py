import os
import glob
import shutil
import sqlite3 as sql
import flet as ft
from core import init_db
from core import unwrap
from core import preference
from core import pattributes


class PastPaper:
    pfile_path: str
    pyear: int
    psbj: str
    ptype: str


def register_papers(pfile_path: str, pyear: int, psbj: str, ptype: str) -> Exception | None:

    """
    (Plan to refactor: replacing args into a list of PastPaper class)
    Register a past paper into database

    Args:
        pfile_path: Past paper file path
        pyear: The year of past paper
        psbj: Past paper subject (supports: ["MATH", "PHY", "CHEM", "BIO", "ICT"])
        ptype: Past paper type (supports: ["DSE", "ALV", "CE"])
    """

    if not os.path.exists(pfile_path):
        return FileNotFoundError(f"failed to find paper '{pfile_path}'")
    if not os.path.exists(preference.pfile_target_path):
        return FileNotFoundError(
            f"target directory not found '{preference.pfile_target_path}'"
        )
    if psbj not in pattributes.sbjs:
        return ValueError(
            f"has no type for psbj={psbj}\nwe have these sbjs {str(pattributes.sbjs)}"
        )
    if ptype not in pattributes.types:
        return ValueError(
            f"has no type for psbj={ptype}\nwe have these types {str(pattributes.types)}"
        )

    con: sql.Connection = unwrap(init_db())
    insert_query: str = """
    INSERT INTO psource (pfile_path, pyear, psbj, ptype)
    VALUES (?, ?, ?, ?)
    """
    cur: sql.Cursor = con.cursor()

    try:
        shutil.copyfile(pfile_path, preference.pfile_target_path)
    except Exception as e:
        return e

    cur.execute(
        insert_query,
        (
            preference.pfile_target_path + os.path.basename(pfile_path),
            pyear,
            psbj,
            ptype,
        ),
    )
    con.commit()
    return


def auto_register_with_folder(path: str, log: ft.Text) -> None | Exception:
    """
    Automatically register past papers into db

    Args:
        path: Path to folder
        log: flet text control element for logging
        
    Returns:
        None
    """

    file_list: list[str] = glob.glob(path + "/*.{pdf,doc,docx}")
    unmatch_list: list[str] = []
    matched_list: list[PastPaper] = []

    if not os.path.isdir(path):
        return FileNotFoundError(f"Cannot find directory: '{path}'")

    for file in file_list:
        para: list[str] = file.split(sep="_", maxsplit=3)
        past_paper: PastPaper = PastPaper()
        past_paper.pfile_path = path

        if para[0].isdigit() and para[1] in pattributes.sbjs and para[2] in pattributes.types:
            past_paper.pyear = int(para[0])
            past_paper.psbj = para[1]
            past_paper.ptype = para[2]
        else:
            unmatch_list.append(file)
            continue
            
