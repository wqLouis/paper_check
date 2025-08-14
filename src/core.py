from typing import TypeVar
import os
import sqlite3 as sql
import flet as ft

T = TypeVar("T")

class preference:
    model_path: str = "./models"
    pfile_target_path: str = "./db/papers"
    db_path: str = "./db"

class pattributes:
    """
    types available for past papers
    """
    types:set[str] = set(["DSE", "ALV", "CE"])
    sbjs:set[str] = set(["MATH", "PHY", "CHEM", "BIO", "ICT"])

def unwrap(value: T | Exception) -> T:
    """
    unwrap function return value and raise error

    Args:
        value:
            return variable of the function
    
    Returns:
        the value itself
    """
    if isinstance(value, Exception):
        raise value
    else:
        return value
    
def init_db() -> Exception | sql.Connection:
    """
    Initialize sqlite database with basic structures
    """
    
    if not os.path.exists(preference.db_path):
        try:
            os.mkdir(preference.db_path)
        except Exception as e:
            return e
    
    if not os.path.exists(preference.pfile_target_path):
        try:
            os.mkdir(preference.db_path)
        except Exception as e:
            return e

    con: sql.Connection = sql.connect(preference.db_path + "/past_papers.db")
    cur: sql.Cursor = con.cursor()

    table_count:int = int(cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table';").fetchone()[0])
    if table_count > 0:
        return con
    try:
        cur.execute(
        """
        CREATE TABLE psource(
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            pfile_path TEXT NOT NULL,
            pyear INTEGER NOT NULL,
            psbj TEXT,
            ptype TEXT
        );
        """
        )
        cur.execute(
        """
        CREATE TABLE qsource(
            qid INTEGER PRIMARY KEY AUTOINCREMENT,
            qstr TEXT NOT NULL,
            qebd_v BLOB NOT NULL,
            pid INTEGER NOT NULL,
            FOREIGN KEY (pid) REFERENCES psource(pid)
        );
        """
        )
        
        con.commit()

        return con
    except Exception as e:
        return e

def unwrap_str(String: str | None) -> str:
    """
    Takes in var with type str or None and return only str

    Args:
        String: Input str
    Returns:
        If String is None then returns "" else return String itself
    """

    return String if String is not None else ""