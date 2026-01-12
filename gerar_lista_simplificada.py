import pandas as pd
import csv

# Lê o arquivo original
df = pd.read_csv('lista.csv', dtype=str)

# Cria um novo arquivo simplificado apenas com nome e telefone
df_simplificado = df[['nome', 'telefone']].dropna()
df_simplificado.to_csv('lista_simplificada.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

print('Arquivo lista_simplificada.csv gerado com sucesso!')
