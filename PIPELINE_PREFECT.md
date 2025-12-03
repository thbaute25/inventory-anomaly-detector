# Pipeline Prefect - Inventory Anomaly Detector

## 📋 Visão Geral

O pipeline Prefect orquestra todas as etapas do sistema de detecção de anomalias, desde o carregamento de dados até a geração de relatórios e envio de alertas.

## 🔄 Estrutura do Flow

O flow `inventory_anomaly_detection_flow` executa as seguintes etapas em sequência:

```
┌─────────────────────────────────────────────────────────────┐
│  inventory_anomaly_detection_flow                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. task_load_data()                                        │
│     └─> Carrega dados de estoque e consumo                 │
│                                                             │
│  2. task_clean_data()                                        │
│     └─> Limpa e prepara dados de consumo                   │
│                                                             │
│  3. task_create_features()                                   │
│     └─> Cria features de série temporal (lags)             │
│                                                             │
│  4. task_aggregate_data()                                    │
│     └─> Agrega dados diários por item                      │
│                                                             │
│  5. task_train_prophet_models()                               │
│     └─> Treina modelos Prophet para cada produto           │
│                                                             │
│  6. task_detect_anomalies()                                  │
│     └─> Detecta anomalias com Isolation Forest             │
│                                                             │
│  7. task_send_alerts() [OPCIONAL]                           │
│     └─> Envia alertas via Discord/Teams/Email             │
│                                                             │
│  8. task_generate_report() [OPCIONAL]                       │
│     └─> Gera relatório PDF com gráficos e tabelas          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Tasks Implementadas

### 1. `task_load_data`
- **Função:** Carrega dados de estoque e consumo do CSV
- **Retries:** 2 tentativas
- **Retry Delay:** 60 segundos
- **Retorna:** Tupla (DataFrame completo, DataFrame de consumo)

### 2. `task_clean_data`
- **Função:** Limpa dados de consumo (remove outliers, preenche valores faltantes)
- **Retries:** 2 tentativas
- **Retry Delay:** 60 segundos
- **Retorna:** DataFrame limpo

### 3. `task_create_features`
- **Função:** Cria features de lag (1, 7, 30 dias)
- **Retries:** 2 tentativas
- **Retry Delay:** 60 segundos
- **Retorna:** DataFrame com features criadas

### 4. `task_aggregate_data`
- **Função:** Agrega dados diários por produto
- **Retries:** 2 tentativas
- **Retry Delay:** 60 segundos
- **Retorna:** DataFrame agregado

### 5. `task_train_prophet_models`
- **Função:** Treina modelos Prophet para cada produto
- **Retries:** 2 tentativas
- **Retry Delay:** 60 segundos
- **Retorna:** Dicionário com modelos treinados
- **Saídas:** Previsões de 7 dias salvas em CSV

### 6. `task_detect_anomalies`
- **Função:** Detecta anomalias usando Isolation Forest
- **Retries:** 2 tentativas
- **Retry Delay:** 60 segundos
- **Retorna:** Tupla (DataFrame com anomalias, modelo treinado)
- **Saídas:** 
  - Modelo salvo em `outputs/models/isolation_forest_model.pkl.gz`
  - Anomalias em CSV e Parquet

### 7. `task_send_alerts`
- **Função:** Envia alertas de anomalias críticas
- **Retries:** 1 tentativa
- **Retry Delay:** 30 segundos
- **Retorna:** Dicionário com resultados do envio
- **Suporta:** Discord, Teams, Email

### 8. `task_generate_report`
- **Função:** Gera relatório PDF completo
- **Retries:** 1 tentativa
- **Retry Delay:** 30 segundos
- **Retorna:** Caminho do arquivo PDF gerado
- **Inclui:** Gráficos e tabelas de anomalias

## 🚀 Como Usar

### Execução Local (Script Python)

```python
import sys
from pathlib import Path
import importlib.util

# Importar pipeline
spec = importlib.util.spec_from_file_location("pipeline_module", "src/pipeline.py")
pipeline_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline_module)

inventory_anomaly_detection_flow = pipeline_module.inventory_anomaly_detection_flow

# Executar pipeline
results = inventory_anomaly_detection_flow(
    data_file=None,  # Usar arquivo padrão
    send_alerts=True,  # Enviar alertas
    send_email=False,  # Enviar email
    generate_pdf_report=True  # Gerar PDF
)

print(results)
```

### Execução via Script

```bash
# Executar pipeline completo
py run_pipeline.py

