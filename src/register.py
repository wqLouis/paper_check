import os
import stat
import glob
import shutil
import sqlite3 as sql
import flet as ft
from src.core import init_db
from src.core import unwrap
from src.core import unwrap_str
from src.core import preference
from src.core import pattributes


class PastPaper:
    pfile_path: str = ""
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
        shutil.copyfile(pfile_path, f"{preference.pfile_target_path}/{os.path.basename(pfile_path)}")
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


def auto_register_with_folder(path: str, log: ft.Text, update_control: ft.Control) -> Exception | None:
    """
    Automatically register past papers into db

    Args:
        path: Path to folder
        log: flet text control element for logging

    Returns:
        None
    """
    log.value = unwrap_str(log.value)

    file_list: list[str] = glob.glob(path + "\\*.pdf") + glob.glob(path + "\\*.doc") + glob.glob(path + "\\*.docx")
    unmatch_list: list[str] = [] # currently unused
    matched_list: list[PastPaper] = []

    if not os.path.isdir(path):
        return FileNotFoundError(f"Cannot find directory: '{path}'")

    for file in file_list:
        para: list[str] = os.path.splitext(os.path.basename(file))[0].split(sep="_")
        past_paper: PastPaper = PastPaper()
        past_paper.pfile_path = file

        if para[0].isdigit() and para[1] in pattributes.sbjs and para[2] in pattributes.types:
            past_paper.pyear = int(para[0])
            past_paper.psbj = para[1]
            past_paper.ptype = para[2]
        else:
            unmatch_list.append(file)
            log.value += f"> Failed to register file: '{file}'\n"
            update_control.update()
            continue
        
        matched_list.append(past_paper)
    
    for past_paper in matched_list:
        unwrap(register_papers(pfile_path = past_paper.pfile_path, pyear = past_paper.pyear, psbj = past_paper.psbj, ptype = past_paper.ptype))
        log.value += f"> Registered: '{past_paper.pfile_path}'\n"
        update_control.update()

def register_extract_format(file: str) -> PastPaper:
    """
        Extracts parameters for registration

        Args:
            file: file name
        
        Returns:
            A list of checked parameters
    """

    para: list[str] = os.path.splitext(os.path.basename(file))[0].split(sep="_")
    past_paper: PastPaper = PastPaper()

    if para[0].isdigit() and para[1] in pattributes.sbjs and para[2] in pattributes.types:
        past_paper.pyear = int(para[0])
        past_paper.psbj = para[1]
        past_paper.ptype = para[2]
    
    return past_paper