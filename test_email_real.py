"""
Script para testar envio real de email.
"""

import sys
from pathlib import Path
import pandas as pd

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.alerts import send_email_alert, format_anomaly_email_html
from src.config import EMAIL_CONFIG

print("=" * 60)
print("TESTE DE ENVIO REAL DE EMAIL")
print("=" * 60)
print()

# Verificar configuração
print("1. Verificando configuração...")
print("-" * 60)

if not EMAIL_CONFIG.get("smtp_password"):
    print("   [ERRO] App Password não configurada!")
    print("   Configure em src/config.py")
    sys.exit(1)

print("   [OK] Configuração encontrada:")
print(f"      Servidor: {EMAIL_CONFIG['smtp_server']}")
print(f"      Porta: {EMAIL_CONFIG['smtp_port']}")
print(f"      De: {EMAIL_CONFIG['from_email']}")
print(f"      Para: {EMAIL_CONFIG['to_emails']}")
print()

# Carregar anomalias para teste
print("2. Carregando anomalias para teste...")
print("-" * 60)

try:
    anomalies_file = Path("outputs/anomalies_only.csv")
    if not anomalies_file.exists():
        print("   [AVISO] Arquivo de anomalias não encontrado.")
        print("   Enviando email de teste simples...")
        
        # Teste simples sem anomalias
        result = send_email_alert(
            subject="Teste de Email - Inventory Anomaly Detector",
            message="Este é um teste de envio de email.\n\nSe você recebeu esta mensagem, a configuração está funcionando corretamente!",
            html_message="<h1>Teste de Email</h1><p>Este é um teste de envio de email.</p><p>Se você recebeu esta mensagem, a configuração está funcionando corretamente!</p>"
        )
        
        if result:
            print("   [OK] Email de teste enviado com sucesso!")
        else:
            print("   [ERRO] Falha ao enviar email")
        
        sys.exit(0)
    
    anomalies = pd.read_csv(anomalies_file)
    anomalies['data'] = pd.to_datetime(anomalies['data'])
    
    # Pegar top 3 anomalias
    top_anomalies = anomalies.nlargest(3, 'anomaly_score')
    
    print(f"   [OK] {len(top_anomalies)} anomalias carregadas para teste")
    
except Exception as e:
    print(f"   [ERRO] Erro ao carregar anomalias: {e}")
    sys.exit(1)

print()

# Formatar mensagens
print("3. Formatando mensagens...")
print("-" * 60)

from src.alerts import format_anomaly_alert

text_message = format_anomaly_alert(top_anomalies, max_anomalies=3)
html_message = format_anomaly_email_html(top_anomalies)

print("   [OK] Mensagens formatadas")
print()

# Enviar email
print("4. Enviando email...")
print("-" * 60)
print("   [INFO] Enviando email de teste com anomalias...")
print()

result = send_email_alert(
    subject="Teste de Alerta - Inventory Anomaly Detector",
    message=text_message,
    html_message=html_message
)

print()
if result:
    print("=" * 60)
    print("SUCESSO!")
    print("=" * 60)
    print("Email enviado com sucesso!")
    print(f"Verifique a caixa de entrada de: {EMAIL_CONFIG['to_emails']}")
    print()
    print("Se você recebeu o email, a configuração está funcionando!")
else:
    print("=" * 60)
    print("ERRO")
    print("=" * 60)
    print("Falha ao enviar email. Verifique:")
    print("  1. Se a App Password está correta")
    print("  2. Se a verificação em duas etapas está ativada")
    print("  3. Se o email destinatário está correto")
    print("  4. Verifique a mensagem de erro acima")

