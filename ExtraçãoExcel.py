# %%
import pandas as pd
import os
from pathlib import Path

# Find all .xlsx files in the current directory
xlsx_files = list(Path('./DADOS').glob('*.xlsx'))

# Read all files and store them with their names
dataframes = {}
for file in xlsx_files:
    dataframes[file.name] = pd.read_excel(file)

# Check if all files have the same columns
columns_list = [set(df.columns) for df in dataframes.values()]
all_same_columns = all(cols == columns_list[0] for cols in columns_list)

print(f"Arquivos encontrados: {list(dataframes.keys())}")
print(f"Todas as colunas são iguais: {all_same_columns}")

if all_same_columns:
    # Combine all dataframes
    arquivo = pd.concat(dataframes.values(), ignore_index=True)
    print(f"\nArquivo combinado: {len(arquivo)} linhas")
    print(f"Colunas: {list(arquivo.columns)}")
else:
    print("\nColunas diferentes encontradas:")
    for name, df in dataframes.items():
        print(f"{name}: {set(df.columns)}")


# %%
import pandas as pd

arquivo.head(3)
# diga o tamanho do arquivo em mb
tamanho_arquivo_mb = arquivo.memory_usage(deep=True).sum() / (1024 * 1024)
print(f"Tamanho do arquivo: {tamanho_arquivo_mb:.2f} MB")


# %%
# remova as colunas "Linha selecionada" e "Unnamed: 0"
arquivo = arquivo.drop(columns=['Linha selecionada', 'Status Nota de Serviço'])
arquivo.to_excel('EXPORT1-clean.xlsx', index=False)

tamanho_arquivo_mb = arquivo.memory_usage(deep=True).sum() / (1024 * 1024)
print(f"Tamanho do arquivo: {tamanho_arquivo_mb:.2f} MB")

# %%
tipo_de_nota_ref = {
    'CN': 2,
    'CT': 0,
    'MI': 2,
    'RE': 0,
    'TE': 1
}
arquivo['Acréscimo de dias'] = arquivo['Tipo de nota'].map(tipo_de_nota_ref).fillna(0)
arquivo.head(10)

# %%
# crie essa formula em python levando em consideração que P é a coluna Conclusão Desejada e R é a coluna Acréscimo de dias =SE(R15=0;P15;SE(DIA.DA.SEMANA(P15;2)<=3;P15+R15;SE(DIA.DA.SEMANA(P15;2)=4;P15+(R15+2);SE(DIA.DA.SEMANA(P15;2)=5;P15+(R15+2);SE(DIA.DA.SEMANA(P15;2)=6;P15+(R15+1);SE(DIA.DA.SEMANA(P15;2)=7;P15+R15;"indefinido"))))))
def calcular_nova_data(row):
    conclusao_desejada = row['Conclusão desejada']
    acrescimo_dias = row['Acréscimo de dias']
    
    if acrescimo_dias == 0:
        return conclusao_desejada
    
    dia_da_semana = conclusao_desejada.weekday() + 1  # Monday=1, Sunday=7
    
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
        return "indefinido"
arquivo['Data limite REAL'] = arquivo.apply(calcular_nova_data, axis=1)
arquivo.head(10)


# %%
# adicione uma coluna chamada quantidade de dias vencidos que é a diferença entre a Data limite REAL e a data limite real e a Encerram.por data
arquivo['Quantidade de dias vencidos'] = (arquivo['Data limite REAL'] - arquivo['Encerram.por data']).dt.days

# adicione uma coluna chamada STATUS que retorne a dentro do prazo se a quantidade de dias for maior ou igual a 0 e vencido se for menor que 0
arquivo['STATUS'] = arquivo['Quantidade de dias vencidos'].apply(lambda x: 'DENTRO DO PRAZO' if x >= 0 else 'FORA DO PRAZO')


# %%
arquivo


