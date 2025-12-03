"""
Módulo para detecção de anomalias usando Isolation Forest.
Detecta anomalias em consumo e estoque.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Optional, List, Tuple
from pathlib import Path
import joblib

from src.config import ISOLATION_FOREST_CONFIG, MODELS_DIR


def train_isolation_forest(
    df: pd.DataFrame,
    feature_columns: List[str],
    contamination: Optional[float] = None,
    random_state: int = 42,
    n_estimators: int = 100
) -> IsolationForest:
    """
    Treina um modelo Isolation Forest para detecção de anomalias.
    
    Args:
        df: DataFrame com features para treinamento.
        feature_columns: Lista de colunas a usar como features.
        contamination: Proporção esperada de anomalias. Se None, usa config padrão.
        random_state: Seed para reprodutibilidade.
        n_estimators: Número de árvores no Isolation Forest.
    
    Returns:
        Modelo Isolation Forest treinado.
    """
    # Verificar colunas
    missing_cols = [col for col in feature_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas não encontradas: {missing_cols}")
    
    # Preparar features
    X = df[feature_columns].values
    
    # Remover NaN
    mask_valid = ~np.isnan(X).any(axis=1)
    X_clean = X[mask_valid]
    
    if len(X_clean) == 0:
        raise ValueError("Não há dados válidos para treinar o modelo.")
    
    # Usar configuração padrão se não especificado
    if contamination is None:
        contamination = ISOLATION_FOREST_CONFIG["contamination"]
    
    print(f"Treinando Isolation Forest...")
    print(f"  - Registros válidos: {len(X_clean)}")
    print(f"  - Features: {len(feature_columns)}")
    print(f"  - Contamination: {contamination}")
    print(f"  - Número de árvores: {n_estimators}")
    
    # Treinar Isolation Forest
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=n_estimators
    )
    
    iso_forest.fit(X_clean)
    
    print(f"  [OK] Modelo treinado com sucesso!")
    
    return iso_forest


def detect_anomalies(
    model: IsolationForest,
    df: pd.DataFrame,
    feature_columns: List[str]
) -> pd.DataFrame:
    """
    Detecta anomalias usando um modelo Isolation Forest treinado.
    
    Args:
        model: Modelo Isolation Forest treinado.
        df: DataFrame com dados para detecção.
        feature_columns: Lista de colunas usadas como features.
    
    Returns:
        DataFrame original com colunas adicionais: 'anomaly_score' e 'is_anomaly'.
    """
    df_result = df.copy()
    
    # Verificar colunas
    missing_cols = [col for col in feature_columns if col not in df_result.columns]
    if missing_cols:
        raise ValueError(f"Colunas não encontradas: {missing_cols}")
    
    # Preparar features
    X = df_result[feature_columns].values
    
    # Remover NaN
    mask_valid = ~np.isnan(X).any(axis=1)
    X_clean = X[mask_valid]
    
    if len(X_clean) == 0:
        raise ValueError("Não há dados válidos para detecção de anomalias.")
    
    # Detectar anomalias
    predictions = model.predict(X_clean)
    scores = model.score_samples(X_clean)
    
    # Converter scores para valores positivos (quanto menor, mais anômalo)
    anomaly_scores = -scores
    
    # Inicializar colunas
    df_result["anomaly_score"] = np.nan
    df_result["is_anomaly"] = False
    
    # Preencher resultados apenas para dados válidos
    df_result.loc[mask_valid, "anomaly_score"] = anomaly_scores
    df_result.loc[mask_valid, "is_anomaly"] = predictions == -1
    
    n_anomalies = df_result["is_anomaly"].sum()
    print(f"Detecção de anomalias concluída:")
    print(f"  - Total de registros: {len(df_result)}")
    print(f"  - Registros válidos: {mask_valid.sum()}")
    print(f"  - Anomalias detectadas: {n_anomalies} ({n_anomalies/len(df_result)*100:.2f}%)")
    if mask_valid.sum() > 0:
        print(f"  - Score médio: {df_result.loc[mask_valid, 'anomaly_score'].mean():.4f}")
    
    return df_result


def detect_anomalies_consumo_estoque(
    df: pd.DataFrame,
    consumo_column: str = "consumo",
    estoque_column: str = "estoque",
    contamination: Optional[float] = None,
    train_model: bool = True
) -> Tuple[pd.DataFrame, IsolationForest]:
    """
    Detecta anomalias em consumo e estoque usando Isolation Forest.
    
    Args:
        df: DataFrame com dados de consumo e estoque.
        consumo_column: Nome da coluna de consumo.
        estoque_column: Nome da coluna de estoque.
        contamination: Proporção esperada de anomalias.
        train_model: Se True, treina novo modelo. Se False, usa modelo existente.
    
    Returns:
        Tupla (DataFrame com anomalias, modelo treinado).
    """
    feature_cols = [col for col in [consumo_column, estoque_column] if col in df.columns]
    
    if len(feature_cols) == 0:
        raise ValueError(f"Colunas '{consumo_column}' ou '{estoque_column}' não encontradas.")
    
    # Treinar modelo
    model = train_isolation_forest(
        df,
        feature_columns=feature_cols,
        contamination=contamination
    )
    
    # Detectar anomalias
    df_anomalies = detect_anomalies(model, df, feature_columns=feature_cols)
    
    return df_anomalies, model


def save_anomaly_model(
    model: IsolationForest,
    file_path: Path,
    compress: bool = True
) -> None:
    """
    Salva modelo de detecção de anomalias.
    
    Args:
        model: Modelo Isolation Forest treinado.
        file_path: Caminho para salvar o modelo.
        compress: Se True, comprime o arquivo.
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remover extensões existentes
    stem = file_path.stem
    if file_path.suffix == ".gz":
        stem = file_path.with_suffix("").stem
    
    if compress:
        file_path = file_path.parent / f"{stem}.pkl.gz"
    else:
        file_path = file_path.parent / f"{stem}.pkl"
    
    try:
        with open(file_path, "wb") as f:
            joblib.dump(model, f, compress=("gzip", 3) if compress else None)
        
        file_size = file_path.stat().st_size / (1024 * 1024)
        print(f"Modelo de anomalias salvo: {file_path} ({file_size:.2f} MB)")
    except Exception as e:
        raise IOError(f"Erro ao salvar modelo: {e}")


def load_anomaly_model(file_path: Path) -> IsolationForest:
    """
    Carrega modelo de detecção de anomalias.
    
    Args:
        file_path: Caminho do arquivo do modelo.
    
    Returns:
        Modelo Isolation Forest carregado.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        if file_path.suffix == ".pkl":
            file_path = file_path.with_suffix(".pkl.gz")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            model = joblib.load(f)
        print(f"Modelo carregado: {file_path}")
        return model
    except Exception as e:
        raise IOError(f"Erro ao carregar modelo: {e}")

