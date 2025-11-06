import flet as ft
import sqlite3 as sql
import os
import json
import glob
import src.core as core
import src.ocr as ocr
from src.core import preference
from src.core import pattributes

def get_data_from_psource(
    pyear: int | None,
    psbj: str | None,
    ptype: str | None,
    page_num: int,
    items_per_page: int,
) -> list[ft.DataRow]:
    """
    Fetch data from psource of db
    Args:
        pyear: Year
        psbj: Subject
        ptype: Past paper type
        page_num: The page number of the table
        items_per_page: The no. of element in one page
    Returns:
        list[ft.DataRow]
    """

    try:
        con: sql.Connection = sql.connect(f"{preference.db_path}")
    except sql.OperationalError:
        con = core.unwrap(core.init_db())

    query: str = """
    select * from psource
    where   (pyear = ? or ? is null) and
            (psbj = ? or ? is null) and
            (ptype = ? or ? is null)
    limit ? offset ?
    """

    cur: sql.Cursor = con.cursor()
    try:
        db_data = cur.execute(
            query,
            (
                pyear,
                pyear,
                psbj,
                psbj,
                ptype,
                ptype,
                items_per_page,
                page_num * items_per_page,
            ),
        ).fetchall()
    except sql.OperationalError as e:
        print("Table not found\nTry to init table")
        con = core.unwrap(core.init_db())
        cur = con.cursor()
        try:
            db_data = cur.execute(
                query,
                (
                    pyear,
                    pyear,
                    psbj,
                    psbj,
                    ptype,
                    ptype,
                    items_per_page,
                    page_num * items_per_page,
                ),
            ).fetchall()
        except BaseException as e:
            print("failed to get data from psource")
            con.close()
            return []

    con.close()

    data_rows: list[ft.DataRow] = []

    for i in db_data:
        data_rows.append(
            ft.DataRow(
                [
                    ft.DataCell(content=ft.Checkbox()),
                    ft.DataCell(content=ft.Text(value=str(i[2]))),
                    ft.DataCell(content=ft.Text(value=str(i[3]))),
                    ft.DataCell(content=ft.Text(value=str(i[4]))),
                    ft.DataCell(
                        content=ft.Text(
                            spans=[
                                ft.TextSpan(
                                    text="CLICK TO OPEN FILE",
                                    url=os.path.abspath(str(i[1])),
                                )
                            ]
                        )
                    ),
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
            dropdown: ft.Dropdown = ft.Dropdown(
                label=i, options=[], col={"md": 2, "lg": 2}
            )

            if dropdown.options is not None:
                for j in pattributes.subattribute_dict[i]:
                    dropdown.options.append(ft.DropdownOption(text=str(j)))
            option_row.controls.append(dropdown)
    return option_row


def send_to_preprocess(
    datatable: ft.DataTable | list[str],
    progress_bar: ft.ProgressBar | None,
    page: ft.Page,
    btn: ft.ElevatedButton
) -> tuple[list[list[str]], list[str]]:
    """
    Preprocess the past paper throgh a pipeline:
    Fetch pdf -> OCR -> LLM filter unwanted text -> Embeddings -> Insert questions into DB

    Args:
        datatable: A flet datatable or a list[str]
        progress_bar: For progress of OCR. If None then a dummy progress_bar will be created in the function
        page: The flet app page
        btn: The elevated button for triggering this function. Will try to disable the button prevent excess request.
        model_name: The llm model used for slicing the OCR string

    Returns:
        The result of preprocess: tuple[list[list[str]], list[str]]. The first element in the tuple contains the result list of each paper and in the list it contains the list of sliced string. The second element contains the file name of the preprocessed PDFs.
        None: The function return None when there is no result
    """

    from llama_cpp import Llama
    print("llama_cpp loaded")

    selected_papers: dict = {"year": [], "sbj": [], "type": [], "path": []}

    if progress_bar is None:
        progress_bar = ft.ProgressBar()  # dummy bar

    if isinstance(datatable, ft.DataTable) and datatable.rows is not None:
        print("datatable found as flet datatable structure")
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
    elif datatable is list[str]:
        print("datatable found as list[str] structure")
        datatable_filename: list[str] = [os.path.basename(i) for i in datatable]
        for idx, i in enumerate(datatable_filename):
            if not os.path.exists(i):
                datatable[idx] = "ERROR"
            else:
                if i is str:
                    parsed_papers: list[str] = i.split("_")
                    selected_papers["year"] = parsed_papers[0]
                    selected_papers["sbj"] = parsed_papers[1]
                    selected_papers["type"] = parsed_papers[2]
                    selected_papers["path"] = datatable[idx]

    print(f"Selected paper: {selected_papers}")
    if len(selected_papers["path"]) == 0:
        print("no selected paper exiting...")
        return ([],[])

    ocred_pdf_list: list[str] = [
        os.path.splitext(os.path.basename(i))[0]
        for i in glob.glob(f"{preference.setting_dict["temp_path"]}/*.json")
    ]
    print(f"found ocred pdf: {ocred_pdf_list}")

    for i in selected_papers["path"]:
        if os.path.splitext(os.path.basename(i))[0] in ocred_pdf_list:
            continue

        if os.path.splitext(os.path.basename(i))[1] == ".pdf":
            progress_bar.value = 0
            result_str: list[str] = ocr.pdf_ocr(
                i, page_progress_bar=progress_bar, page=page, btn=btn
            )

            file_name: str = f"/{os.path.splitext(os.path.basename(i))[0]}.json"

            with open(
                f"{preference.setting_dict["temp_path"]}{file_name}", mode="w"
            ) as f:
                json.dump(result_str, f, indent=4)

    ocred_pdf_list = glob.glob(f"{preference.setting_dict["temp_path"]}/*.json")

    if len(ocred_pdf_list) == 0:
        print("No ocred pdf found exiting preprocess...")
        return ([],[])

    con: sql.Connection = sql.connect(f"{preference.db_path}")
    cur: sql.Cursor = con.cursor()
    pid_list: list[int] = []

    for i in ocred_pdf_list:
        pid_list.append(
            int(
                cur.execute(
                    "select pid from psource where pfile_path like ?",
                    (f"%{os.path.splitext(os.path.basename(i))[0]}%", ),
                ).fetchone()[0]
            )
        )

    if os.path.exists(preference.model_path):
        print("loading llm model")
        llm: Llama = Llama(
            model_path=preference.model_path, verbose=False, n_ctx=2048
        )
    else:
        raise Exception("llm model not found")

    try:
        os.mkdir(f"{preference.setting_dict["temp_path"]}/filtered")
    except BaseException:
        pass

    sys_prompt: str = """
                        You are an AI responsible for preprocessing OCR-extracted text from exam papers for use in embedding models. You will receive a **list of strings**, where each string represents a line (or text block) from the OCR result.

                        Your task is to:

                        1. **Analyze the entire list** and reconstruct the logical flow of the text.
                        2. **Identify and extract individual questions** — each should be a complete, self-contained question.
                        3. **Remove all irrelevant content**, such as:
                           - Headers, footers, or watermarks (e.g., "Page 1", "Confidential")
                           - Instructions (e.g., "Answer all questions", "Write in complete sentences")
                           - Blank lines or placeholder lines (e.g., "Name: ______")
                           - Answer choices (e.g., "A. 4  B. 5  C. 6") — unless part of the question
                           - Section titles (e.g., "Section A: Biology") unless they provide essential context
                        4. **Remove question numbering or labels** (e.g., "1.", "Q3:", "b)") — output only the clean question text.
                        5. **Correct minor OCR errors** only when the intended word or phrase is clear.
                        6. Return a **JSON array** of cleaned question strings, with no numbering or prefixes.

                        Output Format:
                        ```json
                        ["{cleaned question 1}", "{cleaned question 2}", ...]
                        ```

                        If no valid questions are found, return:
                        ```json
                        []
                        ```
                        If question is incomplete, return:
                        ```json
                        ["incomplete"]
                        ```

                        ---

                        **Example Input (list of strings):**
                        ```json
                        [
                          "EXAM PAPER - DO NOT WRITE ON THIS PAGE",
                          "Name: ______________   Grade: __________",
                          "",
                          "1. What is the capital of France?",
                          "   A. London   B. Paris   C. Berlin",
                          "",
                          "2. Describe the process of photosynthesis.",
                          "",
                          "End of Section A"
                        ]
                        ```

                        **Expected Output:**
                        ```json
                        [
                          "What is the capital of France?",
                          "Describe the process of photosynthesis."
                        ]
                        ```

                        ---

                        Now process the following OCR result (list of strings):

                        ---

                        """
    sbj_prompt: dict = {}
    if os.path.exists(preference.setting_dict["plugins_path"] + "/sbj_prompt.json"):
        # try to load subject specify prompt
        with open(
            file=(preference.setting_dict["plugins_path"] + "/sbj_prompt.json"),
            mode="r",
        ) as f:
            sbj_prompt: dict = json.load(f)

    chunk_size: int = 10
    iteration_len: int = 5
    llm_result: list[list[str]] = []

    # TODO: add open router api support

    for i in ocred_pdf_list:
        # Parse file name and use sbj_prompt
        if i.split("_")[1] in sbj_prompt:
            print(f"found subject specific prompt: {sbj_prompt[i.split("_")[1]]}")
            sys_prompt = sbj_prompt[i.split("_")[1]]

        with open(file=i, mode="r") as f:
            json_str: list[str] = json.load(f)
        if len(json_str) <= 0:
            return ([],[])
        ptr: int = 0
        failed_count: int = 0
        while True:
            chunked: str = json_str[ptr : min(ptr + chunk_size, len(json_str) - 1)]
            while True:
                print(chunked)
                llm_raw_result = str(
                    llm.create_chat_completion(
                        messages=[{"role": "user", "content": f"{sys_prompt}\n{chunked}"}],
                        response_format={
                            "type": "json_object",
                            "schema": {
                                "type" : "array",
                                "items" : {
                                    "type" : "string"
                                }
                            }
                        }
                    )
                )
                print(llm_raw_result)
                try:
                    llm_result[-1] += json.loads(llm_raw_result)
                except ValueError:
                    failed_count += 1
                    if failed_count > 5:
                        print(f"failed to process: {ptr}")
                    else:
                        continue
                break
            if ptr + chunk_size > len(json_str) - 1:
                break
            ptr += iteration_len
            progress_bar.value = min(float(ptr) / float(json_str), 1)
            page.update() # idk is this needed
            llm_result.append([])

    return (llm_result, ocred_pdf_list)

def send_to_db(llm_result: list[list[str]], ocred_pdf_list: list[str]):
    con = sql.connect(preference.db_path)
    cur = con.cursor()
    insert_query = "insert into qsource (qstr, pid) values (? ,?);"
    get_pid_query = "select pid from psource where pfile_path = ?;"
    
    print("insert into db")
    
    pid: list[int] = [int(cur.execute(get_pid_query, i).fetchone()) for i in ocred_pdf_list]
    
    for (idx, i) in enumerate(llm_result):
        for j in i:
            cur.execute(insert_query, (j, pid[idx]))
            print(f"\ninsert into db with val: {j}")
    con.commit()
    
    get_qid_query = "select qid from qsource where qstr = ?;"

    if not os.path.exists(preference.model_path):
        print(f"{preference.model_path} Failed to locate LLM model, check settings")
        return

    print("loading llama_cpp and chromadb")
    from llama_cpp import Llama
    import chromadb

    print("connect to chromadb")
    client = chromadb.PersistentClient(preference.setting_dict["vcdb_path"]+"/embed.db")
    collection = client.get_or_create_collection(
        name="questions"
    )
    print(f"loading embed_model with path: {preference.setting_dict["embed_model_path"]}")
    embed_model = Llama(model_path=preference.setting_dict["embed_model_path"], embedding=True)

    import numpy as np

    for i in llm_result:
        embeddings = np.array(embed_model.embed(input=i))
        print(embeddings)
        collection.add(ids=cur.executemany(get_qid_query, i).fetchall(), embeddings=embeddings, metadatas=[{"pid": i} for i in pid])
    
    return