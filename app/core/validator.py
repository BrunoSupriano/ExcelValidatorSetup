
import pandas as pd
from typing import List, Dict, Optional, Tuple
from .config import Config

class ValidationError:
    def __init__(self, file_name: str, message: str, severity: str = "critical"):
        self.file_name = file_name
        self.message = message
        self.severity = severity # critical, warning, info

class Validator:
    @staticmethod
    def validate_structure(file_path: str, df: pd.DataFrame) -> List[ValidationError]:
        errors = []
        file_name = str(file_path).split('\\')[-1]

        if df.empty:
            errors.append(ValidationError(file_name, "O arquivo está vazio.", "critical"))
            return errors

        # Check for required columns
        missing_cols = [col for col in Config.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(ValidationError(
                file_name, 
                f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}", 
                "critical"
            ))

        # Check for duplicates
        if len(df.columns) != len(set(df.columns)):
            errors.append(ValidationError(file_name, "Existem colunas duplicadas no arquivo.", "warning"))

        return errors

    @staticmethod
    def compare_columns(dataframes: Dict[str, pd.DataFrame]) -> Tuple[bool, List[ValidationError]]:
        if not dataframes:
            return True, []

        reference_cols = set(list(dataframes.values())[0].columns)
        all_match = True
        errors = []

        for name, df in dataframes.items():
            current_cols = set(df.columns)
            if current_cols != reference_cols:
                all_match = False
                # What is missing?
                missing = reference_cols - current_cols
                extra = current_cols - reference_cols
                
                if missing:
                    errors.append(ValidationError(name, f"Colunas faltando em relação ao primeiro arquivo: {', '.join(missing)}", "critical"))
                if extra:
                    errors.append(ValidationError(name, f"Colunas extras encontradas: {', '.join(extra)}", "warning"))
        
        return all_match, errors
