"""
Pipeline Prefect para detecção de anomalias em estoque e consumo.
Orquestra todas as etapas: carregamento, limpeza, features, modelos e alertas.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import sys

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta

# Imports dos módulos do projeto
from src.data_loader import load_inventory_data, load_raw_consumo, validate_data
from src.data_cleaning import clean_consumo, save_processed
from src.data_aggregator import aggregate_daily_by_item
from src.features import create_lag_features
from src.forecasting import train_models_by_product, forecast_7_days_by_product
from src.anomalies import detect_anomalies_consumo_estoque, save_anomaly_model
from src.alerts import send_anomaly_alerts, send_anomaly_alert_by_product
from src.reports import generate_anomaly_report_pdf
from src.config import (
    DATA_FILE,
    MODELS_DIR,
    REPORT_OUTPUT_DIR,
    PREFECT_CONFIG,
    ALERT_CONFIG,
    DATE_COLUMN,
    PRODUCT_COLUMN
)


@task(name="load_data", retries=PREFECT_CONFIG["retries"], retry_delay_seconds=PREFECT_CONFIG["retry_delay_seconds"])
def task_load_data(data_file: Optional[Path] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Task para carregar dados de estoque e consumo.
    
    Args:
        data_file: Caminho do arquivo CSV. Se None, usa config padrão.
    
    Returns:
        Tupla (DataFrame completo, DataFrame de consumo).
    """
    logger = get_run_logger()
    
    if data_file is None:
        data_file = DATA_FILE
    
    logger.info(f"Carregando dados de: {data_file}")
    
    # Carregar dados completos
    df = load_inventory_data(data_file)
    validate_data(df)
    
    # Carregar dados de consumo
    consumo_df = load_raw_consumo(data_file)
    
    logger.info(f"Dados carregados: {len(df)} registros completos, {len(consumo_df)} registros de consumo")
    
    return df, consumo_df


@task(name="clean_data", retries=PREFECT_CONFIG["retries"], retry_delay_seconds=PREFECT_CONFIG["retry_delay_seconds"])
def task_clean_data(consumo_df: pd.DataFrame) -> pd.DataFrame:
    """
    Task para limpar dados de consumo.
    
    Args:
        consumo_df: DataFrame com dados de consumo.
    
    Returns:
        DataFrame limpo.
    """
    logger = get_run_logger()
    
    logger.info("Limpando dados de consumo...")
    
    consumo_limpo = clean_consumo(
        consumo_df,
        remove_outliers=True,
        fill_missing=True,
        fill_method="interpolate"
    )
    
    logger.info(f"Dados limpos: {len(consumo_limpo)} registros")
    
    return consumo_limpo


