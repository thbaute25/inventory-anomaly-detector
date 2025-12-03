"""Script para mostrar resultados do pipeline"""
import pandas as pd
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print("\n" + "="*60)
print("RESULTADOS DO PIPELINE - Inventory Anomaly Detector")
print("="*60)

# Carregar anomalias
df_anomalies = pd.read_csv('outputs/anomalies_only.csv')
df_all = pd.read_csv('outputs/anomalies_detected.csv')

print(f"\nESTATISTICAS GERAIS:")
print(f"  - Total de registros analisados: {len(df_all):,}")
print(f"  - Anomalias detectadas: {len(df_anomalies):,} ({len(df_anomalies)/len(df_all)*100:.2f}%)")
print(f"  - Score medio das anomalias: {df_anomalies['anomaly_score'].mean():.4f}")
print(f"  - Score maximo: {df_anomalies['anomaly_score'].max():.4f}")
print(f"  - Score minimo: {df_anomalies['anomaly_score'].min():.4f}")

print(f"\nANOMALIAS POR PRODUTO:")
print(df_anomalies['produto_id'].value_counts().to_string())

print(f"\nTOP 10 ANOMALIAS MAIS CRITICAS:")
top_anomalies = df_anomalies.nlargest(10, 'anomaly_score')[
    ['data', 'produto_id', 'consumo_mean', 'estoque_mean', 'anomaly_score']
]
print(top_anomalies.to_string(index=False))

print(f"\nARQUIVOS GERADOS:")
print(f"  - Anomalias completas: outputs/anomalies_detected.csv ({len(df_all):,} registros)")
print(f"  - Apenas anomalias: outputs/anomalies_only.csv ({len(df_anomalies):,} registros)")
print(f"  - Relatorio PDF: outputs/reports/anomaly_report_*.pdf")
print(f"  - Modelos Prophet: outputs/models/prophet_model_*.pkl.gz (5 modelos)")
print(f"  - Modelo Isolation Forest: outputs/models/isolation_forest_model.pkl.gz")

print("\n" + "="*60)
print("Pipeline executado com sucesso!")
print("="*60 + "\n")

