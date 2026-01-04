
import pandas as pd
from .config import Config

class Processor:
    @staticmethod
    def calculate_real_deadline(row):
        conclusao_desejada = row.get('Conclusão desejada')
        acrescimo_dias = row.get('Acréscimo de dias', 0)
        
        if pd.isnull(conclusao_desejada):
            return pd.NaT

        if acrescimo_dias == 0:
            return conclusao_desejada
        
        try:
            # Ensure it's a timestamp
            if not isinstance(conclusao_desejada, pd.Timestamp):
                conclusao_desejada = pd.to_datetime(conclusao_desejada)

            dia_da_semana = conclusao_desejada.weekday() + 1  # Monday=1, Sunday=7
            
            # Logic ported from ExtraçãoExcel.py
            if dia_da_semana <= 3:  # Monday to Wednesday
                return conclusao_desejada + pd.Timedelta(days=acrescimo_dias)
            elif dia_da_semana == 4:  # Thursday
                return conclusao_desejada + pd.Timedelta(days=acrescimo_dias + 2)
            elif dia_da_semana == 5:  # Friday
                return conclusao_desejada + pd.Timedelta(days=acrescimo_dias + 2)
            elif dia_da_semana == 6:  # Saturday
                return conclusao_desejada + pd.Timedelta(days=acrescimo_dias + 1)
            elif dia_da_semana == 7:  # Sunday
                return conclusao_desejada + pd.Timedelta(days=acrescimo_dias)
            else:
                return pd.NaT
        except Exception:
            return pd.NaT

    @staticmethod
    def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        # Create a copy to avoid SettingWithCopy warnings handled upstream
        df = df.copy()

        # 1. Map 'Acréscimo de dias'
        if 'Tipo de nota' in df.columns:
            df['Acréscimo de dias'] = df['Tipo de nota'].map(Config.TIPO_DE_NOTA_REF).fillna(0)
        
        # 2. Calculate 'Data limite REAL'
        if 'Conclusão desejada' in df.columns and 'Acréscimo de dias' in df.columns:
             # Ensure datetime
            df['Conclusão desejada'] = pd.to_datetime(df['Conclusão desejada'], errors='coerce')
            df['Data limite REAL'] = df.apply(Processor.calculate_real_deadline, axis=1)

        # 3. Calculate 'Quantidade de dias vencidos'
        if 'Data limite REAL' in df.columns and 'Encerram.por data' in df.columns:
            df['Encerram.por data'] = pd.to_datetime(df['Encerram.por data'], errors='coerce')
            df['Quantidade de dias vencidos'] = (df['Data limite REAL'] - df['Encerram.por data']).dt.days

        # 4. Status
        if 'Quantidade de dias vencidos' in df.columns:
            df['STATUS'] = df['Quantidade de dias vencidos'].apply(
                lambda x: 'DENTRO DO PRAZO' if x >= 0 else 'FORA DO PRAZO'
            )
            
        # 5. Cleanup unwanted columns
        cols_to_drop = ['Linha selecionada', 'Status Nota de Serviço']
        df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
            
        return df
