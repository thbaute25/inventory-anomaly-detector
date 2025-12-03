"""
Módulo para criação de features de série temporal.
Cria lags, agregações e features temporais para modelagem.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict

from src.config import FEATURE_CONFIG


def create_lag_features(
    df: pd.DataFrame,
    value_column: str,
    lags: Optional[List[int]] = None,
    group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Cria features de lag (valores anteriores) para séries temporais.
    
    Args:
        df: DataFrame com coluna de data e valor.
        value_column: Nome da coluna com os valores para criar lags.
        lags: Lista de lags a criar. Se None, usa configuração padrão.
        group_by: Coluna para agrupar (ex: produto_id). Se None, não agrupa.
    
    Returns:
        DataFrame com features de lag adicionadas.
    """
    df_features = df.copy()
    
    if lags is None:
        lags = FEATURE_CONFIG["lags"]
    
    # Garantir que está ordenado por data
    if group_by:
        df_features = df_features.sort_values([group_by, "ds"]).reset_index(drop=True)
    else:
        df_features = df_features.sort_values("ds").reset_index(drop=True)
    
    # Criar lags
    for lag in lags:
        if group_by:
            # Criar lag dentro de cada grupo
            df_features[f"{value_column}_lag_{lag}"] = (
                df_features.groupby(group_by)[value_column].shift(lag)
            )
        else:
            # Criar lag global
            df_features[f"{value_column}_lag_{lag}"] = df_features[value_column].shift(lag)
    
    print(f"Features de lag criadas: {len(lags)} lags")
    print(f"  - Lags: {lags}")
    
    return df_features


def create_rolling_features(
    df: pd.DataFrame,
    value_column: str,
    windows: Optional[List[int]] = None,
    aggregations: Optional[List[str]] = None,
    group_by: Optional[str] = None
) -> pd.DataFrame:
    """
    Cria features de agregação móvel (rolling window) para séries temporais.
    
    Args:
        df: DataFrame com coluna de data e valor.
        value_column: Nome da coluna com os valores para criar agregações.
        windows: Lista de janelas móveis. Se None, usa configuração padrão.
        aggregations: Lista de agregações ('mean', 'std', 'min', 'max'). 
                     Se None, usa configuração padrão.
        group_by: Coluna para agrupar (ex: produto_id). Se None, não agrupa.
    
    Returns:
        DataFrame com features de agregação móvel adicionadas.
    """
    df_features = df.copy()
    
    if windows is None:
        windows = FEATURE_CONFIG["rolling_windows"]
    
    if aggregations is None:
        aggregations = FEATURE_CONFIG["aggregations"]
    
    # Garantir que está ordenado por data
    if group_by:
        df_features = df_features.sort_values([group_by, "ds"]).reset_index(drop=True)
    else:
        df_features = df_features.sort_values("ds").reset_index(drop=True)
    
    # Criar features de rolling
    for window in windows:
        for agg in aggregations:
            feature_name = f"{value_column}_rolling_{window}d_{agg}"
            
            if group_by:
                # Criar rolling dentro de cada grupo
                df_features[feature_name] = (
                    df_features.groupby(group_by)[value_column]
                    .rolling(window=window, min_periods=1)
                    .agg(agg)
                    .reset_index(level=0, drop=True)
                )
            else:
                # Criar rolling global
                df_features[feature_name] = (
                    df_features[value_column]
                    .rolling(window=window, min_periods=1)
                    .agg(agg)
                )
    
    print(f"Features de agregação móvel criadas:")
    print(f"  - Janelas: {windows}")
    print(f"  - Agregações: {aggregations}")
    print(f"  - Total de features: {len(windows) * len(aggregations)}")
    
    return df_features


