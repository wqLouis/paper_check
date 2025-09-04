import flet as ft
import sqlite3 as sql
import os
import json
import glob
import src.ocr as ocr
from src.core import preference
from src.core import pattributes
from src.main_utils import load_model
from llama_cpp import Llama

def get_data_from_psource(pyear: int | None, psbj: str | None, ptype: str | None, page_num: int, items_per_page: int) -> list[ft.DataRow]:
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


    con: sql.Connection = sql.connect("D:\\vsproject\\paper_check\\db\\past_papers.db")
    query: str = """
    select * from psource
    where   (pyear = ? or ? is null) and
            (psbj = ? or ? is null) and
            (ptype = ? or ? is null)
    limit ? offset ?
    """

    cur: sql.Cursor = con.cursor()
    db_data = cur.execute(query, (pyear, pyear, psbj, psbj, ptype, ptype, items_per_page, page_num*items_per_page)).fetchall()

    data_rows: list[ft.DataRow] = []

    for i in db_data:
        data_rows.append(
            ft.DataRow(
                [
                    ft.DataCell(content=ft.Checkbox()),
                    ft.DataCell(content=ft.Text(value=str(i[2]))),
                    ft.DataCell(content=ft.Text(value=str(i[3]))),
                    ft.DataCell(content=ft.Text(value=str(i[4]))),
                    ft.DataCell(content=ft.Text(spans=[ft.TextSpan(text="CLICK TO OPEN FILE", url=os.path.abspath(str(i[1])))]))
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
            dropdown: ft.Dropdown = ft.Dropdown(label=i, options=[], col={"md": 2, "lg": 2})

            if dropdown.options is not None:
                for j in pattributes.subattribute_dict[i]:
                    dropdown.options.append(
                        ft.DropdownOption(
                            text=str(j)
                        )
                    )
            option_row.controls.append(
                dropdown
            )
    return option_row

def send_to_preprocess(datatable: ft.DataTable, progress_bar: ft.ProgressBar, page: ft.Page, btn: ft.ElevatedButton, model_name: str = "Qwen3-8B-Q5_0.gguf") -> None:
    """
        Preprocess the past paper throgh a pipeline:
        Fetch pdf -> OCR -> LLM filter unwanted text -> Embeddings -> Insert questions into DB
    """


    selected_papers: dict ={
        "year" : [],
        "sbj" : [],
        "type" : [],
        "path" : []
    }
    
    if datatable.rows is not None:
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
    
    if len(selected_papers["path"]) == 0:
        return

    ocred_pdf_list = [os.path.splitext(os.path.basename(i))[0] for i in glob.glob(f"{preference.setting_dict["temp_path"]}/*.json")]

    for i in selected_papers["path"]:
        if os.path.splitext(os.path.basename(i))[0] in ocred_pdf_list:
            continue

        if os.path.splitext(os.path.basename(i))[1] == ".pdf":
            progress_bar.value = 0
            result_str: list[str] = (ocr.pdf_ocr(i, page_progress_bar=progress_bar, page=page, btn=btn))
            
            file_name: str = f"/{os.path.splitext(os.path.basename(i))[0]}.json"
            
            with open(f"{preference.setting_dict["temp_path"]}{file_name}", mode="w") as f:
                json.dump(result_str, f, indent=4)
    
    ocred_pdf_list = glob.glob(f"{preference.setting_dict["temp_path"]}/*.json")
    
    if len(ocred_pdf_list) == 0:
        return

    con: sql.Connection = sql.connect(f"{preference.db_path}/past_paper.db")
    cur: sql.Cursor = con.cursor()
    pid_list: list[int] = []

    for i in ocred_pdf_list:
        pid_list.append(int(cur.execute("select pid from psource where pfile_path like ?", f"%{os.path.splitext(os.path.basename(i))[0]}%").fetchone()[0]))
    
    if os.path.exists(f"{preference.model_path}/llm/{model_name}"):
        llm: Llama = Llama(model_path=f"{preference.model_path}/llm/{model_name}", verbose=False)
    else:
        return

    os.mkdir(f"{preference.setting_dict["temp_path"]}/filtered")

    sys_prompt: str =   """
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
        with open(file=(preference.setting_dict["plugins_path"] + "/sbj_prompt.json"), mode="r") as f:
            sbj_prompt:dict = json.load(f)
        
    llm.create_chat_completion(messages=[{
        "role" : "system",
        "content" : sys_prompt
    }])

    chunk_size: int = 10
    iteration_len: int = 5

    for i in ocred_pdf_list:
        # Parse file name and use sbj_prompt
        if i.split("_")[1] in sbj_prompt:
            print(f"found subject specific prompt: {sbj_prompt[i.split("_")[1]]}")
            llm.reset()
            llm.create_chat_completion(messages=[{
                "role" : "system",
                "content" : sbj_prompt[i.split("_")[1]]
            }])
        
        with open(file=i, mode="r") as f:
            json_str: str = str(json.load(f))
        if len(json_str) <= 0:
            return
        ptr: int = 0
        failed_count: int = 0
        while True:
            chunked: str = json_str[ptr:ptr+chunk_size]
            llm_raw_result = str(llm.create_chat_completion(messages=[{
                "role" : "user",
                "content" : chunked
            }]))
            try:
                llm_result = json.loads(llm_raw_result)
            except ValueError:
                failed_count += iteration_len
                if failed_count > 5:
                    print(f"failed to process: {ptr}")
                else:
                    continue
            break

        with open(file=f"{preference.setting_dict["temp_path"]}/filtered/{os.path.basename(i)}", mode="w") as f:
            json.dump(llm_result, f, indent=4)