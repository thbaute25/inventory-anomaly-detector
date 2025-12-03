# 🚀 Guia de Deployment Prefect

## 📋 Arquivo `prefect.yaml`

O arquivo `prefect.yaml` contém configurações para deployments do Prefect. É opcional, mas útil para:

- Configurar múltiplos deployments
- Definir schedules (agendamentos)
- Configurar parâmetros padrão
- Organizar tags e metadados

## 🔧 Configurações Disponíveis

### Deployment de Produção

```yaml
name: inventory-anomaly-detection-production
entrypoint: src/pipeline.py:inventory_anomaly_detection_flow
parameters:
  send_alerts: true
  send_email: false  # Configurar para true em produção
  generate_pdf_report: true
```

### Deployment de Teste

```yaml
name: inventory-anomaly-detection-test
entrypoint: src/pipeline.py:inventory_anomaly_detection_flow
parameters:
  send_alerts: false
  send_email: false
  generate_pdf_report: true
```

## 📅 Agendamento (Schedule)

Para agendar execuções automáticas, adicione um schedule:

```yaml
schedule:
  cron: "0 8 * * *"  # Diariamente às 8h
  timezone: "America/Sao_Paulo"
```

Ou usando intervalos:

```yaml
schedule:
  interval: 3600  # A cada hora (em segundos)
```

## 🚀 Como Usar

### 1. Criar Deployment

```bash
# Criar deployment a partir do prefect.yaml
prefect deployment build --name inventory-anomaly-detection-production

# Ou criar diretamente
prefect deployment build src/pipeline.py:inventory_anomaly_detection_flow -n inventory-anomaly-detection
```

### 2. Aplicar Deployment

```bash
prefect deployment apply inventory_anomaly_detection_flow-deployment.yaml
```

### 3. Executar Deployment

```bash
# Executar manualmente
prefect deployment run inventory-anomaly-detection-production

# Ou agendar execução
prefect deployment run inventory-anomaly-detection-production --schedule
```

## 🔄 Execução Local (sem Prefect Server)

Se não quiser usar Prefect Server, execute diretamente:

```bash
py run_pipeline.py
```

Ou:

```bash
py src/pipeline.py
```

## 📊 Monitoramento

### Prefect UI Local

```bash
# Iniciar servidor Prefect local
prefect server start

# Acessar UI em: http://localhost:4200
```

### Prefect Cloud

1. Criar conta em: https://app.prefect.cloud
2. Configurar API key:
   ```bash
   prefect cloud login
   ```
3. Aplicar deployments:
   ```bash
   prefect deployment apply inventory_anomaly_detection_flow-deployment.yaml
   ```

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente

Configure credenciais via variáveis de ambiente:

```bash
export PREFECT_API_URL="http://localhost:4200/api"
export GMAIL_APP_PASSWORD="sua_senha"
export DISCORD_WEBHOOK_URL="seu_webhook"
```

### Work Pools

Criar work pool para execução:

```bash
prefect work-pool create --type process default-agent-pool
prefect work-pool set-concurrency-limit default-agent-pool 5
```

### Agents

Iniciar agent para processar jobs:

```bash
prefect agent start --pool default-agent-pool
```

## 📝 Exemplos de Uso

### Execução Manual

```python
from src.pipeline import inventory_anomaly_detection_flow

results = inventory_anomaly_detection_flow(
    send_alerts=True,
    send_email=True,
    generate_pdf_report=True
)
```

### Via Prefect CLI

```bash
# Executar flow diretamente
prefect flow-run execute inventory-anomaly-detection-production

# Ver status
prefect deployment ls

# Ver logs
prefect flow-run logs <flow-run-id>
```

## 🔒 Segurança

⚠️ **IMPORTANTE**: 
- Não commite credenciais no `prefect.yaml`
- Use variáveis de ambiente para senhas
- Configure `.prefect/` no `.gitignore`

## ✅ Checklist de Deployment

- [ ] Prefect instalado (`pip install prefect`)
- [ ] Prefect Server iniciado (ou Cloud configurado)
- [ ] Work pool criado
- [ ] Agent iniciado (se necessário)
- [ ] Deployment aplicado
- [ ] Teste de execução realizado
- [ ] Schedule configurado (se necessário)

## 📚 Referências

- [Prefect Deployments](https://docs.prefect.io/concepts/deployments/)
- [Prefect Schedules](https://docs.prefect.io/concepts/schedules/)
- [Prefect Work Pools](https://docs.prefect.io/concepts/work-pools/)