def create_temporal_features(df: pd.DataFrame, date_column: str = "ds") -> pd.DataFrame:
    """
    Cria features temporais a partir da coluna de data.
    
    Args:
        df: DataFrame com coluna de data.
        date_column: Nome da coluna de data.
    
    Returns:
        DataFrame com features temporais adicionadas.
    """
    df_features = df.copy()
    
    # Garantir que a coluna de data é datetime
    if not pd.api.types.is_datetime64_any_dtype(df_features[date_column]):
        df_features[date_column] = pd.to_datetime(df_features[date_column])
    
    # Extrair componentes temporais
    df_features["year"] = df_features[date_column].dt.year
    df_features["month"] = df_features[date_column].dt.month
    df_features["day"] = df_features[date_column].dt.day
    df_features["day_of_week"] = df_features[date_column].dt.dayofweek
    df_features["day_of_year"] = df_features[date_column].dt.dayofyear
    df_features["week_of_year"] = df_features[date_column].dt.isocalendar().week
    df_features["quarter"] = df_features[date_column].dt.quarter
    
    # Features cíclicas (sin/cos para capturar padrões circulares)
    df_features["month_sin"] = np.sin(2 * np.pi * df_features["month"] / 12)
    df_features["month_cos"] = np.cos(2 * np.pi * df_features["month"] / 12)
    df_features["day_of_week_sin"] = np.sin(2 * np.pi * df_features["day_of_week"] / 7)
    df_features["day_of_week_cos"] = np.cos(2 * np.pi * df_features["day_of_week"] / 7)
    df_features["day_of_year_sin"] = np.sin(2 * np.pi * df_features["day_of_year"] / 365)
    df_features["day_of_year_cos"] = np.cos(2 * np.pi * df_features["day_of_year"] / 365)
    
    print("Features temporais criadas:")
    print("  - Componentes: year, month, day, day_of_week, day_of_year, week_of_year, quarter")
    print("  - Features cíclicas: sin/cos para month, day_of_week, day_of_year")
    
    return df_features


def create_all_features(
    df: pd.DataFrame,
    value_column: str = "y",
    date_column: str = "ds",
    group_by: Optional[str] = None,
    include_lags: bool = True,
    include_rolling: bool = True,
    include_temporal: bool = True
) -> pd.DataFrame:
    """
    Cria todas as features de série temporal de uma vez.
    
    Args:
        df: DataFrame com dados de série temporal.
        value_column: Nome da coluna com valores.
        date_column: Nome da coluna de data.
        group_by: Coluna para agrupar (ex: produto_id). Se None, não agrupa.
        include_lags: Se True, cria features de lag.
        include_rolling: Se True, cria features de agregação móvel.
        include_temporal: Se True, cria features temporais.
    
    Returns:
        DataFrame com todas as features criadas.
    """
    df_features = df.copy()
    
    print("=" * 60)
    print("CRIANDO FEATURES DE SÉRIE TEMPORAL")
    print("=" * 60)
    print()
    
    initial_columns = len(df_features.columns)
    
    # Criar features temporais
    if include_temporal:
        df_features = create_temporal_features(df_features, date_column=date_column)
        print()
    
    # Criar features de lag
    if include_lags:
        df_features = create_lag_features(
            df_features, 
            value_column=value_column,
            group_by=group_by
        )
        print()
    
    # Criar features de agregação móvel
    if include_rolling:
        df_features = create_rolling_features(
            df_features,
            value_column=value_column,
            group_by=group_by
        )
        print()
    
    final_columns = len(df_features.columns)
    new_features = final_columns - initial_columns
    
    print("=" * 60)
    print(f"RESUMO:")
    print(f"  - Colunas iniciais: {initial_columns}")
    print(f"  - Colunas finais: {final_columns}")
    print(f"  - Novas features criadas: {new_features}")
    print("=" * 60)
    
    return df_features


def get_feature_columns(
    df: pd.DataFrame,
    exclude_original: bool = True,
    exclude_date: bool = True
) -> List[str]:
    """
    Retorna lista de colunas de features (excluindo colunas originais e data).
    
    Args:
        df: DataFrame com features.
        exclude_original: Se True, exclui colunas originais (y, estoque, consumo).
        exclude_date: Se True, exclui coluna de data.
    
    Returns:
        Lista de nomes de colunas de features.
    """
    feature_cols = df.columns.tolist()
    
    # Colunas a excluir
    exclude_cols = []
    
    if exclude_date:
        exclude_cols.extend(["ds", "data", "date"])
    
    if exclude_original:
        exclude_cols.extend(["y", "estoque", "consumo", "produto_id"])
    
    # Remover colunas de exclusão
    feature_cols = [col for col in feature_cols if col not in exclude_cols]
    
    return feature_cols

