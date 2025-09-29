from llama_cpp import Llama
import sqlite3 as sql
from src.core import preference

model_path: str = preference.model_path
pfile_target_path: str = preference.pfile_target_path
db_path: str = preference.db_path

def analysis(input: str, pids: list[str] | None) -> Exception | str:
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
    query_result = collection.query(query_embeddings=[], n_results=5, ids=pids)

    # TODO: connect to sqlite and get the question text
    con = sql.Connection(preference.db_path)
    cur = con.cursor()
    cur.execute("""""")

    return Exception("Uncomplete function")
