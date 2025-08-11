from llama_cpp import Llama
import os
import shutil
import sqlite3 as sql
from src.unwrap import unwrap
import numpy as np

model_path: str = "./models/Qwen3-Embedding-4B-Q6_K.gguf"
pfile_target_path: str = "./db/papers"
db_path: str = "./db"

class pattributes:
    """
    types available for past papers
    """
    types:set[str] = set(["DSE", "ALV", "CE"])
    sbjs:set[str] = set(["MATH", "PHY", "CHEM", "BIO", "ICT"])

def init_db() -> Exception | sql.Connection:
    """
    Initialize sqlite database with basic structures
    """
    
    if not os.path.exists(db_path):
        try:
            os.mkdir(db_path)
        except Exception as e:
            return e
    
    if not os.path.exists(pfile_target_path):
        try:
            os.mkdir(db_path)
        except Exception as e:
            return e

    con: sql.Connection = sql.connect(db_path + "/past_papers.db")
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

def load_model(path: str) -> Exception | Llama:
    if not os.path.exists(path):
        return FileNotFoundError(f"failed to load model '{path}'")
    try:
        ebd = Llama(path)
        return ebd
    except Exception as e:
        return e

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
    if not os.path.exists(pfile_target_path):
        return FileNotFoundError(f"target directory not found '{pfile_target_path}'")
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
        shutil.copyfile(pfile_path, pfile_target_path)
    except Exception as e:
        return e

    cur.execute(insert_query, (pfile_target_path+os.path.basename(pfile_path), pyear, psbj, ptype))
    con.commit()
    return

def examine(data: list[str] | str, pid: int) -> Exception | None:
    """
    Examine the input and create a sqlite db for further analsys
    Returns:
        None:
    """
    
    con: sql.Connection = unwrap(init_db())
    cur: sql.Cursor = con.cursor()

    pid_count = cur.execute("SELECT count(*) FROM psource WHERE pid = ?;", (pid,)).fetchone()[0]
    if pid_count == 0:
        return ValueError(f"pid={pid} is not in psource")
    
    model: Llama = unwrap(load_model(model_path))
    
    insert_query: str = """
        INSERT INTO qsource (qstr, qebd_v, pid)
        VALUES (?, ?, ?)
    """
    if isinstance(data, list):
        for i in data:
            qebd_v:bytes = np.array(model.embed(i)).tobytes()
            cur.execute(insert_query,(i, qebd_v, pid))
    else:
        qebd_v:bytes = np.array(model.embed(data)).tobytes()
        cur.execute(insert_query, (data, qebd_v, pid))
    
    con.commit()

def analysis() -> Exception | None:
    """
    Analysis simularity mode
    
    Args:
        model_path: Path of embedding model
    Returns:
        None: Return exception if error occurs
    """

    while True:
        input_xl_path: str = str(input("Path to xlsx:"))
        if os.path.exists(input_xl_path):
            break
    
    model: Llama = unwrap(load_model(model_path))
    _ = model  # Prevent unused variable error
    print("done")