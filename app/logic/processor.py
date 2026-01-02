
import pandas as pd
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QThread
import time

class WorkerSignals(QObject):
    progress = Signal(str)
    error = Signal(str)
    finished = Signal()

class ExcelProcessor(QObject):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.data_dir = Path('./DADOS')
        self.output_file = 'EXPORT1-clean.xlsx'

    def run(self):
        try:
            self.signals.progress.emit("Iniciando processamento...")
            
            if not self.data_dir.exists():
                raise FileNotFoundError(f"Diretório '{self.data_dir}' não encontrado.")

            # 1. Find files
            xlsx_files = list(self.data_dir.glob('*.xlsx'))
            if not xlsx_files:
                raise FileNotFoundError("Nenhum arquivo .xlsx encontrado em ./DADOS")

            self.signals.progress.emit(f"Encontrados {len(xlsx_files)} arquivos.")

            # 2. Read files
            dataframes = {}
            for file in xlsx_files:
                self.signals.progress.emit(f"Lendo {file.name}...")
                dataframes[file.name] = pd.read_excel(file)

            # 3. Check columns
            self.signals.progress.emit("Verificando colunas...")
            columns_list = [set(df.columns) for df in dataframes.values()]
            all_same_columns = all(cols == columns_list[0] for cols in columns_list)

            if not all_same_columns:
                details = []
                for name, df in dataframes.items():
                    details.append(f"{name}: {len(df.columns)} colunas")
                raise ValueError(f"Colunas diferentes encontradas!\n" + "\n".join(details))

            # 4. Concatenate
            self.signals.progress.emit("Combinando arquivos...")
            
            # Filter out empty or none dfs
            valid_dfs = [df for df in dataframes.values() if not df.empty and not df.isna().all().all()]
            
            if not valid_dfs:
                 raise ValueError("Todos os arquivos encontrados estão vazios.")
                 
            # Fix FutureWarning about empty/NA columns
            # We explicitly allow it or filter. simpler to just silence it or let pandas handle it by ensuring data is clean
            # For this context, standard concat is fine, but let's suppress the warning for cleaner logs
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=FutureWarning)
                arquivo = pd.concat(valid_dfs, ignore_index=True)
                
            self.signals.progress.emit(f"Combinado: {len(arquivo)} linhas.")

            # 5. Clean Data
            self.signals.progress.emit("Limpando dados...")
            cols_to_drop = ['Linha selecionada', 'Status Nota de Serviço']
            # Only drop if they exist to avoid errors if source changes slightly
            existing_cols_to_drop = [c for c in cols_to_drop if c in arquivo.columns]
            arquivo = arquivo.drop(columns=existing_cols_to_drop)

            # 6. Calc Logic
            self.signals.progress.emit("Calculando datas...")
            
            tipo_de_nota_ref = {
                'CN': 2, 'CT': 0, 'MI': 2, 'RE': 0, 'TE': 1
            }
            if 'Tipo de nota' in arquivo.columns:
                arquivo['Acréscimo de dias'] = arquivo['Tipo de nota'].map(tipo_de_nota_ref).fillna(0)
            else:
                self.signals.progress.emit("Aviso: Coluna 'Tipo de nota' não encontrada. Assumindo 0 dias.")
                arquivo['Acréscimo de dias'] = 0

            if 'Conclusão desejada' in arquivo.columns:
                arquivo['Data limite REAL'] = arquivo.apply(self.calcular_nova_data, axis=1)
            else:
                 raise ValueError("Coluna 'Conclusão desejada' obrigatória não encontrada.")

            if 'Encerram.por data' in arquivo.columns:
                arquivo['Quantidade de dias vencidos'] = (arquivo['Data limite REAL'] - arquivo['Encerram.por data']).dt.days
                arquivo['STATUS'] = arquivo['Quantidade de dias vencidos'].apply(lambda x: 'DENTRO DO PRAZO' if x >= 0 else 'FORA DO PRAZO')
            else:
                 self.signals.progress.emit("Aviso: 'Encerram.por data' não encontrada. Status ignorado.")

            # 7. Export
            self.signals.progress.emit(f"Salvando em {self.output_file}...")
            arquivo.to_excel(self.output_file, index=False)
            
            self.signals.progress.emit("Concluído com sucesso!")
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))

    def calcular_nova_data(self, row):
        try:
            conclusao_desejada = pd.to_datetime(row['Conclusão desejada'])
            acrescimo_dias = row['Acréscimo de dias']
            
            if pd.isna(conclusao_desejada):
                return pd.NaT

            if acrescimo_dias == 0:
                return conclusao_desejada
            
            dia_da_semana = conclusao_desejada.weekday() + 1  # 1=Mon, 7=Sun
            
            days_to_add = 0
            if dia_da_semana <= 3:
                days_to_add = acrescimo_dias
            elif dia_da_semana == 4:
                days_to_add = acrescimo_dias + 2
            elif dia_da_semana == 5:
                days_to_add = acrescimo_dias + 2
            elif dia_da_semana == 6:
                days_to_add = acrescimo_dias + 1
            elif dia_da_semana == 7:
                days_to_add = acrescimo_dias
                
            return conclusao_desejada + pd.Timedelta(days=days_to_add)
        except Exception:
            return pd.NaT

class ProcessorThread(QThread):
    def __init__(self, processor):
        super().__init__()
        self.processor = processor

    def run(self):
        self.processor.run()
