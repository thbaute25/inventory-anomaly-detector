# Alerts module
# Importar funções do módulo principal src/alerts.py
# Usar importação relativa para evitar conflito com diretório alerts/

import importlib.util
from pathlib import Path

# Carregar módulo diretamente do arquivo
alerts_file = Path(__file__).parent.parent / "alerts.py"
spec = importlib.util.spec_from_file_location("alerts_module", alerts_file)
alerts_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alerts_module)

# Exportar funções
send_discord_alert = alerts_module.send_discord_alert
send_teams_alert = alerts_module.send_teams_alert
format_anomaly_alert = alerts_module.format_anomaly_alert
send_anomaly_alerts = alerts_module.send_anomaly_alerts
send_anomaly_alert_by_product = alerts_module.send_anomaly_alert_by_product
send_email_alert = alerts_module.send_email_alert
format_anomaly_email_html = alerts_module.format_anomaly_email_html
send_anomaly_email = alerts_module.send_anomaly_email

__all__ = [
    "send_discord_alert",
    "send_teams_alert",
    "format_anomaly_alert",
    "send_anomaly_alerts",
    "send_anomaly_alert_by_product",
    "send_email_alert",
    "format_anomaly_email_html",
    "send_anomaly_email"
]
