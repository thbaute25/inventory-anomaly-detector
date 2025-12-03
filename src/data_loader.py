"""
Módulo para carregamento de dados de estoque e consumo.
Lê dados de um arquivo CSV e retorna um DataFrame preparado.
"""

import pandas as pd
from pathlib import Path
from typing import Optional

from src.config import (
    DATA_FILE,
    DATE_COLUMN,
    PRODUCT_COLUMN,
    STOCK_COLUMN,
    CONSUMPTION_COLUMN,
)


def load_inventory_data(
    file_path: Optional[Path] = None,
    parse_dates: bool = True,
    sort_by_date: bool = True
) -> pd.DataFrame:
    """
    Carrega dados de estoque e consumo de um arquivo CSV.
    
    Args:
        file_path: Caminho para o arquivo CSV. Se None, usa o caminho padrão do config.
        parse_dates: Se True, converte a coluna de data para datetime.
        sort_by_date: Se True, ordena os dados por data.
    
    Returns:
        DataFrame com os dados de estoque e consumo.
    
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        ValueError: Se o arquivo estiver vazio ou não contiver as colunas esperadas.
    """
    # Usar caminho padrão se não fornecido
    if file_path is None:
        file_path = DATA_FILE
    
    # Verificar se o arquivo existe
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    # Carregar CSV
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo CSV: {e}")
    
    # Verificar se o DataFrame está vazio
    if df.empty:
        raise ValueError("O arquivo CSV está vazio.")
    
    # Verificar colunas obrigatórias
    required_columns = [DATE_COLUMN, PRODUCT_COLUMN, STOCK_COLUMN, CONSUMPTION_COLUMN]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias não encontradas: {missing_columns}. "
            f"Colunas disponíveis: {list(df.columns)}"
        )
    
    # Converter coluna de data se solicitado
    if parse_dates:
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
        
        # Verificar se a conversão foi bem-sucedida
        if df[DATE_COLUMN].isna().any():
            raise ValueError(
                f"Erro ao converter coluna '{DATE_COLUMN}' para datetime. "
                "Verifique o formato das datas no arquivo."
            )
    
    # Ordenar por data se solicitado
    if sort_by_date and parse_dates:
        df = df.sort_values(by=[PRODUCT_COLUMN, DATE_COLUMN]).reset_index(drop=True)
    
    # Verificar tipos de dados numéricos
    try:
        df[STOCK_COLUMN] = pd.to_numeric(df[STOCK_COLUMN], errors="coerce")
        df[CONSUMPTION_COLUMN] = pd.to_numeric(df[CONSUMPTION_COLUMN], errors="coerce")
    except Exception as e:
        raise ValueError(f"Erro ao converter colunas numéricas: {e}")
    
    # Verificar valores negativos (se não forem esperados)
    if (df[STOCK_COLUMN] < 0).any():
        print(f"Aviso: Encontrados {df[STOCK_COLUMN].lt(0).sum()} valores negativos na coluna '{STOCK_COLUMN}'.")
    
    if (df[CONSUMPTION_COLUMN] < 0).any():
        print(f"Aviso: Encontrados {df[CONSUMPTION_COLUMN].lt(0).sum()} valores negativos na coluna '{CONSUMPTION_COLUMN}'.")
    
    print(f"Dados carregados com sucesso!")
    print(f"  - Total de registros: {len(df)}")
    print(f"  - Período: {df[DATE_COLUMN].min()} a {df[DATE_COLUMN].max()}")
    print(f"  - Produtos: {df[PRODUCT_COLUMN].nunique()}")
    print(f"  - Valores nulos: {df.isnull().sum().sum()}")
    
    return df


def validate_data(df: pd.DataFrame) -> bool:
    """
    Valida se o DataFrame contém os dados necessários para o pipeline.
    
    Args:
        df: DataFrame a ser validado.
    
    Returns:
        True se os dados são válidos.
    
    Raises:
        ValueError: Se os dados não passarem na validação.
    """
    # Verificar se o DataFrame está vazio
    if df.empty:
        raise ValueError("DataFrame está vazio.")
    
    # Verificar colunas obrigatórias
    required_columns = [DATE_COLUMN, PRODUCT_COLUMN, STOCK_COLUMN, CONSUMPTION_COLUMN]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias não encontradas: {missing_columns}")
    
    # Verificar se há dados suficientes (mínimo de registros)
    min_records = 30  # Mínimo de 30 dias para análise
    if len(df) < min_records:
        raise ValueError(
            f"Dados insuficientes. Mínimo de {min_records} registros necessário. "
            f"Encontrados: {len(df)}"
        )
    
    # Verificar se há múltiplos produtos ou dados suficientes por produto
    products = df[PRODUCT_COLUMN].unique()
    for product in products:
        product_data = df[df[PRODUCT_COLUMN] == product]
        if len(product_data) < min_records:
            print(
                f"Aviso: Produto '{product}' tem apenas {len(product_data)} registros. "
                f"Mínimo recomendado: {min_records}"
            )
    
    print("Validação dos dados concluída com sucesso!")
    return True


def load_raw_consumo(
    file_path: Optional[Path] = None,
    produto_id: Optional[str] = None
) -> pd.DataFrame:
    """
    Carrega dados brutos de consumo do CSV.
    Retorna um DataFrame com colunas de data e consumo, formatado para análise de séries temporais.
    
    Args:
        file_path: Caminho para o arquivo CSV. Se None, usa o caminho padrão do config.
        produto_id: ID do produto específico. Se None, retorna dados de todos os produtos.
    
    Returns:
        DataFrame com colunas: ds (data) e y (consumo), e produto_id se múltiplos produtos.
        Formato adequado para Prophet (ds, y).
    
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        ValueError: Se o arquivo estiver vazio ou não contiver as colunas esperadas.
    """
    # Carregar dados completos
    df = load_inventory_data(file_path=file_path, parse_dates=True, sort_by_date=True)
    
    # Filtrar por produto se especificado
    if produto_id is not None:
        if produto_id not in df[PRODUCT_COLUMN].values:
            available_products = df[PRODUCT_COLUMN].unique().tolist()
            raise ValueError(
                f"Produto '{produto_id}' não encontrado. "
                f"Produtos disponíveis: {available_products}"
            )
        df = df[df[PRODUCT_COLUMN] == produto_id].copy()
    
    # Preparar DataFrame para Prophet (ds = data, y = consumo)
    consumo_df = pd.DataFrame({
        "ds": df[DATE_COLUMN],
        "y": df[CONSUMPTION_COLUMN]
    })
    
    # Adicionar produto_id se houver múltiplos produtos
    if produto_id is None and df[PRODUCT_COLUMN].nunique() > 1:
        consumo_df[PRODUCT_COLUMN] = df[PRODUCT_COLUMN].values
    
    # Remover valores nulos
    consumo_df = consumo_df.dropna(subset=["ds", "y"])
    
    # Ordenar por data
    consumo_df = consumo_df.sort_values("ds").reset_index(drop=True)
    
    print(f"Dados de consumo carregados!")
    print(f"  - Total de registros: {len(consumo_df)}")
    print(f"  - Período: {consumo_df['ds'].min()} a {consumo_df['ds'].max()}")
    if produto_id is None and PRODUCT_COLUMN in consumo_df.columns:
        print(f"  - Produtos: {consumo_df[PRODUCT_COLUMN].nunique()}")
    
    return consumo_df

