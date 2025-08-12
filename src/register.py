import os
import shutil
import sqlite3 as sql
from core import init_db
from core import unwrap
from core import preference
from core import pattributes

def register_papers(pfile_path:str, pyear:int, psbj:str, ptype:str) -> Exception | None:
    
    """
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
        return FileNotFoundError(f"target directory not found '{preference.pfile_target_path}'")
    if psbj not in pattributes.sbjs:
        return ValueError(f"has no type for psbj={psbj}\nwe have these sbjs {str(pattributes.sbjs)}")
    if ptype not in pattributes.types:
        return ValueError(f"has no type for psbj={ptype}\nwe have these types {str(pattributes.types)}")
    
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

    cur.execute(insert_query, (preference.pfile_target_path+os.path.basename(pfile_path), pyear, psbj, ptype))
    con.commit()
    return