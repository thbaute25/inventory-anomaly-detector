"""
Módulo para limpeza e preparação de dados de estoque e consumo.
Contém funções para tratar valores faltantes, outliers e inconsistências.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import joblib


def clean_consumo(
    df: pd.DataFrame,
    remove_outliers: bool = True,
    outlier_method: str = "iqr",
    fill_missing: bool = True,
    fill_method: str = "forward_fill",
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    remove_negative: bool = True
) -> pd.DataFrame:
    """
    Limpa e prepara dados de consumo.
    
    Args:
        df: DataFrame com colunas 'ds' (data) e 'y' (consumo).
        remove_outliers: Se True, remove outliers usando o método especificado.
        outlier_method: Método para detectar outliers ('iqr' ou 'zscore').
        fill_missing: Se True, preenche valores faltantes.
        fill_method: Método para preencher valores faltantes 
                    ('forward_fill', 'backward_fill', 'interpolate', 'mean').
        min_value: Valor mínimo permitido. Valores abaixo serão tratados.
        max_value: Valor máximo permitido. Valores acima serão tratados.
        remove_negative: Se True, remove ou trata valores negativos.
    
    Returns:
        DataFrame limpo com dados de consumo.
    """
    df_clean = df.copy()
    
    # Verificar colunas necessárias
    if "y" not in df_clean.columns:
        raise ValueError("DataFrame deve conter a coluna 'y' (consumo)")
    
    if "ds" not in df_clean.columns:
        raise ValueError("DataFrame deve conter a coluna 'ds' (data)")
    
    # Ordenar por data
    df_clean = df_clean.sort_values("ds").reset_index(drop=True)
    
    print("Iniciando limpeza dos dados de consumo...")
    initial_count = len(df_clean)
    
    # 1. Remover valores negativos se solicitado
    if remove_negative:
        negative_count = (df_clean["y"] < 0).sum()
        if negative_count > 0:
            print(f"  - Encontrados {negative_count} valores negativos")
            # Substituir por 0 ou remover
            df_clean.loc[df_clean["y"] < 0, "y"] = 0
    
    # 2. Aplicar limites mínimo e máximo
    if min_value is not None:
        below_min = (df_clean["y"] < min_value).sum()
        if below_min > 0:
            print(f"  - {below_min} valores abaixo do mínimo ({min_value})")
            df_clean.loc[df_clean["y"] < min_value, "y"] = min_value
    
    if max_value is not None:
        above_max = (df_clean["y"] > max_value).sum()
        if above_max > 0:
            print(f"  - {above_max} valores acima do máximo ({max_value})")
            df_clean.loc[df_clean["y"] > max_value, "y"] = max_value
    
    # 3. Remover outliers
    if remove_outliers:
        outliers_mask = _detect_outliers(
            df_clean["y"], 
            method=outlier_method
        )
        outliers_count = outliers_mask.sum()
        
        if outliers_count > 0:
            print(f"  - Detectados {outliers_count} outliers usando método '{outlier_method}'")
            # Marcar outliers como NaN para serem tratados no próximo passo
            df_clean.loc[outliers_mask, "y"] = np.nan
    
    # 4. Preencher valores faltantes
    missing_before = df_clean["y"].isna().sum()
    
    if fill_missing and missing_before > 0:
        df_clean = _fill_missing_values(df_clean, method=fill_method)
        missing_after = df_clean["y"].isna().sum()
        print(f"  - Valores faltantes: {missing_before} -> {missing_after}")
    
    # 5. Verificar se ainda há valores faltantes
    if df_clean["y"].isna().any():
        print(f"  - Aviso: Ainda existem {df_clean['y'].isna().sum()} valores faltantes")
        # Remover linhas com valores faltantes se necessário
        df_clean = df_clean.dropna(subset=["y"])
    
    # 6. Verificar duplicatas de data
    duplicates = df_clean["ds"].duplicated().sum()
    if duplicates > 0:
        print(f"  - Encontradas {duplicates} datas duplicadas. Mantendo a primeira ocorrência.")
        df_clean = df_clean.drop_duplicates(subset=["ds"], keep="first")
    
    final_count = len(df_clean)
    removed_count = initial_count - final_count
    
    print(f"\nLimpeza concluída!")
    print(f"  - Registros iniciais: {initial_count}")
    print(f"  - Registros finais: {final_count}")
    print(f"  - Registros removidos: {removed_count}")
    print(f"  - Valores nulos finais: {df_clean['y'].isna().sum()}")
    
    return df_clean.reset_index(drop=True)


def _detect_outliers(series: pd.Series, method: str = "iqr") -> pd.Series:
    """
    Detecta outliers em uma série usando diferentes métodos.
    
    Args:
        series: Série com valores numéricos.
        method: Método de detecção ('iqr' ou 'zscore').
    
    Returns:
        Série booleana indicando outliers (True = outlier).
    """
    if method == "iqr":
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return (series < lower_bound) | (series > upper_bound)
    
    elif method == "zscore":
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > 3  # Valores além de 3 desvios padrão
    
    else:
        raise ValueError(f"Método '{method}' não suportado. Use 'iqr' ou 'zscore'.")


def _fill_missing_values(
    df: pd.DataFrame, 
    method: str = "forward_fill"
) -> pd.DataFrame:
    """
    Preenche valores faltantes na coluna 'y' usando diferentes métodos.
    
    Args:
        df: DataFrame com colunas 'ds' e 'y'.
        method: Método de preenchimento.
    
    Returns:
        DataFrame com valores faltantes preenchidos.
    """
    df_filled = df.copy()
    
    if method == "forward_fill":
        df_filled["y"] = df_filled["y"].ffill()
        df_filled["y"] = df_filled["y"].bfill()  # Se ainda houver no início
    
    elif method == "backward_fill":
        df_filled["y"] = df_filled["y"].bfill()
        df_filled["y"] = df_filled["y"].ffill()  # Se ainda houver no final
    
    elif method == "interpolate":
        df_filled["y"] = df_filled["y"].interpolate(method="linear")
        # Preencher extremos se necessário
        df_filled["y"] = df_filled["y"].ffill()
        df_filled["y"] = df_filled["y"].bfill()
    
    elif method == "mean":
        mean_value = df_filled["y"].mean()
        df_filled["y"] = df_filled["y"].fillna(mean_value)
    
    else:
        raise ValueError(
            f"Método '{method}' não suportado. "
            "Use 'forward_fill', 'backward_fill', 'interpolate' ou 'mean'."
        )
    
    return df_filled


def save_processed(
    df: pd.DataFrame,
    file_path: Path,
    format: str = "csv",
    compress: bool = False,
    index: bool = False
) -> None:
    """
    Salva dados processados em arquivo.
    
    Args:
        df: DataFrame com dados processados a serem salvos.
        file_path: Caminho completo do arquivo de saída.
        format: Formato de arquivo ('csv', 'pkl', 'parquet').
        compress: Se True, comprime o arquivo (apenas para CSV e pickle).
        index: Se True, salva o índice do DataFrame.
    
    Raises:
        ValueError: Se o formato não for suportado.
        IOError: Se houver erro ao salvar o arquivo.
    """
    # Criar diretório se não existir
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Salvando dados processados em: {file_path}")
    
    try:
        if format.lower() == "csv":
            if compress:
                # CSV comprimido
                file_path = file_path.with_suffix(".csv.gz")
                df.to_csv(file_path, index=index, compression="gzip", encoding="utf-8")
            else:
                df.to_csv(file_path, index=index, encoding="utf-8")
        
        elif format.lower() == "pkl" or format.lower() == "pickle":
            if compress:
                # Pickle comprimido
                file_path = file_path.with_suffix(".pkl.gz")
                with open(file_path, "wb") as f:
                    joblib.dump(df, f, compress=("gzip", 3))
            else:
                file_path = file_path.with_suffix(".pkl")
                with open(file_path, "wb") as f:
                    joblib.dump(df, f)
        
        elif format.lower() == "parquet":
            file_path = file_path.with_suffix(".parquet")
            df.to_parquet(file_path, index=index, compression="snappy" if compress else None)
        
        else:
            raise ValueError(
                f"Formato '{format}' não suportado. "
                "Use 'csv', 'pkl' ou 'parquet'."
            )
        
        file_size = file_path.stat().st_size / (1024 * 1024)  # Tamanho em MB
        print(f"  [OK] Arquivo salvo com sucesso!")
        print(f"  - Formato: {format.upper()}")
        print(f"  - Tamanho: {file_size:.2f} MB")
        print(f"  - Registros: {len(df)}")
        print(f"  - Colunas: {len(df.columns)}")
        
    except Exception as e:
        raise IOError(f"Erro ao salvar arquivo: {e}")

