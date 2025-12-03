"""
Script de teste para envio de alertas (Discord, Teams, Email).
"""

import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.alerts import (
    format_anomaly_alert,
    format_anomaly_email_html,
    send_discord_alert,
    send_teams_alert,
    send_email_alert,
    send_anomaly_alerts,
    send_anomaly_alert_by_product
)

print("=" * 60)
print("TESTE DE ENVIO DE ALERTAS - Inventory Anomaly Detector")
print("=" * 60)
print()

# Carregar anomalias detectadas
print("1. Carregando anomalias detectadas...")
print("-" * 60)
try:
    anomalies_file = Path("outputs/anomalies_only.csv")
    if not anomalies_file.exists():
        print(f"   [ERRO] Arquivo não encontrado: {anomalies_file}")
        print("   Execute primeiro: py detect_anomalies_example.py")
        sys.exit(1)
    
    anomalies = pd.read_csv(anomalies_file)
    anomalies['data'] = pd.to_datetime(anomalies['data'])
    
    # Filtrar apenas anomalias com score alto (>= 0.7)
    high_score_anomalies = anomalies[anomalies['anomaly_score'] >= 0.7].copy()
    
    print(f"   [OK] Anomalias carregadas: {len(anomalies)}")
    print(f"   [OK] Anomalias com score >= 0.7: {len(high_score_anomalies)}")
    
    if len(high_score_anomalies) == 0:
        print("   [AVISO] Nenhuma anomalia com score alto encontrada.")
        print("   Usando top 5 anomalias para teste...")
        high_score_anomalies = anomalies.nlargest(5, 'anomaly_score')
    
except Exception as e:
    print(f"   [ERRO] Erro ao carregar anomalias: {e}")
    sys.exit(1)

print()

# 2. Testar formatação de mensagens
print("2. Testando formatação de mensagens...")
print("-" * 60)

# Formatar mensagem de texto
test_anomalies = high_score_anomalies.head(5)
text_message = format_anomaly_alert(test_anomalies, max_anomalies=5)
print("   [OK] Mensagem de texto formatada")
print(f"   Tamanho da mensagem: {len(text_message)} caracteres")

# Formatar HTML
html_message = format_anomaly_email_html(test_anomalies)
print("   [OK] Mensagem HTML formatada")
print(f"   Tamanho do HTML: {len(html_message)} caracteres")

print()

# 3. Verificar configurações
print("3. Verificando configurações...")
print("-" * 60)

from src.config import ALERT_CONFIG, EMAIL_CONFIG

print("Configurações de Webhooks:")
print(f"   Discord webhook: {'Configurado' if ALERT_CONFIG.get('discord_webhook_url') else 'Não configurado'}")
print(f"   Teams webhook: {'Configurado' if ALERT_CONFIG.get('teams_webhook_url') else 'Não configurado'}")

print("\nConfigurações de Email:")
print(f"   SMTP Server: {EMAIL_CONFIG.get('smtp_server', 'Não configurado')}")
print(f"   SMTP Port: {EMAIL_CONFIG.get('smtp_port', 'Não configurado')}")
print(f"   From Email: {EMAIL_CONFIG.get('from_email', 'Não configurado')}")
print(f"   To Emails: {len(EMAIL_CONFIG.get('to_emails', []))} destinatário(s)")

print()

# 4. Testar envio de alertas individuais
print("4. Testando envio de alertas individuais...")
print("-" * 60)

# Teste Discord
print("\n4.1. Teste Discord:")
print("-" * 40)
if ALERT_CONFIG.get('discord_webhook_url'):
    result = send_discord_alert(text_message, title="Teste de Alerta - Discord")
    print(f"   Resultado: {'Sucesso' if result else 'Falha'}")
else:
    print("   [PULADO] Discord webhook não configurado")
    print("   Para configurar, edite src/config.py e defina ALERT_CONFIG['discord_webhook_url']")

# Teste Teams
print("\n4.2. Teste Teams:")
print("-" * 40)
if ALERT_CONFIG.get('teams_webhook_url'):
    result = send_teams_alert(text_message, title="Teste de Alerta - Teams")
    print(f"   Resultado: {'Sucesso' if result else 'Falha'}")
