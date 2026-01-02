
import pandas as pd
from pathlib import Path
from typing import Dict, List
import shutil

class ExcelHandler:
    @staticmethod
    def load_files(file_paths: List[str]) -> Dict[str, pd.DataFrame]:
        dataframes = {}
        for path in file_paths:
            try:
                p = Path(path)
                # Load only headers first to check validity? No, load standard for now.
                # Using openpyxl engine for .xlsx
                df = pd.read_excel(p, engine='openpyxl')
                dataframes[p.name] = df
            except Exception as e:
                print(f"Erro ao ler {path}: {e}")
                # We might want to return errors here too, but for now just skip or empty
                dataframes[Path(path).name] = pd.DataFrame() 
        return dataframes

    @staticmethod
    def save_excel(df: pd.DataFrame, path: str):
        df.to_excel(path, index=False, engine='xlsxwriter')