# Ou executar diretamente o módulo
py src/pipeline.py
```

### Execução com Prefect CLI

```bash
# Executar flow localmente
prefect deployment run inventory-anomaly-detection-flow

# Ou criar deployment
prefect deployment build src/pipeline.py:inventory_anomaly_detection_flow -n inventory-anomaly-detection
prefect deployment apply inventory_anomaly_detection_flow-deployment.yaml
```

## ⚙️ Parâmetros do Flow

### `inventory_anomaly_detection_flow()`

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `data_file` | `Optional[Path]` | `None` | Caminho do arquivo CSV. Se None, usa `data/inventory_data.csv` |
| `send_alerts` | `bool` | `True` | Se True, envia alertas de anomalias |
| `send_email` | `bool` | `False` | Se True, envia alertas por email |
| `generate_pdf_report` | `bool` | `True` | Se True, gera relatório PDF |

## 📊 Retorno do Flow

O flow retorna um dicionário com os seguintes resultados:

```python
{
    "total_records": 3655,  # Total de registros analisados
    "anomalies_detected": 366,  # Número de anomalias detectadas
    "anomaly_percentage": 10.01,  # Percentual de anomalias
    "prophet_models_trained": 5,  # Número de modelos Prophet treinados
    "alert_results": {  # Resultados do envio de alertas
        "discord": True/False,
        "teams": True/False,
        "email": True/False
    },
    "pdf_report_path": "outputs/reports/anomaly_report_20240101_120000.pdf",
    "anomalies_file": "outputs/anomalies_detected.csv",
    "anomalies_only_file": "outputs/anomalies_only.csv"
}
```

## 🔧 Configuração

### Configurações do Prefect

As configurações estão em `src/config.py`:

```python
PREFECT_CONFIG = {
    "flow_name": "inventory_anomaly_detection",
    "retries": 2,
    "retry_delay_seconds": 60,
}
```

### Configurações de Alertas

```python
ALERT_CONFIG = {
    "discord_webhook_url": None,  # Configurar quando necessário
    "teams_webhook_url": None,  # Configurar quando necessário
    "min_anomaly_score": 0.7,  # Score mínimo para alerta
}
```

## 📝 Logging

O pipeline usa o sistema de logging do Prefect. Todos os logs são capturados automaticamente e podem ser visualizados:

- **Localmente:** No console durante a execução
- **Prefect Cloud/Server:** Na interface web do Prefect

## 🔄 Retry e Tratamento de Erros

- **Tasks principais:** 2 tentativas com delay de 60 segundos
- **Tasks de alerta/relatório:** 1 tentativa com delay de 30 segundos
- **Logs detalhados:** Todos os erros são logados

## 📈 Monitoramento

### Visualizar Execuções

```bash
# Iniciar servidor Prefect local
prefect server start

# Acessar UI em: http://localhost:4200
```

### Ver Logs

```python
from prefect import get_client

# Obter logs de uma execução
async with get_client() as client:
    logs = await client.read_logs(flow_run_id="...")
```

## 🎯 Exemplos de Uso

### Exemplo 1: Pipeline Completo

```python
results = inventory_anomaly_detection_flow(
    send_alerts=True,
    send_email=True,
    generate_pdf_report=True
)
```

### Exemplo 2: Apenas Detecção (sem alertas)

```python
results = inventory_anomaly_detection_flow(
    send_alerts=False,
    send_email=False,
    generate_pdf_report=True
)
```

### Exemplo 3: Com Arquivo Customizado

```python
from pathlib import Path

results = inventory_anomaly_detection_flow(
    data_file=Path("data/meus_dados.csv"),
    send_alerts=True,
    generate_pdf_report=True
)
```

## ✅ Checklist de Execução

- [ ] Dados CSV disponíveis em `data/inventory_data.csv`
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Configurações de alertas (se necessário)
- [ ] Diretórios de saída criados (`outputs/`, `outputs/models/`, `outputs/reports/`)

## 🐛 Troubleshooting

### Erro: "Cannot import pipeline"
- **Solução:** Use o script `run_pipeline.py` ou importe diretamente do arquivo

### Erro: "Data file not found"
- **Solução:** Verifique se o arquivo existe em `data/inventory_data.csv`

### Erro: "Prefect flow not found"
- **Solução:** Execute `prefect server start` ou use execução local

## 📚 Referências

- [Documentação Prefect](https://docs.prefect.io/)
- [Prefect Flows](https://docs.prefect.io/concepts/flows/)
- [Prefect Tasks](https://docs.prefect.io/concepts/tasks/)

