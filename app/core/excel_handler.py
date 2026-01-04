
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
    def save_excel(df: pd.DataFrame, path: str, progress_callback=None):
        if progress_callback:
            progress_callback(0, "Preparando dados...")
            
        try:
            from openpyxl import Workbook
            import numpy as np
            
            # 'write_only=True' streams data to a temporary file immediately,
            # keeping memory low and shifting the work to the loop (progress bar)
            # rather than the final save() call.
            wb = Workbook(write_only=True)
            ws = wb.create_sheet("Relatório")
            
            # Write Header
            ws.append(df.columns.tolist())
            
            # Convert to numpy/list for speed (and handle NaN)
            # Replace NaN with None (which openpyxl treats as empty cell)
            df_cleaned = df.replace({np.nan: None})
            
            total_rows = len(df_cleaned)
            rows = df_cleaned.itertuples(index=False, name=None)
            
            progress_step = max(1, total_rows // 100) # Update every 1% or so
            
            for i, row in enumerate(rows, 1):
                ws.append(row)
                
                if progress_callback and i % progress_step == 0:
                    percent = int((i / total_rows) * 95) # Reserve 5% for final zip
                    progress_callback(percent, "Gravando dados...")
            
            if progress_callback:
                progress_callback(95, "Finalizando arquivo (comprimindo)...")
                
            wb.save(path)
            
            if progress_callback:
                progress_callback(100, "Concluído!")
                
        except Exception as e:
            print(f"Write-only save failed: {e}")
            if progress_callback:
                progress_callback(0, "Tentando método alternativo...")
            # Fallback
            df.to_excel(path, index=False, engine='xlsxwriter')
