"""
Script para visualizar a tabela de anomalias que será incluída no PDF.
"""

import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.reports import create_anomaly_table_data

print("=" * 60)
print("TABELA DE ANOMALIAS - PREVIEW")
print("=" * 60)
print()

# Carregar anomalias
anomalies_file = Path("outputs/anomalies_only.csv")

if not anomalies_file.exists():
    print(f"[ERRO] Arquivo não encontrado: {anomalies_file}")
    print("Execute primeiro: py detect_anomalies_example.py")
    sys.exit(1)

anomalies = pd.read_csv(anomalies_file)
anomalies['data'] = pd.to_datetime(anomalies['data']) if 'data' in anomalies.columns else None

print(f"Total de anomalias: {len(anomalies)}")
print()

# Preparar dados da tabela
table_data = create_anomaly_table_data(anomalies, max_rows=50)

# Exibir tabela formatada
print("=" * 120)
print("TABELA DE ANOMALIAS (Top 50 por Score)")
print("=" * 120)
print()

# Cabeçalho
header = table_data[0]
print(f"{'Data':<12} | {'Produto':<12} | {'Consumo':<12} | {'Estoque':<15} | {'Score':<10}")
print("-" * 120)

# Dados
for row in table_data[1:]:
    if len(row) >= 5:
        print(f"{row[0]:<12} | {row[1]:<12} | {row[2]:<12} | {row[3]:<15} | {row[4]:<10}")

print()
print("=" * 120)
print(f"Total de linhas na tabela: {len(table_data) - 1}")
print("=" * 120)

# Estatísticas da tabela
print()
print("ESTATÍSTICAS DAS ANOMALIAS NA TABELA:")
print("-" * 60)

if len(anomalies) > 0:
    top_50 = anomalies.nlargest(50, 'anomaly_score')
    
    print(f"Score mínimo: {top_50['anomaly_score'].min():.4f}")
    print(f"Score máximo: {top_50['anomaly_score'].max():.4f}")
    print(f"Score médio: {top_50['anomaly_score'].mean():.4f}")
    print()
    
    print("Produtos mais frequentes (top 5):")
    print(top_50['produto_id'].value_counts().head(5).to_string())
    print()
    
    print("Datas com mais anomalias (top 5):")
    if 'data' in top_50.columns:
        top_50['data'] = pd.to_datetime(top_50['data'])
        print(top_50.groupby(top_50['data'].dt.date).size().sort_values(ascending=False).head(5).to_string())

