"""
Módulo para previsão de consumo usando Prophet.
Treina modelos Prophet e faz previsões de séries temporais.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Optional, Dict, List
from pathlib import Path
import joblib

from src.config import PROPHET_CONFIG, MODELS_DIR


def train_prophet_model(
    df: pd.DataFrame,
    config: Optional[Dict] = None,
    product_id: Optional[str] = None
) -> Prophet:
    """
    Treina um modelo Prophet para previsão de consumo.
    
    Args:
        df: DataFrame com colunas 'ds' (data) e 'y' (consumo).
        config: Dicionário com configurações do Prophet. Se None, usa configuração padrão.
        product_id: ID do produto (apenas para logging).
    
    Returns:
        Modelo Prophet treinado.
    """
    if config is None:
        config = PROPHET_CONFIG.copy()
    
    # Verificar colunas necessárias
    if "ds" not in df.columns or "y" not in df.columns:
        raise ValueError("DataFrame deve conter colunas 'ds' (data) e 'y' (consumo)")
    
    # Preparar dados
    df_train = df[["ds", "y"]].copy()
    df_train = df_train.dropna(subset=["ds", "y"])
    df_train = df_train.sort_values("ds").reset_index(drop=True)
    
    if len(df_train) < 2:
        raise ValueError("Dados insuficientes para treinar o modelo. Mínimo de 2 registros necessário.")
    
    # Criar e treinar modelo
    model = Prophet(**config)
    
    print(f"Treinando modelo Prophet{' para ' + product_id if product_id else ''}...")
    print(f"  - Registros de treino: {len(df_train)}")
    print(f"  - Período: {df_train['ds'].min()} a {df_train['ds'].max()}")
    
    model.fit(df_train)
    
    print(f"  [OK] Modelo treinado com sucesso!")
    
    return model


def make_forecast(
    model: Prophet,
    periods: int = 30,
    freq: str = "D",
    include_history: bool = True
) -> pd.DataFrame:
    """
    Faz previsões usando um modelo Prophet treinado.
    
    Args:
        model: Modelo Prophet treinado.
        periods: Número de períodos a prever.
        freq: Frequência da previsão ('D' para diário, 'W' para semanal, etc.).
        include_history: Se True, inclui dados históricos na previsão.
    
    Returns:
        DataFrame com previsões (ds, yhat, yhat_lower, yhat_upper).
    """
    # Criar DataFrame futuro
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=include_history)
    
    # Fazer previsão
    forecast = model.predict(future)
    
    # Selecionar colunas relevantes
    forecast_cols = ["ds", "yhat", "yhat_lower", "yhat_upper"]
    forecast_result = forecast[forecast_cols].copy()
    
    print(f"Previsão gerada:")
    print(f"  - Períodos futuros: {periods}")
    print(f"  - Frequência: {freq}")
    print(f"  - Total de previsões: {len(forecast_result)}")
    
    return forecast_result


def forecast_7_days(
    model: Prophet,
    include_history: bool = False
) -> pd.DataFrame:
    """
    Faz previsão para os próximos 7 dias.
    Função de conveniência para previsão de 7 dias.
    
    Args:
        model: Modelo Prophet treinado.
        include_history: Se True, inclui dados históricos na previsão.
    
    Returns:
        DataFrame com previsões para 7 dias (ds, yhat, yhat_lower, yhat_upper).
    """
    return make_forecast(model, periods=7, freq="D", include_history=include_history)


def evaluate_model(
    model: Prophet,
    df_test: pd.DataFrame,
    metrics: Optional[List[str]] = None
) -> Dict[str, float]:
    """
    Avalia o desempenho do modelo Prophet usando dados de teste.
    
    Args:
        model: Modelo Prophet treinado.
        df_test: DataFrame de teste com colunas 'ds' e 'y'.
        metrics: Lista de métricas a calcular. Se None, usa métricas padrão.
    
    Returns:
        Dicionário com métricas de avaliação.
    """
    if metrics is None:
        metrics = ["mae", "mse", "rmse", "mape"]
    
    # Fazer previsão para dados de teste
    forecast = model.predict(df_test[["ds"]])
    
    # Calcular métricas
    y_true = df_test["y"].values
    y_pred = forecast["yhat"].values
    
    # Remover valores NaN
    mask = ~(np.isnan(y_true) | np.isnan(y_pred))
    y_true = y_true[mask]
    y_pred = y_pred[mask]
    
    if len(y_true) == 0:
        raise ValueError("Não há valores válidos para avaliação.")
    
    results = {}
    
    if "mae" in metrics:
        results["mae"] = np.mean(np.abs(y_true - y_pred))
    
    if "mse" in metrics:
        results["mse"] = np.mean((y_true - y_pred) ** 2)
    
    if "rmse" in metrics:
        results["rmse"] = np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    if "mape" in metrics:
        # Evitar divisão por zero
        mask_nonzero = y_true != 0
        if mask_nonzero.sum() > 0:
            results["mape"] = np.mean(np.abs((y_true[mask_nonzero] - y_pred[mask_nonzero]) / y_true[mask_nonzero])) * 100
        else:
            results["mape"] = np.nan
    
    print("Avaliação do modelo:")
    for metric, value in results.items():
        print(f"  - {metric.upper()}: {value:.4f}")
    
    return results


def save_model(
    model: Prophet,
    file_path: Path,
    compress: bool = True
) -> None:
    """
    Salva um modelo Prophet treinado.
    
    Args:
        model: Modelo Prophet treinado.
        file_path: Caminho para salvar o modelo (sem extensão ou com .pkl).
        compress: Se True, comprime o arquivo.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remover extensões existentes para evitar duplicação
    stem = file_path.stem  # Nome sem extensão
    if file_path.suffix == ".gz":
        # Se já tem .gz, pegar o stem do arquivo antes do .gz
        stem = file_path.with_suffix("").stem
    
    # Construir caminho final
    if compress:
        file_path = file_path.parent / f"{stem}.pkl.gz"
    else:
        file_path = file_path.parent / f"{stem}.pkl"
    
    try:
        with open(file_path, "wb") as f:
            joblib.dump(model, f, compress=("gzip", 3) if compress else None)
        
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        print(f"Modelo salvo com sucesso!")
        print(f"  - Arquivo: {file_path}")
        print(f"  - Tamanho: {file_size:.2f} MB")
    except Exception as e:
        raise IOError(f"Erro ao salvar modelo: {e}")