else:
    print("   [PULADO] Teams webhook não configurado")
    print("   Para configurar, edite src/config.py e defina ALERT_CONFIG['teams_webhook_url']")

# Teste Email
print("\n4.3. Teste Email:")
print("-" * 40)
email_config_ok = (
    EMAIL_CONFIG.get('smtp_server') and
    EMAIL_CONFIG.get('from_email') and
    EMAIL_CONFIG.get('to_emails')
)
if email_config_ok:
    result = send_email_alert(
        text_message,
        title="Teste de Alerta - Email",
        html_message=html_message
    )
    print(f"   Resultado: {'Sucesso' if result else 'Falha'}")
else:
    print("   [PULADO] Email não configurado completamente")
    print("   Para configurar, edite src/config.py e defina:")
    print("     - EMAIL_CONFIG['smtp_server']")
    print("     - EMAIL_CONFIG['from_email']")
    print("     - EMAIL_CONFIG['to_emails']")
    print("     - EMAIL_CONFIG['smtp_password'] (senha ou app password)")

print()

# 5. Testar envio de alertas agrupados
print("5. Testando envio de alertas agrupados...")
print("-" * 60)

print("\n5.1. Envio de alertas (todos):")
print("-" * 40)
print("   [INFO] Para testar, descomente as linhas abaixo:")
print("   results = send_anomaly_alerts(")
print("       high_score_anomalies,")
print("       produto_id='TODOS',")
print("       min_score=0.7,")
print("       send_discord=False,")
print("       send_teams=False,")
print("       send_email=False")
print("   )")

# Exemplo comentado:
# results = send_anomaly_alerts(
#     high_score_anomalies,
#     produto_id="TODOS",
#     min_score=0.7,
#     send_discord=bool(ALERT_CONFIG.get('discord_webhook_url')),
#     send_teams=bool(ALERT_CONFIG.get('teams_webhook_url')),
#     send_email=email_config_ok
# )
# print(f"   Resultados: {results}")

print("\n5.2. Envio de alertas por produto:")
print("-" * 40)
print("   [INFO] Para testar, descomente as linhas abaixo:")
print("   results_by_product = send_anomaly_alert_by_product(")
print("       high_score_anomalies,")
print("       produto_column='produto_id',")
print("       min_score=0.7,")
print("       send_discord=False,")
print("       send_teams=False,")
print("       send_email=False")
print("   )")

# Exemplo comentado:
# results_by_product = send_anomaly_alert_by_product(
#     high_score_anomalies,
#     produto_column="produto_id",
#     min_score=0.7,
#     send_discord=bool(ALERT_CONFIG.get('discord_webhook_url')),
#     send_teams=bool(ALERT_CONFIG.get('teams_webhook_url')),
#     send_email=email_config_ok
# )
# print(f"   Alertas enviados para {len(results_by_product)} produtos")

print()

# 6. Preview das mensagens
print("6. Preview das mensagens formatadas...")
print("-" * 60)

print("\n6.1. Mensagem de texto (primeiras 500 caracteres):")
print("-" * 40)
print(text_message[:500])
print("...")

print("\n6.2. Mensagem HTML (primeiras 500 caracteres):")
print("-" * 40)
print(html_message[:500])
print("...")

print()

# 7. Resumo
print("=" * 60)
print("RESUMO DO TESTE")
print("=" * 60)
print(f"Anomalias carregadas: {len(anomalies)}")
print(f"Anomalias para teste (score >= 0.7): {len(high_score_anomalies)}")
print(f"Mensagens formatadas: OK")
print(f"Discord: {'Configurado' if ALERT_CONFIG.get('discord_webhook_url') else 'Não configurado'}")
print(f"Teams: {'Configurado' if ALERT_CONFIG.get('teams_webhook_url') else 'Não configurado'}")
print(f"Email: {'Configurado' if email_config_ok else 'Não configurado'}")
print()
print("Para habilitar o envio de alertas:")
print("  1. Configure os webhooks/email em src/config.py")
print("  2. Execute este script novamente")
print("  3. Ou use as funções diretamente no seu código")
print("=" * 60)

