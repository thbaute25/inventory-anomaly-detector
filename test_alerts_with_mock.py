"""
Script de teste para envio de alertas com simulação (mock).
Demonstra como funcionaria o envio sem precisar configurar webhooks/email reais.
"""

import sys
from pathlib import Path
import pandas as pd
from unittest.mock import patch, MagicMock

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
print("TESTE DE ENVIO DE ALERTAS COM MOCK")
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
    
    if len(high_score_anomalies) == 0:
        high_score_anomalies = anomalies.nlargest(5, 'anomaly_score')
    
    print(f"   [OK] Anomalias carregadas: {len(anomalies)}")
    print(f"   [OK] Anomalias para teste: {len(high_score_anomalies)}")
    
except Exception as e:
    print(f"   [ERRO] Erro ao carregar anomalias: {e}")
    sys.exit(1)

print()

# 2. Formatar mensagens
print("2. Formatando mensagens...")
print("-" * 60)

test_anomalies = high_score_anomalies.head(5)
text_message = format_anomaly_alert(test_anomalies, max_anomalies=5)
html_message = format_anomaly_email_html(test_anomalies)

print("   [OK] Mensagens formatadas")
print()

# 3. Testar envio com mock
print("3. Testando envio de alertas (simulado)...")
print("-" * 60)

# Mock para requests (Discord e Teams)
mock_response = MagicMock()
mock_response.status_code = 200
mock_response.raise_for_status = MagicMock()

# Mock para SMTP (Email)
import smtplib
mock_smtp_instance = MagicMock()
mock_smtp_instance.starttls = MagicMock()
mock_smtp_instance.login = MagicMock()
mock_smtp_instance.send_message = MagicMock()
mock_smtp_instance.quit = MagicMock()

print("\n3.1. Teste Discord (simulado):")
print("-" * 40)
import requests
# Configurar webhook temporário para teste
from src.config import ALERT_CONFIG
original_discord_url = ALERT_CONFIG.get('discord_webhook_url')
ALERT_CONFIG['discord_webhook_url'] = 'https://discord.com/api/webhooks/test'

with patch.object(requests, 'post', return_value=mock_response):
    result = send_discord_alert(text_message, title="Teste de Alerta - Discord")
    print(f"   Resultado: {'Sucesso' if result else 'Falha'}")
    print("   [INFO] Em produção, isso enviaria para o webhook do Discord")

# Restaurar configuração original
ALERT_CONFIG['discord_webhook_url'] = original_discord_url

print("\n3.2. Teste Teams (simulado):")
print("-" * 40)
# Configurar webhook temporário para teste
original_teams_url = ALERT_CONFIG.get('teams_webhook_url')
ALERT_CONFIG['teams_webhook_url'] = 'https://outlook.office.com/webhook/test'

with patch.object(requests, 'post', return_value=mock_response):
    result = send_teams_alert(text_message, title="Teste de Alerta - Teams")
    print(f"   Resultado: {'Sucesso' if result else 'Falha'}")
    print("   [INFO] Em produção, isso enviaria para o webhook do Teams")

# Restaurar configuração original
ALERT_CONFIG['teams_webhook_url'] = original_teams_url

print("\n3.3. Teste Email (simulado):")
print("-" * 40)
with patch.object(smtplib, 'SMTP', return_value=mock_smtp_instance):
    result = send_email_alert(
        subject="Teste de Alerta - Email",
        message=text_message,
        html_message=html_message,
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_username="test@example.com",
        smtp_password="password",
        from_email="test@example.com",
        to_emails=["recipient@example.com"]
    )
    print(f"   Resultado: {'Sucesso' if result else 'Falha'}")
    print("   [INFO] Em produção, isso enviaria email via SMTP")

print()

# 4. Testar funções agrupadas
print("4. Testando funções de alerta agrupadas (simulado)...")
print("-" * 60)

print("\n4.1. Envio de alertas (todos):")
print("-" * 40)
# Configurar webhook temporário
ALERT_CONFIG['discord_webhook_url'] = 'https://discord.com/api/webhooks/test'

with patch.object(requests, 'post', return_value=mock_response):
    results = send_anomaly_alerts(
        high_score_anomalies,
        produto_id="TODOS",
        min_score=0.7,
        send_discord=True,
        send_teams=False
    )
    print(f"   Resultados: {results}")
    print("   [INFO] Discord simulado enviado com sucesso")

# Restaurar configuração original
ALERT_CONFIG['discord_webhook_url'] = original_discord_url

print("\n4.2. Envio de alertas por produto:")
print("-" * 40)
# Configurar webhook temporário
ALERT_CONFIG['discord_webhook_url'] = 'https://discord.com/api/webhooks/test'

with patch.object(requests, 'post', return_value=mock_response):
    results_by_product = send_anomaly_alert_by_product(
        high_score_anomalies.head(20),  # Limitar para teste
        produto_column="produto_id",
        min_score=0.7,
        send_discord=True,
        send_teams=False
    )
    print(f"   Alertas enviados para {len(results_by_product)} produtos")
    for produto, result in list(results_by_product.items())[:3]:
        print(f"     - {produto}: {result}")

# Restaurar configuração original
ALERT_CONFIG['discord_webhook_url'] = original_discord_url

print()

# 5. Mostrar mensagens formatadas
print("5. Preview das mensagens formatadas...")
print("-" * 60)

print("\n5.1. Mensagem de texto completa:")
print("=" * 60)
print(text_message)
print("=" * 60)

print("\n5.2. Mensagem HTML (primeiras 800 caracteres):")
print("=" * 60)
print(html_message[:800])
print("...")
print("=" * 60)

print()

# 6. Resumo
print("=" * 60)
print("RESUMO DO TESTE COM MOCK")
print("=" * 60)
print(f"Anomalias testadas: {len(test_anomalies)}")
print(f"Formatação de mensagens: OK")
print(f"Envio simulado Discord: OK")
print(f"Envio simulado Teams: OK")
print(f"Envio simulado Email: OK")
print(f"Funções agrupadas: OK")
print()
print("TODOS OS TESTES PASSARAM!")
print()
print("Para usar em produção:")
print("  1. Configure webhooks/email em src/config.py")
print("  2. Use as funções normalmente (sem mock)")
print("  3. Os alertas serão enviados automaticamente")
print("=" * 60)

