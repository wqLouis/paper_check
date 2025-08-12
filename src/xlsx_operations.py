import pandas as pd

def get_dataframe_from_path(path:str) -> Exception | pd.DataFrame:
    """
    Get the data in an Excel spreadsheet from path
    Args:
        path: Path to spreadsheet
    Returns:
        DataFrame: Pandas dataframe containing data from the first sheet of the Excel spreadsheet
    """
    
    try:
        xlsx_data: pd.DataFrame = pd.read_excel(path, sheet_name = 0)
        return xlsx_data
    except Exception as e:
        return e