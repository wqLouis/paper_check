from llama_cpp import Llama
import os
import sqlite3 as sql
from core import unwrap
from core import init_db
from core import pattributes
from core import preference
import numpy as np

model_path: str = preference.model_path
pfile_target_path: str = preference.pfile_target_path
db_path: str = preference.db_path

def load_model(path: str) -> Exception | Llama:
    if not os.path.exists(path):
        return FileNotFoundError(f"failed to load model '{path}'")
    try:
        ebd = Llama(path)
        return ebd
    except Exception as e:
        return e

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