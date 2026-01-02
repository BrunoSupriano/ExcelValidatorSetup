
from typing import Dict

class Config:
    # Business Rules for "Tipo de nota" => "Acréscimo de dias"
    TIPO_DE_NOTA_REF: Dict[str, int] = {
        'CN': 2,
        'CT': 0,
        'MI': 2,
        'RE': 0,
        'TE': 1
    }

    # Required columns for validation
    REQUIRED_COLUMNS = [
        'Conclusão desejada',
        'Tipo de nota',
        'Encerram.por data'
    ]

    # Date format for display
    DATE_FORMAT = "%d/%m/%Y"
