"""
Módulo para agregação de dados por item e data.
Cria agregados diários por produto.
"""

import pandas as pd
from typing import Dict, Optional, List
from src.config import (
    DATE_COLUMN,
    PRODUCT_COLUMN,
    STOCK_COLUMN,
    CONSUMPTION_COLUMN,
)


def aggregate_daily_by_item(
    df: pd.DataFrame,
    aggregations: Optional[Dict[str, List[str]]] = None,
    fill_missing_dates: bool = False
) -> pd.DataFrame:
    """
    Cria agregados diários por item (produto).
    
    Args:
        df: DataFrame com dados de estoque e consumo.
        aggregations: Dicionário com colunas e funções de agregação.
                     Ex: {"consumo": ["mean", "sum"], "estoque": ["mean", "min", "max"]}
                     Se None, usa agregações padrão.
        fill_missing_dates: Se True, preenche datas faltantes com NaN.
    
    Returns:
        DataFrame agregado por produto e data.
    """
    df_agg = df.copy()
    
    # Verificar colunas necessárias
    required_cols = [DATE_COLUMN, PRODUCT_COLUMN]
    missing_cols = [col for col in required_cols if col not in df_agg.columns]
    
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias não encontradas: {missing_cols}")
    
    # Garantir que a data é datetime
    if not pd.api.types.is_datetime64_any_dtype(df_agg[DATE_COLUMN]):
        df_agg[DATE_COLUMN] = pd.to_datetime(df_agg[DATE_COLUMN])
    
    # Normalizar data para dia (remover hora se houver)
    df_agg[DATE_COLUMN] = df_agg[DATE_COLUMN].dt.normalize()
    
    # Definir agregações padrão se não fornecidas
    if aggregations is None:
        aggregations = {
            CONSUMPTION_COLUMN: ["mean", "sum", "min", "max", "std"],
            STOCK_COLUMN: ["mean", "min", "max", "std"]
        }
    
    # Criar dicionário de agregação para groupby
    agg_functions = {}
    for col, funcs in aggregations.items():
        if col in df_agg.columns:
            # Criar lista de funções para esta coluna
            func_list = []
            for func in funcs:
                if func in ["mean", "sum", "min", "max", "std", "count"]:
                    func_list.append(func)
            
            if func_list:
                agg_functions[col] = func_list
    
    # Se não houver colunas para agregar, apenas contar registros
    if not agg_functions:
        grouped = df_agg.groupby([PRODUCT_COLUMN, DATE_COLUMN])
        df_result = grouped.size().reset_index(name="count")
    else:
        # Agrupar por produto e data e aplicar agregações
        grouped = df_agg.groupby([PRODUCT_COLUMN, DATE_COLUMN])
        df_result = grouped.agg(agg_functions).reset_index()
        
        # Achatar MultiIndex nas colunas se necessário
        if isinstance(df_result.columns, pd.MultiIndex):
            df_result.columns = [
                f"{col}_{func}" if func else col 
                for col, func in df_result.columns
            ]
    
    # Preencher datas faltantes se solicitado
    if fill_missing_dates:
        df_result = _fill_missing_dates(df_result, PRODUCT_COLUMN, DATE_COLUMN)
    
    # Ordenar resultado
    df_result = df_result.sort_values([PRODUCT_COLUMN, DATE_COLUMN]).reset_index(drop=True)
    
    print("Agregação diária por item concluída!")
    print(f"  - Produtos: {df_result[PRODUCT_COLUMN].nunique()}")
    print(f"  - Período: {df_result[DATE_COLUMN].min()} a {df_result[DATE_COLUMN].max()}")
    print(f"  - Total de registros agregados: {len(df_result)}")
    print(f"  - Colunas criadas: {len(df_result.columns) - 2}")  # -2 para produto e data
    
    return df_result


def _fill_missing_dates(
    df: pd.DataFrame,
    group_col: str,
    date_col: str
) -> pd.DataFrame:
    """
    Preenche datas faltantes para cada grupo.
    
    Args:
        df: DataFrame com dados agrupados.
        group_col: Coluna de agrupamento (ex: produto_id).
        date_col: Coluna de data.
    
    Returns:
        DataFrame com datas faltantes preenchidas.
    """
    # Criar range completo de datas para cada grupo
    date_range = pd.date_range(
        start=df[date_col].min(),
        end=df[date_col].max(),
        freq="D"
    )
    
    # Criar MultiIndex com todas as combinações
    groups = df[group_col].unique()
    multi_index = pd.MultiIndex.from_product(
        [groups, date_range],
        names=[group_col, date_col]
    )
    
    # Reindexar DataFrame
    df_filled = df.set_index([group_col, date_col]).reindex(multi_index).reset_index()
    
    return df_filled


def aggregate_consumo_daily_by_item(
    df: pd.DataFrame,
    fill_missing_dates: bool = False
) -> pd.DataFrame:
    """
    Cria agregados diários de consumo por item.
    Função de conveniência específica para consumo.
    
    Args:
        df: DataFrame com dados de consumo.
        fill_missing_dates: Se True, preenche datas faltantes com NaN.
    
    Returns:
        DataFrame agregado por produto e data com consumo agregado.
    """
    aggregations = {
        CONSUMPTION_COLUMN: ["mean", "sum", "min", "max", "std", "count"]
    }
    
    return aggregate_daily_by_item(
        df,
        aggregations=aggregations,
        fill_missing_dates=fill_missing_dates
    )


def aggregate_stock_daily_by_item(
    df: pd.DataFrame,
    fill_missing_dates: bool = False
) -> pd.DataFrame:
    """
    Cria agregados diários de estoque por item.
    Função de conveniência específica para estoque.
    
    Args:
        df: DataFrame com dados de estoque.
        fill_missing_dates: Se True, preenche datas faltantes com NaN.
    
    Returns:
        DataFrame agregado por produto e data com estoque agregado.
    """
    aggregations = {
        STOCK_COLUMN: ["mean", "min", "max", "std"]
    }
    
    return aggregate_daily_by_item(
        df,
        aggregations=aggregations,
        fill_missing_dates=fill_missing_dates
    )

