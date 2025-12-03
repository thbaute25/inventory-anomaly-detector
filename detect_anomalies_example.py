"""
Script de exemplo para detectar anomalias em consumo e estoque.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import load_inventory_data
from src.data_aggregator import aggregate_daily_by_item
from src.anomalies import detect_anomalies_consumo_estoque, save_anomaly_model
from src.data_cleaning import save_processed

print("=" * 60)
print("DETECÇÃO DE ANOMALIAS - Inventory Anomaly Detector")
print("=" * 60)
print()

# 1. Carregar dados
print("1. Carregando dados...")
print("-" * 60)
df = load_inventory_data()
print()

# 2. Agregar dados diários por item
print("2. Agregando dados diários por item...")
print("-" * 60)
df_aggregated = aggregate_daily_by_item(df, fill_missing_dates=False)
print()

# 3. Detectar anomalias
print("3. Detectando anomalias com Isolation Forest...")
print("-" * 60)
df_with_anomalies, anomaly_model = detect_anomalies_consumo_estoque(
    df_aggregated,
    consumo_column="consumo_mean",
    estoque_column="estoque_mean",
    contamination=0.1
)
print()

# 4. Análise das anomalias
print("4. Análise das anomalias detectadas...")
print("-" * 60)
anomalies = df_with_anomalies[df_with_anomalies["is_anomaly"]]

if len(anomalies) > 0:
    print(f"\nTotal de anomalias: {len(anomalies)}")
    print(f"\nAnomalias por produto:")
    print(anomalies.groupby("produto_id").size().sort_values(ascending=False))
    
    print(f"\nTop 10 anomalias (maior score):")
    top_anomalies = anomalies.nlargest(10, "anomaly_score")
    print(top_anomalies[["produto_id", "data", "consumo_mean", "estoque_mean", "anomaly_score"]].to_string(index=False))
    
    print(f"\nEstatísticas dos scores de anomalia:")
    print(f"  - Mínimo: {anomalies['anomaly_score'].min():.4f}")
    print(f"  - Máximo: {anomalies['anomaly_score'].max():.4f}")
    print(f"  - Média: {anomalies['anomaly_score'].mean():.4f}")
    print(f"  - Mediana: {anomalies['anomaly_score'].median():.4f}")
else:
    print("Nenhuma anomalia detectada.")

print()

# 5. Salvar modelo e resultados
print("5. Salvando modelo e resultados...")
print("-" * 60)

# Salvar modelo
model_path = Path("outputs/models/isolation_forest_model.pkl.gz")
save_anomaly_model(anomaly_model, model_path, compress=True)

# Salvar resultados completos em CSV e Parquet
output_path_csv = Path("outputs/anomalies_detected.csv")
save_processed(df_with_anomalies, output_path_csv, format="csv")

output_path_parquet = Path("outputs/anomalies_detected.parquet")
save_processed(df_with_anomalies, output_path_parquet, format="parquet", compress=True)

# Salvar apenas anomalias em CSV e Parquet
if len(anomalies) > 0:
    anomalies_csv = Path("outputs/anomalies_only.csv")
    save_processed(anomalies, anomalies_csv, format="csv")
    
    anomalies_parquet = Path("outputs/anomalies_only.parquet")
    save_processed(anomalies, anomalies_parquet, format="parquet", compress=True)
    
    print(f"   [OK] Apenas anomalias salvas em CSV e Parquet")

print(f"   [OK] Todos os dados salvos em CSV e Parquet")
print()

# 6. Resumo
print("=" * 60)
print("RESUMO")
print("=" * 60)
print(f"Total de registros analisados: {len(df_with_anomalies)}")
print(f"Anomalias detectadas: {len(anomalies)} ({len(anomalies)/len(df_with_anomalies)*100:.2f}%)")
print(f"Modelo salvo em: {model_path}")
print(f"Resultados salvos em CSV: {output_path_csv}")
print(f"Resultados salvos em Parquet: {output_path_parquet}")
print("=" * 60)

