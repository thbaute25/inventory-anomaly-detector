"""
Arquivo de configuração do projeto Inventory Anomaly Detector.
Contém constantes, caminhos e parâmetros utilizados em todo o pipeline.
"""

from pathlib import Path

# Diretórios do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = OUTPUTS_DIR / "models"

# Caminhos de arquivos
DATA_FILE = DATA_DIR / "inventory_data.csv"
REPORT_OUTPUT_DIR = OUTPUTS_DIR / "reports"

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
REPORT_OUTPUT_DIR.mkdir(exist_ok=True)

# Configurações de dados
DATE_COLUMN = "data"
PRODUCT_COLUMN = "produto_id"
STOCK_COLUMN = "estoque"
CONSUMPTION_COLUMN = "consumo"

# Configurações do Prophet
PROPHET_CONFIG = {
    "yearly_seasonality": True,
    "weekly_seasonality": True,
    "daily_seasonality": False,
    "seasonality_mode": "multiplicative",
    "changepoint_prior_scale": 0.05,
    "interval_width": 0.95,
}

# Configurações do Isolation Forest
ISOLATION_FOREST_CONFIG = {
    "contamination": 0.1,  # 10% de anomalias esperadas
    "random_state": 42,
    "n_estimators": 100,
}

# Configurações de features temporais
FEATURE_CONFIG = {
    "lags": [1, 7, 30],  # Lags de 1, 7 e 30 dias
    "rolling_windows": [7, 30],  # Janelas móveis de 7 e 30 dias
    "aggregations": ["mean", "std", "min", "max"],
}

# Configurações de alertas (webhooks)
ALERT_CONFIG = {
    "discord_webhook_url": None,  # Configurar quando necessário
    "teams_webhook_url": None,  # Configurar quando necessário
    "min_anomaly_score": 0.7,  # Score mínimo para enviar alerta
}

# Configurações de email
EMAIL_CONFIG = {
    "smtp_server": None,  # Ex: "smtp.gmail.com"
    "smtp_port": 587,  # Porta SMTP (587 para TLS, 465 para SSL)
    "smtp_username": None,  # Email do remetente
    "smtp_password": None,  # Senha ou app password
    "from_email": None,  # Email do remetente
    "to_emails": [],  # Lista de emails destinatários
    "use_tls": True,  # Usar TLS
}

# Configurações de relatório PDF
REPORT_CONFIG = {
    "title": "Relatório de Anomalias em Estoque e Consumo",
    "author": "Inventory Anomaly Detector",
    "font_size": 10,
    "figure_dpi": 300,
}

# Configurações do Prefect
PREFECT_CONFIG = {
    "flow_name": "inventory_anomaly_detection",
    "retries": 2,
    "retry_delay_seconds": 60,
}