def load_model(file_path: Path) -> Prophet:
    """
    Carrega um modelo Prophet salvo.
    
    Args:
        file_path: Caminho do arquivo do modelo.
    
    Returns:
        Modelo Prophet carregado.
    """
    file_path = Path(file_path)
    
    # Tentar com e sem extensão .gz
    if not file_path.exists():
        if file_path.suffix == ".pkl":
            file_path = file_path.with_suffix(".pkl.gz")
        elif file_path.suffix == ".gz":
            file_path = file_path.with_suffix("").with_suffix(".pkl.gz")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo de modelo não encontrado: {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            model = joblib.load(f)
        
        print(f"Modelo carregado com sucesso: {file_path}")
        return model
    except Exception as e:
        raise IOError(f"Erro ao carregar modelo: {e}")


def train_models_by_product(
    df: pd.DataFrame,
    product_column: str = "produto_id",
    config: Optional[Dict] = None,
    save_models: bool = True,
    models_dir: Optional[Path] = None
) -> Dict[str, Prophet]:
    """
    Treina modelos Prophet separados para cada produto.
    
    Args:
        df: DataFrame com dados de múltiplos produtos.
        product_column: Nome da coluna de produto.
        config: Configurações do Prophet. Se None, usa configuração padrão.
        save_models: Se True, salva os modelos treinados.
        models_dir: Diretório para salvar modelos. Se None, usa diretório padrão.
    
    Returns:
        Dicionário com modelos treinados {produto_id: model}.
    """
    if product_column not in df.columns:
        raise ValueError(f"Coluna '{product_column}' não encontrada no DataFrame")
    
    if models_dir is None:
        models_dir = MODELS_DIR
    
    models_dir.mkdir(parents=True, exist_ok=True)
    
    products = df[product_column].unique()
    trained_models = {}
    
    print(f"Treinando modelos para {len(products)} produtos...")
    print("=" * 60)
    
    for product_id in products:
        try:
            # Filtrar dados do produto
            df_product = df[df[product_column] == product_id].copy()
            
            # Treinar modelo
            model = train_prophet_model(df_product, config=config, product_id=product_id)
            trained_models[product_id] = model
            
            # Salvar modelo se solicitado
            if save_models:
                model_path = models_dir / f"prophet_model_{product_id}"
                save_model(model, model_path, compress=True)
            
            print()
        except Exception as e:
            print(f"  [ERRO] Erro ao treinar modelo para {product_id}: {e}")
            print()
    
    print("=" * 60)
    print(f"Treinamento concluído: {len(trained_models)} modelos treinados")
    
    return trained_models


def forecast_by_product(
    models: Dict[str, Prophet],
    periods: int = 30,
    freq: str = "D"
) -> pd.DataFrame:
    """
    Faz previsões para múltiplos produtos usando modelos treinados.
    
    Args:
        models: Dicionário com modelos {produto_id: model}.
        periods: Número de períodos a prever.
        freq: Frequência da previsão.
    
    Returns:
        DataFrame com previsões de todos os produtos.
    """
    all_forecasts = []
    
    print(f"Gerando previsões para {len(models)} produtos...")
    
    for product_id, model in models.items():
        forecast = make_forecast(model, periods=periods, freq=freq, include_history=False)
        forecast["produto_id"] = product_id
        all_forecasts.append(forecast)
    
    df_forecasts = pd.concat(all_forecasts, ignore_index=True)
    
    # Reordenar colunas
    cols = ["produto_id", "ds", "yhat", "yhat_lower", "yhat_upper"]
    df_forecasts = df_forecasts[cols]
    
    print(f"  [OK] Previsões geradas: {len(df_forecasts)} registros")
    
    return df_forecasts


def forecast_7_days_by_product(
    models: Dict[str, Prophet]
) -> pd.DataFrame:
    """
    Faz previsão de 7 dias para múltiplos produtos.
    Função de conveniência para previsão de 7 dias por produto.
    
    Args:
        models: Dicionário com modelos {produto_id: model}.
    
    Returns:
        DataFrame com previsões de 7 dias para todos os produtos.
    """
    return forecast_by_product(models, periods=7, freq="D")

