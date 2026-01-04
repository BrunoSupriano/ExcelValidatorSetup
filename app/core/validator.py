
import pandas as pd
from typing import List, Dict, Optional, Tuple
from .config import Config

class ValidationError:
    def __init__(self, file_name: str, message: str, severity: str = "critical", full_path: str = None):
        self.file_name = file_name
        self.message = message
        self.severity = severity # critical, warning, info
        self.full_path = full_path

class Validator:
    @staticmethod
    def validate_structure(file_path: str, df: pd.DataFrame) -> List[ValidationError]:
        errors = []
        from pathlib import Path
        file_name = Path(file_path).name

        if df.empty:
            errors.append(ValidationError(file_name, "O arquivo está vazio.", "critical", full_path=str(file_path)))
            return errors

        # Check for required columns
        missing_cols = [col for col in Config.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(ValidationError(
                file_name, 
                f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}", 
                "critical",
                full_path=str(file_path)
            ))

        # Check for duplicates
        if len(df.columns) != len(set(df.columns)):
            errors.append(ValidationError(file_name, "Existem colunas duplicadas no arquivo.", "warning", full_path=str(file_path)))

        return errors

    @staticmethod
    def compare_columns(dataframes: Dict[str, pd.DataFrame]) -> Tuple[bool, List[ValidationError]]:
        if not dataframes:
            return True, []

        reference_cols = set(list(dataframes.values())[0].columns)
        all_match = True
        errors = []
        from pathlib import Path

        for name, df in dataframes.items():
            # name might be full path or filename
            display_name = Path(name).name
            
            current_cols = set(df.columns)
            if current_cols != reference_cols:
                all_match = False
                # What is missing?
                missing = reference_cols - current_cols
                extra = current_cols - reference_cols
                
                if missing:
                    errors.append(ValidationError(display_name, f"Colunas faltando em relação ao primeiro arquivo: {', '.join(missing)}", "warning", full_path=name))
                if extra:
                    errors.append(ValidationError(display_name, f"Colunas extras encontradas: {', '.join(extra)}", "warning", full_path=name))
        
        return all_match, errors
