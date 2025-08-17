import rapidocr
import numpy as np
import flet as ft
from pdf2image import convert_from_path
from PIL import Image
from src.core import preference


def pdf_ocr(path: str, page_progress_bar: ft.ProgressBar, page: ft.Page, btn: ft.ElevatedButton) -> list[str]:
    """
    perform ocr with file

    Args:
        path: Path to PDF
    Returns:
        A list of string
    """
    pdf: list[Image.Image] = convert_from_path(pdf_path=path)
    text: list[str] = []

    engine: rapidocr.RapidOCR = rapidocr.RapidOCR()

    page_count: int = len(pdf)

    for i, pdf_page in enumerate(pdf):
        page_progress_bar.value = float(i) / float(page_count)
        page.update()
        ocr_result = engine(
            img_content=np.array(pdf_page), use_det=True, use_cls=True, use_rec=True
        )
        text += list(ocr_result.txts)  # type: ignore
    btn.disabled = False
    return text