@task(name="create_features", retries=PREFECT_CONFIG["retries"], retry_delay_seconds=PREFECT_CONFIG["retry_delay_seconds"])
def task_create_features(consumo_limpo: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Task para criar features de lag.
    
    Args:
        consumo_limpo: DataFrame com dados de consumo limpos.
        df: DataFrame completo para obter produto_id.
    
    Returns:
        DataFrame com features criadas.
    """
    logger = get_run_logger()
    
    logger.info("Criando features de lag...")
    
    # Adicionar produto_id se não existir
    if "produto_id" not in consumo_limpo.columns:
        consumo_limpo = consumo_limpo.merge(
            df[[DATE_COLUMN, PRODUCT_COLUMN]].drop_duplicates(),
            left_on="ds",
            right_on=DATE_COLUMN,
            how="left"
        )
        consumo_limpo = consumo_limpo.drop(columns=[DATE_COLUMN])
    
    # Criar features de lag
    consumo_com_features = create_lag_features(
        consumo_limpo,
        value_column="y",  # Coluna de valores (consumo)
        group_by="produto_id",
        lags=[1, 7, 30]
    )
    
    logger.info(f"Features criadas: {len([col for col in consumo_com_features.columns if 'lag' in col])} features de lag")
    
    return consumo_com_features


@task(name="aggregate_data", retries=PREFECT_CONFIG["retries"], retry_delay_seconds=PREFECT_CONFIG["retry_delay_seconds"])
def task_aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Task para agregar dados diários por item.
    
    Args:
        df: DataFrame completo.
    
    Returns:
        DataFrame agregado.
    """
    logger = get_run_logger()
    
    logger.info("Agregando dados diários por item...")
    
    df_aggregated = aggregate_daily_by_item(df, fill_missing_dates=False)
    
    logger.info(f"Dados agregados: {len(df_aggregated)} registros")
    
    return df_aggregated


@task(name="train_prophet_models", retries=PREFECT_CONFIG["retries"], retry_delay_seconds=PREFECT_CONFIG["retry_delay_seconds"])
def task_train_prophet_models(consumo_com_features: pd.DataFrame) -> Dict[str, any]:
    """
    Task para treinar modelos Prophet.
    
    Args:
        consumo_com_features: DataFrame com features criadas.
    
    Returns:
        Dicionário com modelos Prophet treinados.
    """
    logger = get_run_logger()
    
    logger.info("Treinando modelos Prophet...")
    
    prophet_models = train_models_by_product(
        consumo_com_features,
        product_column="produto_id",
        save_models=True
    )
    
    logger.info(f"Modelos Prophet treinados: {len(prophet_models)} modelos")
    
    # Fazer previsões de 7 dias
    forecast_7d = forecast_7_days_by_product(prophet_models)
    
    # Salvar previsões
    output_path_forecast_7d = Path("outputs/forecast_7d.csv")
    save_processed(forecast_7d, output_path_forecast_7d, format="csv")
    
    logger.info(f"Previsões de 7 dias salvas em: {output_path_forecast_7d}")
    
    return prophet_models


@task(name="detect_anomalies", retries=PREFECT_CONFIG["retries"], retry_delay_seconds=PREFECT_CONFIG["retry_delay_seconds"])
def task_detect_anomalies(df_aggregated: pd.DataFrame) -> Tuple[pd.DataFrame, any]:
    """
    Task para detectar anomalias usando Isolation Forest.
    
    Args:
        df_aggregated: DataFrame agregado.
    
    Returns:
        Tupla (DataFrame com anomalias, modelo treinado).
    """
    logger = get_run_logger()
    
    logger.info("Detectando anomalias com Isolation Forest...")
    
    df_with_anomalies, anomaly_model = detect_anomalies_consumo_estoque(
        df_aggregated,
        consumo_column="consumo_mean",
        estoque_column="estoque_mean",
        contamination=0.1
    )
    
    anomalies = df_with_anomalies[df_with_anomalies["is_anomaly"]]
    
    logger.info(f"Anomalias detectadas: {len(anomalies)} ({len(anomalies)/len(df_with_anomalies)*100:.2f}%)")
    
    # Salvar modelo
    model_path = MODELS_DIR / "isolation_forest_model.pkl.gz"
    save_anomaly_model(anomaly_model, model_path, compress=True)
    
    # Salvar resultados
    output_path_all = Path("outputs/anomalies_detected.csv")
    save_processed(df_with_anomalies, output_path_all, format="csv")
    
    output_path_parquet = Path("outputs/anomalies_detected.parquet")
    save_processed(df_with_anomalies, output_path_parquet, format="parquet", compress=True)
    
    if len(anomalies) > 0:
        output_path_anomalies = Path("outputs/anomalies_only.csv")
        save_processed(anomalies, output_path_anomalies, format="csv")
        
        output_path_anomalies_parquet = Path("outputs/anomalies_only.parquet")
        save_processed(anomalies, output_path_anomalies_parquet, format="parquet", compress=True)
    
    logger.info(f"Resultados salvos em CSV e Parquet")
    
    return df_with_anomalies, anomaly_model


@task(name="send_alerts", retries=1, retry_delay_seconds=30)
def task_send_alerts(df_with_anomalies: pd.DataFrame, send_email: bool = False) -> Dict[str, bool]:
    """
    Task para enviar alertas de anomalias.
    
    Args:
        df_with_anomalies: DataFrame com anomalias detectadas.
        send_email: Se True, envia alertas por email.
    
    Returns:
        Dicionário com resultados do envio.
    """
    logger = get_run_logger()
    
    anomalies = df_with_anomalies[df_with_anomalies["is_anomaly"]]
    
    if len(anomalies) == 0:
        logger.info("Nenhuma anomalia detectada. Nenhum alerta enviado.")
        return {"discord": False, "teams": False, "email": False}
    
    # Filtrar apenas anomalias com score alto
    min_score = ALERT_CONFIG.get("min_anomaly_score", 0.7)
    high_score_anomalies = anomalies[anomalies["anomaly_score"] >= min_score]
    
    if len(high_score_anomalies) == 0:
        logger.info(f"Nenhuma anomalia acima do score mínimo ({min_score}). Nenhum alerta enviado.")
        return {"discord": False, "teams": False, "email": False}
    
    logger.info(f"Enviando alertas para {len(high_score_anomalies)} anomalias críticas...")
    
    results = {}
    
    # Enviar alertas agrupados
    results_all = send_anomaly_alerts(
        high_score_anomalies,
        produto_id="TODOS",
        min_score=min_score,
        send_discord=bool(ALERT_CONFIG.get("discord_webhook_url")),
        send_teams=bool(ALERT_CONFIG.get("teams_webhook_url"))
    )
    
    results.update(results_all)
    
    # Enviar email se configurado
    if send_email:
        from src.alerts import send_email_alert, format_anomaly_alert, format_anomaly_email_html
        
        text_message = format_anomaly_alert(high_score_anomalies.head(20), max_anomalies=20)
        html_message = format_anomaly_email_html(high_score_anomalies.head(20))
        
        email_result = send_email_alert(
            subject="Alerta de Anomalias - Inventory Anomaly Detector",
            message=text_message,
            html_message=html_message
        )
        
        results["email"] = email_result
    else:
        results["email"] = False
    
    logger.info(f"Alertas enviados: {results}")
    
    return results


@task(name="generate_report", retries=1, retry_delay_seconds=30)
def task_generate_report(df_with_anomalies: pd.DataFrame) -> Path:
    """
    Task para gerar relatório PDF.
    
    Args:
        df_with_anomalies: DataFrame com anomalias detectadas.
    
    Returns:
        Caminho do arquivo PDF gerado.
    """
    logger = get_run_logger()
    
    anomalies = df_with_anomalies[df_with_anomalies["is_anomaly"]]
    
    logger.info("Gerando relatório PDF...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = REPORT_OUTPUT_DIR / f"anomaly_report_{timestamp}.pdf"
    
    pdf_path = generate_anomaly_report_pdf(
        df_with_anomalies,
        anomalies,
        output_path=output_path,
        title="Relatório de Anomalias em Estoque e Consumo",
        include_charts=True
    )
    
    logger.info(f"Relatório PDF gerado: {pdf_path}")
    
    return pdf_path


@flow(name=PREFECT_CONFIG["flow_name"], log_prints=True)
def inventory_anomaly_detection_flow(
    data_file: Optional[Path] = None,
    send_alerts: bool = True,
    send_email: bool = False,
    generate_pdf_report: bool = True
) -> Dict[str, any]:
    """
    Flow principal do pipeline de detecção de anomalias.
    
    Orquestra todas as etapas na ordem:
    1. LOAD: Carregar dados de estoque e consumo
    2. CLEAN: Limpar e preparar dados
    3. FEATURES: Criar features de série temporal (lags)
    4. FORECAST: Treinar modelos Prophet e fazer previsões
    5. ANOMALIES: Detectar anomalias com Isolation Forest
    6. ALERTS: Enviar alertas (opcional)
    7. PDF: Gerar relatório PDF (opcional)
    
    Args:
        data_file: Caminho do arquivo CSV. Se None, usa config padrão.
        send_alerts: Se True, envia alertas de anomalias.
        send_email: Se True, envia alertas por email.
        generate_pdf_report: Se True, gera relatório PDF.
    
    Returns:
        Dicionário com resultados do pipeline.
    """
    logger = get_run_logger()
    
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE DE DETECÇÃO DE ANOMALIAS")
    logger.info("=" * 60)
    
    # Pipeline: load → clean → features → forecast → anomalies → alerts → pdf
    
    # 1. LOAD: Carregar dados
    df, consumo_df = task_load_data(data_file)
    
    # 2. CLEAN: Limpar dados
    consumo_limpo = task_clean_data(consumo_df)
    
    # 3. FEATURES: Criar features de série temporal
    consumo_com_features = task_create_features(consumo_limpo, df)
    
    # 4. AGGREGATE: Agregar dados diários (necessário para anomalias)
    df_aggregated = task_aggregate_data(df)
    
    # 5. FORECAST: Treinar modelos Prophet e fazer previsões
    prophet_models = task_train_prophet_models(consumo_com_features)
    
    # 6. ANOMALIES: Detectar anomalias com Isolation Forest
    df_with_anomalies, anomaly_model = task_detect_anomalies(df_aggregated)
    
    # 7. ALERTS: Enviar alertas (se habilitado)
    alert_results = {}
    if send_alerts:
        alert_results = task_send_alerts(df_with_anomalies, send_email=send_email)
    
    # 8. PDF: Gerar relatório PDF (se habilitado)
    pdf_path = None
    if generate_pdf_report:
        pdf_path = task_generate_report(df_with_anomalies)
    
    # Resumo final
    anomalies = df_with_anomalies[df_with_anomalies["is_anomaly"]]
    
    results = {
        "total_records": len(df_with_anomalies),
        "anomalies_detected": len(anomalies),
        "anomaly_percentage": len(anomalies) / len(df_with_anomalies) * 100 if len(df_with_anomalies) > 0 else 0,
        "prophet_models_trained": len(prophet_models),
        "alert_results": alert_results,
        "pdf_report_path": str(pdf_path) if pdf_path else None,
        "anomalies_file": "outputs/anomalies_detected.csv",
        "anomalies_only_file": "outputs/anomalies_only.csv" if len(anomalies) > 0 else None
    }
    
    logger.info("=" * 60)
    logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
    logger.info("=" * 60)
    logger.info(f"Total de registros: {results['total_records']}")
    logger.info(f"Anomalias detectadas: {results['anomalies_detected']} ({results['anomaly_percentage']:.2f}%)")
    logger.info(f"Modelos Prophet treinados: {results['prophet_models_trained']}")
    logger.info(f"Alertas enviados: {alert_results}")
    if pdf_path:
        logger.info(f"Relatório PDF: {pdf_path}")
    
    return results


if __name__ == "__main__":
    # Executar pipeline localmente
    results = inventory_anomaly_detection_flow(
        data_file=None,  # Usar arquivo padrão
        send_alerts=True,
        send_email=False,  # Mudar para True para enviar email
        generate_pdf_report=True
    )
    
    print("\n" + "=" * 60)
    print("RESULTADOS DO PIPELINE")
    print("=" * 60)
    for key, value in results.items():
        print(f"{key}: {value}")

