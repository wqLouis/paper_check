import rapidocr
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

def pdf_ocr(path: str) -> list[str]:
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

    for page in pdf:
        text += list(engine(img_content=np.array(page)).txts) # type: ignore
    return text
