"""
Script de teste para gerar relatório PDF de anomalias.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.reports import generate_report_from_file, generate_anomaly_report_pdf
import pandas as pd

print("=" * 60)
print("GERAÇÃO DE RELATÓRIO PDF - Inventory Anomaly Detector")
print("=" * 60)
print()

# Verificar se arquivo de anomalias existe
anomalies_file = Path("outputs/anomalies_detected.csv")

if not anomalies_file.exists():
    print(f"[ERRO] Arquivo não encontrado: {anomalies_file}")
    print("Execute primeiro: py detect_anomalies_example.py")
    sys.exit(1)

print("1. Carregando dados...")
print("-" * 60)

# Carregar dados
df_all = pd.read_csv(anomalies_file)
df_all['data'] = pd.to_datetime(df_all['data']) if 'data' in df_all.columns else None

# Separar anomalias
if 'is_anomaly' in df_all.columns:
    anomalies = df_all[df_all['is_anomaly'] == True].copy()
else:
    anomalies = df_all.copy()

print(f"   [OK] Total de registros: {len(df_all)}")
print(f"   [OK] Anomalias detectadas: {len(anomalies)}")
print()

# Gerar relatório
print("2. Gerando relatório PDF...")
print("-" * 60)

try:
    output_path = Path("outputs/reports/anomaly_report.pdf")
    
    pdf_path = generate_anomaly_report_pdf(
        df_all,
        anomalies,
        output_path=output_path,
        title="Relatório de Anomalias em Estoque e Consumo",
        include_charts=True
    )
    
    print()
    print("=" * 60)
    print("SUCESSO!")
    print("=" * 60)
    print(f"Relatório PDF gerado: {pdf_path}")
    print(f"Tamanho do arquivo: {pdf_path.stat().st_size / (1024*1024):.2f} MB")
    print()
    print("O relatório inclui:")
    print("  - Resumo executivo")
    print("  - Gráficos de anomalias")
    print("  - Tabela detalhada das anomalias")
    print("=" * 60)
    
except Exception as e:
    print(f"[ERRO] Erro ao gerar relatório: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

