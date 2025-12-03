# Guia de Configuração de Alertas

Este guia explica como configurar os alertas para Discord, Teams e Email.

## 📧 Configuração de Email (Gmail)

### Passo 1: Criar App Password

O Gmail requer uma "App Password" (senha de aplicativo) para autenticação SMTP. Siga estes passos:

1. **Ative a verificação em duas etapas** (se ainda não tiver):
   - Acesse: https://myaccount.google.com/security
   - Ative "Verificação em duas etapas"

2. **Crie uma App Password**:
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "Email" como aplicativo
   - Selecione "Outro (nome personalizado)" como dispositivo
   - Digite um nome (ex: "Inventory Anomaly Detector")
   - Clique em "Gerar"
   - **Copie a senha gerada** (16 caracteres, sem espaços)

3. **Configure no arquivo `src/config.py`**:
   ```python
   EMAIL_CONFIG = {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "smtp_username": "baute.thomas25@gmail.com",
       "smtp_password": "SUA_APP_PASSWORD_AQUI",  # Cole a senha de 16 caracteres aqui
       "from_email": "baute.thomas25@gmail.com",
       "to_emails": ["baute.thomas25@gmail.com"],  # Adicione mais emails se necessário
       "use_tls": True,
   }
   ```

### Testar Email

Execute:
```bash
py test_alerts.py
```

Ou teste diretamente:
```python
from src.alerts import send_email_alert

send_email_alert(
    subject="Teste de Alerta",
    message="Este é um teste de envio de email.",
    html_message="<h1>Teste</h1><p>Este é um teste.</p>"
)
```

---

## 💬 Configuração do Discord Webhook

### Passo 1: Criar Webhook no Discord

1. Abra o Discord e entre no servidor desejado
2. Vá em **Configurações do Servidor** (ícone de engrenagem)
3. Clique em **Integrações** > **Webhooks**
4. Clique em **Novo Webhook** ou **Criar Webhook**
5. Configure:
   - Nome do webhook (ex: "Anomaly Alerts")
   - Canal onde os alertas serão enviados
   - Opcional: Avatar personalizado
6. Clique em **Copiar URL do Webhook**
7. Cole a URL no arquivo `src/config.py`:
   ```python
   ALERT_CONFIG = {
       "discord_webhook_url": "https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI",
       ...
   }
   ```

### Testar Discord

Execute:
```bash
py test_alerts.py
```

---

## 👥 Configuração do Microsoft Teams Webhook

### Passo 1: Criar Webhook no Teams

1. Abra o Microsoft Teams
2. Vá no canal onde deseja receber os alertas
3. Clique nos **3 pontos** (...) ao lado do nome do canal
4. Selecione **Conectores**
5. Procure por **"Incoming Webhook"**
6. Clique em **Configurar**
7. Dê um nome ao webhook (ex: "Anomaly Alerts")
8. Opcional: Adicione uma imagem
9. Clique em **Criar**
10. **Copie a URL do webhook** gerada
11. Cole a URL no arquivo `src/config.py`:
    ```python
    ALERT_CONFIG = {
        "teams_webhook_url": "https://outlook.office.com/webhook/SEU_WEBHOOK_AQUI",
        ...
    }
    ```

### Testar Teams

Execute:
```bash
py test_alerts.py
```

---

## 🔒 Segurança

⚠️ **IMPORTANTE**: 
- **NUNCA** commite senhas ou webhooks no Git!
- O arquivo `src/config.py` pode conter informações sensíveis
- Considere usar variáveis de ambiente para produção:
  ```python
  import os
  EMAIL_CONFIG = {
      "smtp_password": os.getenv("GMAIL_APP_PASSWORD"),
      ...
  }
  ```

---

## ✅ Verificar Configuração

Execute o script de teste:
```bash
py test_alerts.py
```

Este script verificará:
- ✅ Se as configurações estão preenchidas
- ✅ Se as mensagens são formatadas corretamente
- ✅ Preview das mensagens que serão enviadas

Para testar envio real (com mock desabilitado):
```bash
py test_alerts_with_mock.py
```

---

## 📝 Exemplo de Uso

Depois de configurar, use assim:

```python
from src.alerts import send_anomaly_alerts
import pandas as pd

# Carregar anomalias
anomalies = pd.read_csv('outputs/anomalies_only.csv')

# Filtrar anomalias críticas
critical = anomalies[anomalies['anomaly_score'] >= 0.7]

# Enviar alertas
results = send_anomaly_alerts(
    critical,
    produto_id="TODOS",
    min_score=0.7,
    send_discord=True,  # Enviar para Discord
    send_teams=False,   # Não enviar para Teams
    send_email=False    # Não enviar email (use send_anomaly_email para email)
)

print(f"Alertas enviados: {results}")
```

