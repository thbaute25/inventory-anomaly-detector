"""
Script de teste para verificar o funcionamento do pipeline até o momento.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("TESTE DO PIPELINE - Inventory Anomaly Detector")
print("=" * 60)
print()

# 1. Gerar dados fake se não existirem
print("1. Gerando dados fake...")
print("-" * 60)
try:
    from generate_fake_data import generate_fake_inventory_data
    
    data_file = Path("data/inventory_data.csv")
    if not data_file.exists():
        print("   Arquivo de dados não encontrado. Gerando dados fake...")
        generate_fake_inventory_data()
    else:
        print(f"   Arquivo de dados já existe: {data_file}")
    print("   [OK] Dados fake gerados/verificados")
except Exception as e:
    print(f"   [ERRO] Erro ao gerar dados: {e}")
    sys.exit(1)

print()

# 2. Carregar dados completos
print("2. Carregando dados completos...")
print("-" * 60)
try:
    from src.data_loader import load_inventory_data, validate_data
    from src.config import DATE_COLUMN, PRODUCT_COLUMN
    
    df = load_inventory_data()
    validate_data(df)
    print("   [OK] Dados carregados e validados")
except Exception as e:
    print(f"   [ERRO] Erro ao carregar dados: {e}")
    sys.exit(1)

print()

# 3. Carregar dados de consumo
print("3. Carregando dados de consumo...")
print("-" * 60)
try:
    from src.data_loader import load_raw_consumo
    
    consumo_df = load_raw_consumo()
    print(f"   [OK] Dados de consumo carregados: {len(consumo_df)} registros")
except Exception as e:
    print(f"   [ERRO] Erro ao carregar consumo: {e}")
    sys.exit(1)

print()

# 4. Limpar dados de consumo
print("4. Limpando dados de consumo...")
print("-" * 60)
try:
    from src.data_cleaning import clean_consumo
    
    consumo_limpo = clean_consumo(
        consumo_df,
        remove_outliers=True,
        fill_missing=True,
        fill_method="interpolate"
    )
    print(f"   [OK] Dados limpos: {len(consumo_limpo)} registros")
except Exception as e:
    print(f"   [ERRO] Erro ao limpar dados: {e}")
    sys.exit(1)

print()

# 5. Criar features de lag
print("5. Criando features de lag...")
print("-" * 60)
try:
    from src.features import create_lag_features
    
    # Adicionar produto_id ao DataFrame se não existir
    if "produto_id" not in consumo_limpo.columns:
        # Pegar produto_id do DataFrame original
        consumo_limpo = consumo_limpo.merge(
            df[[DATE_COLUMN, PRODUCT_COLUMN]].drop_duplicates(),
            left_on="ds",
            right_on=DATE_COLUMN,
            how="left"
        )
        consumo_limpo = consumo_limpo.drop(columns=[DATE_COLUMN])
    
    consumo_com_lags = create_lag_features(
        consumo_limpo,
        value_column="y",
        group_by="produto_id" if "produto_id" in consumo_limpo.columns else None
    )
    
    # Mostrar algumas features criadas
    lag_cols = [col for col in consumo_com_lags.columns if "lag" in col]
    print(f"   [OK] Features de lag criadas: {len(lag_cols)} features")
    print(f"   - Features: {lag_cols}")
    print(f"   - Exemplo de valores:")
    print(consumo_com_lags[["ds", "y"] + lag_cols[:2]].head(10).to_string(index=False))
except Exception as e:
    print(f"   [ERRO] Erro ao criar features de lag: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 6. Criar agregados diários por item
print("6. Criando agregados diários por item...")
print("-" * 60)
try:
    from src.data_aggregator import aggregate_daily_by_item
    
    # Agregar dados por produto e data
    df_aggregated = aggregate_daily_by_item(
        df,
        fill_missing_dates=False
    )
    
    print(f"   [OK] Agregados criados: {len(df_aggregated)} registros")
    print(f"   - Colunas agregadas: {list(df_aggregated.columns)}")
    print(f"   - Exemplo de dados agregados:")
    print(df_aggregated.head(10).to_string(index=False))
    
    # Salvar agregados
    from src.data_cleaning import save_processed
    output_path_agg = Path("outputs/daily_aggregated_by_item.csv")
    save_processed(df_aggregated, output_path_agg, format="csv")
    print(f"   [OK] Agregados salvos em: {output_path_agg}")
except Exception as e:
    print(f"   [ERRO] Erro ao criar agregados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 7. Salvar dados processados
print("7. Salvando dados processados...")
print("-" * 60)
try:
    from src.data_cleaning import save_processed
    
    output_path = Path("outputs/processed_consumo.csv")
    save_processed(consumo_limpo, output_path, format="csv")
    
    # Salvar também dados com features
    output_path_features = Path("outputs/consumo_with_features.csv")
    save_processed(consumo_com_lags, output_path_features, format="csv")
    print("   [OK] Dados processados salvos")
except Exception as e:
    print(f"   [ERRO] Erro ao salvar dados: {e}")
    sys.exit(1)

print()

# 8. Treinar modelos Prophet para cada produto
print("8. Treinando modelos Prophet para cada produto...")
print("-" * 60)
try:
    from src.forecasting import train_models_by_product
    
    # Preparar dados de consumo com produto_id para treinamento
    # Usar dados limpos mas com produto_id
    consumo_para_treino = consumo_limpo.copy()
    
    # Adicionar produto_id se não existir
    if "produto_id" not in consumo_para_treino.columns:
        # Pegar produto_id do DataFrame original usando merge
        consumo_para_treino = consumo_para_treino.merge(
            df[[DATE_COLUMN, PRODUCT_COLUMN]].drop_duplicates(),
            left_on="ds",
            right_on=DATE_COLUMN,
            how="left"
        )
        consumo_para_treino = consumo_para_treino.drop(columns=[DATE_COLUMN])
    
    # Remover linhas sem produto_id (se houver)
    consumo_para_treino = consumo_para_treino.dropna(subset=["produto_id"])
    
    # Treinar modelos para cada produto
    prophet_models = train_models_by_product(
        consumo_para_treino,
        product_column="produto_id",
        save_models=True
    )
    
    print(f"   [OK] Modelos treinados: {len(prophet_models)} modelos")
    print(f"   - Produtos: {list(prophet_models.keys())}")
    
    # Fazer previsão para os próximos 7 dias para cada produto
    from src.forecasting import forecast_7_days_by_product
    forecast_7d = forecast_7_days_by_product(prophet_models)
    
    # Fazer previsão para os próximos 30 dias para cada produto
    from src.forecasting import forecast_by_product
    forecast_30d = forecast_by_product(prophet_models, periods=30, freq="D")
    
    # Salvar previsões
    from src.data_cleaning import save_processed
    output_path_forecast_7d = Path("outputs/forecast_7d.csv")
    save_processed(forecast_7d, output_path_forecast_7d, format="csv")
    print(f"   [OK] Previsões para 7 dias geradas e salvas")
    
    output_path_forecast_30d = Path("outputs/forecast_30d.csv")
    save_processed(forecast_30d, output_path_forecast_30d, format="csv")
    print(f"   [OK] Previsões para 30 dias geradas e salvas")
    
except Exception as e:
    print(f"   [ERRO] Erro ao treinar modelos Prophet: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 9. Treinar Isolation Forest e detectar anomalias
print("9. Treinando Isolation Forest e detectando anomalias...")
print("-" * 60)
try:
    from src.anomalies import detect_anomalies_consumo_estoque, save_anomaly_model
    
    # Detectar anomalias nos dados agregados
    df_with_anomalies, anomaly_model = detect_anomalies_consumo_estoque(
        df_aggregated,
        consumo_column="consumo_mean",
        estoque_column="estoque_mean",
        contamination=0.1
    )
    
    # Filtrar apenas anomalias
    anomalies = df_with_anomalies[df_with_anomalies["is_anomaly"]]
    print(f"   [OK] Anomalias detectadas: {len(anomalies)}")
    
    if len(anomalies) > 0:
        print(f"   - Exemplo de anomalias:")
        print(anomalies[["produto_id", "data", "consumo_mean", "estoque_mean", "anomaly_score"]].head(5).to_string(index=False))
    
    # Salvar modelo de anomalias
    model_path = Path("outputs/models/isolation_forest_model.pkl.gz")
    save_anomaly_model(anomaly_model, model_path, compress=True)
    
    # Salvar resultados em CSV e Parquet
    from src.data_cleaning import save_processed
    
    # Salvar CSV
    output_path_csv = Path("outputs/anomalies_detected.csv")
    save_processed(df_with_anomalies, output_path_csv, format="csv")
    
    # Salvar Parquet (mais eficiente para grandes volumes)
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
    
    # Exemplo de envio de alertas (descomente e configure webhooks para usar)
    # from src.alerts import send_anomaly_alerts
    # send_anomaly_alerts(
    #     df_with_anomalies,
    #     send_discord=False,  # Configure webhook no config.py primeiro
    #     send_teams=False     # Configure webhook no config.py primeiro
    # )
    
except Exception as e:
    print(f"   [ERRO] Erro ao detectar anomalias: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 10. Resumo final
print("=" * 60)
print("RESUMO DO TESTE")
print("=" * 60)
print(f"[OK] Dados originais: {len(df)} registros")
print(f"[OK] Dados de consumo: {len(consumo_df)} registros")
print(f"[OK] Dados limpos: {len(consumo_limpo)} registros")
print(f"[OK] Features de lag criadas: {len([col for col in consumo_com_lags.columns if 'lag' in col])} features")
print(f"[OK] Agregados diários por item: {len(df_aggregated)} registros")
print(f"[OK] Modelos Prophet treinados: {len(prophet_models)} modelos")
print(f"[OK] Isolation Forest treinado e anomalias detectadas")
print(f"[OK] Arquivo processado salvo em: outputs/processed_consumo.csv")
print(f"[OK] Arquivo com features salvo em: outputs/consumo_with_features.csv")
print(f"[OK] Arquivo agregados salvo em: outputs/daily_aggregated_by_item.csv")
print(f"[OK] Previsões 7 dias salvas em: outputs/forecast_7d.csv")
print(f"[OK] Previsões 30 dias salvas em: outputs/forecast_30d.csv")
print(f"[OK] Anomalias salvas em CSV e Parquet: outputs/anomalies_detected.*")
print()
print("Pipeline funcionando corretamente até este ponto!")
print("=" * 60)

