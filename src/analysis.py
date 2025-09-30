from llama_cpp import Llama
from src.core import preference
import flet as ft
import sqlite3 as sql

model_path: str = preference.model_path
pfile_target_path: str = preference.pfile_target_path
db_path: str = preference.db_path

def analysis(input: str, pids: list[str] | None) -> Exception | list[str]:
    """
    Analysis simularity mode (Not working)

    Args:
        model_path: Path of embedding model
    Returns:
        None: Return exception if error occurs
    """

    model: Llama = Llama(model_path=model_path, embedding=True)

    import chromadb

    client = chromadb.PersistentClient(preference.setting_dict["vcdb_path"]+"/embed.db")
    collection = client.get_collection(
        name="questions"
    )
    
    # I hope it wont fucked up type casting
    import typing
    return [str(i) for i in collection.query(query_embeddings=typing.cast(list[float],model.embed(input=input)), n_results=5, ids=pids)["ids"]]

def construct_table_with_result(ids: list[str]) -> list[ft.DataRow]:
    con = sql.connect(preference.db_path)
    cur = con.cursor()
    query = "select * from qsource where qid = ?;"

    query_result = cur.executemany(query, ids).fetchall()
    row = [ft.DataRow(cells=[])]

    for i in query_result:
        for j in i:
            row[-1].cells.append(ft.DataCell(
                content=ft.Text(value=str(j))
            ))
        row.append(ft.DataRow(cells=[]))
    
    return row