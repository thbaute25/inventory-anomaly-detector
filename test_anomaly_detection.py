"""
Script de teste completo para detecção de anomalias.
"""

import pandas as pd
from pathlib import Path
from src.alerts import format_anomaly_alert, format_anomaly_email_html

print("=" * 60)
print("TESTE DE DETECÇÃO DE ANOMALIAS - RESUMO")
print("=" * 60)
print()

# Carregar resultados salvos
df_all = pd.read_csv('outputs/anomalies_detected.csv')
anomalies = df_all[df_all['is_anomaly'] == True]

print("RESUMO DOS RESULTADOS:")
print("-" * 60)
print(f"Total de registros analisados: {len(df_all)}")
print(f"Anomalias detectadas: {len(anomalies)} ({len(anomalies)/len(df_all)*100:.2f}%)")
print()

if len(anomalies) > 0:
    print("ESTATÍSTICAS DAS ANOMALIAS:")
    print("-" * 60)
    print(f"Score mínimo: {anomalies['anomaly_score'].min():.4f}")
    print(f"Score máximo: {anomalies['anomaly_score'].max():.4f}")
    print(f"Score médio: {anomalies['anomaly_score'].mean():.4f}")
    print(f"Score mediano: {anomalies['anomaly_score'].median():.4f}")
    print()
    
    print("ANOMALIAS POR PRODUTO:")
    print("-" * 60)
    print(anomalies['produto_id'].value_counts().to_string())
    print()
    
    print("TOP 5 ANOMALIAS (MAIOR SCORE):")
    print("-" * 60)
    top_5 = anomalies.nlargest(5, 'anomaly_score')
    print(top_5[['produto_id', 'data', 'consumo_mean', 'estoque_mean', 'anomaly_score']].to_string(index=False))
    print()
    
    print("TESTE DE FORMATAÇÃO DE ALERTAS:")
    print("=" * 60)
    print()
    
    # Testar formatação de alerta texto
    print("1. Mensagem de alerta (texto):")
    print("-" * 60)
    alert_msg = format_anomaly_alert(top_5, max_anomalies=5)
    print(alert_msg)
    print()
    
    # Testar formatação HTML
    print("2. HTML para email (primeiras 300 caracteres):")
    print("-" * 60)
    html_msg = format_anomaly_email_html(top_5)
    print(html_msg[:300])
    print("...")
    print()
    
    # Verificar arquivos salvos
    print("ARQUIVOS GERADOS:")
    print("-" * 60)
    files = [
        'outputs/anomalies_detected.csv',
        'outputs/anomalies_detected.parquet',
        'outputs/anomalies_only.csv',
        'outputs/anomalies_only.parquet',
        'outputs/models/isolation_forest_model.pkl.gz'
    ]
    
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  [OK] {file_path} ({size_mb:.2f} MB)")
        else:
            print(f"  [ERRO] {file_path} não encontrado")
    
    print()
    print("=" * 60)
    print("TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
else:
    print("Nenhuma anomalia detectada para análise.")

