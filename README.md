# 🔍 Inventory Anomaly Detector

Pipeline completo em Python para detectar anomalias em consumo e estoque usando modelos de Machine Learning e orquestração com Prefect.

---

## 📋 Índice

- [Introdução](#-introdução)
- [Arquitetura](#-arquitetura)
- [Como Rodar](#-como-rodar)
- [Prints e Exemplos](#-prints-e-exemplos)
- [Sprints](#-sprints)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias](#-tecnologias)
- [Configuração](#-configuração)

---

## 🎯 Introdução

O **Inventory Anomaly Detector** é um sistema completo de detecção de anomalias em dados de estoque e consumo. O projeto utiliza técnicas avançadas de Machine Learning para identificar padrões anômalos que podem indicar problemas operacionais, fraudes ou oportunidades de otimização.

### Objetivos do Projeto

1. ✅ Ler dados de estoque e consumo de um CSV
2. ✅ Limpar e preparar os dados com Pandas
3. ✅ Criar features de série temporal (lags, agregações)
4. ✅ Treinar modelos Prophet para previsão de consumo
5. ✅ Usar Isolation Forest para detectar anomalias
6. ✅ Organizar tudo em um pipeline Prefect
7. ✅ Enviar alertas via webhook (Discord/Teams) e email
8. ✅ Gerar relatório PDF com gráficos e tabelas

### Características Principais

- 🔄 **Pipeline Orquestrado**: Fluxo completo automatizado com Prefect
- 🤖 **ML Avançado**: Prophet para previsões e Isolation Forest para anomalias
- 📊 **Relatórios Automáticos**: PDF com gráficos e análises detalhadas
- 🔔 **Sistema de Alertas**: Notificações via Discord, Teams e Email
- 📈 **Análise Temporal**: Features de lag e agregações para séries temporais
- 🛡️ **Robustez**: Retry automático, tratamento de erros e validações

---

## 🏗️ Arquitetura

### Visão Geral do Pipeline

O pipeline segue uma arquitetura modular e sequencial, onde cada etapa processa os dados e passa para a próxima:

```
┌─────────────────────────────────────────────────────────────────┐
│              INVENTORY ANOMALY DETECTION PIPELINE               │
└─────────────────────────────────────────────────────────────────┘

1. 📥 CARREGAMENTO DE DADOS
   └─> load_inventory_data()
       ├─> Validação de schema
       ├─> Parsing de datas
       └─> Separação de dados de consumo

2. 🧹 LIMPEZA DE DADOS
   └─> clean_consumo()
       ├─> Remoção de outliers (IQR)
       ├─> Preenchimento de valores faltantes
       └─> Remoção de duplicatas

3. 🔧 ENGENHARIA DE FEATURES
   └─> create_lag_features()
       ├─> Lags: 1, 7, 30 dias
       ├─> Rolling statistics (média, std)
       └─> Features temporais (dia da semana, mês)

4. 📊 AGREGAÇÃO DE DADOS
   └─> aggregate_daily_by_item()
       ├─> Agregação diária por produto
       ├─> Média de consumo e estoque
       └─> Preenchimento de datas faltantes

5. 🔮 PREVISÃO COM PROPHET
   └─> train_models_by_product()
       ├─> Modelo Prophet por produto
       ├─> Previsão de 7 dias
       └─> Salvamento de modelos (.pkl)

6. 🚨 DETECÇÃO DE ANOMALIAS
   └─> detect_anomalies_consumo_estoque()
       ├─> Isolation Forest
       ├─> Score de anomalia
       └─> Classificação binária

7. 🔔 ENVIO DE ALERTAS
   └─> send_anomaly_alerts()
       ├─> Discord (webhook)
       ├─> Microsoft Teams (webhook)
       └─> Email (SMTP)

8. 📄 GERAÇÃO DE RELATÓRIO PDF
   └─> generate_anomaly_report_pdf()
       ├─> Gráficos de anomalias
       ├─> Tabelas detalhadas
       └─> Resumo executivo
```

### Módulos do Projeto

```
src/
├── config.py              # Configurações centralizadas
├── data_loader.py         # Carregamento e validação de dados
├── data_cleaning/         # Limpeza de dados
│   └── data_cleaner.py
├── data_aggregator.py     # Agregação de dados
├── features.py            # Engenharia de features
├── forecasting.py         # Modelos Prophet
├── anomalies.py           # Detecção de anomalias (Isolation Forest)
├── alerts.py              # Sistema de alertas
├── reports.py             # Geração de relatórios PDF
└── pipeline.py            # Pipeline Prefect (orquestração)
```

### Fluxo de Dados

```
CSV Input
    ↓
[Data Loader] → DataFrame
    ↓
[Data Cleaner] → DataFrame Limpo
    ↓
[Feature Engineering] → DataFrame com Features
    ↓
[Data Aggregator] → DataFrame Agregado
    ↓
[Prophet Models] → Previsões (7 dias)
    ↓
[Isolation Forest] → Anomalias Detectadas
    ↓
[Alerts] → Notificações (Discord/Teams/Email)
    ↓
[PDF Report] → Relatório Final
```

### Tecnologias Utilizadas

| Categoria | Tecnologia | Versão |
|-----------|-----------|--------|
| **Linguagem** | Python | 3.9+ |
| **Data Processing** | Pandas | ≥2.0.0 |
| **ML - Forecasting** | Prophet | ≥1.1.0 |
| **ML - Anomaly Detection** | Scikit-learn | ≥1.3.0 |
| **Orchestration** | Prefect | ≥2.10.0 |
| **PDF Generation** | ReportLab | ≥4.0.0 |
| **Visualization** | Matplotlib | ≥3.7.0 |
| **Model Persistence** | Joblib | ≥1.3.0 |
| **Data Format** | PyArrow | ≥14.0.0 |

---

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

### Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/inventory-anomaly-detector.git
cd inventory-anomaly-detector
```

2. **Crie um ambiente virtual (recomendado):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure os alertas (opcional):**
   - Edite `src/config.py` com suas credenciais
   - Veja `CONFIGURACAO_ALERTAS.md` para mais detalhes
   - Veja `COMO_CRIAR_APP_PASSWORD.md` para configurar email Gmail

### Executando o Pipeline

#### Opção 1: Executar via Script Python

```bash
python run_pipeline.py
```

#### Opção 2: Executar via Prefect Flow

```python
from src.pipeline import inventory_anomaly_detection_flow

# Executar pipeline completo
results = inventory_anomaly_detection_flow(
    data_file=None,              # Usar arquivo padrão (data/inventory_data.csv)
    send_alerts=True,            # Enviar alertas
    send_email=False,            # Enviar email (requer configuração)
    generate_pdf_report=True     # Gerar relatório PDF
)

print(results)
```

#### Opção 3: Executar via Prefect CLI

```bash
# Executar flow diretamente
prefect deployment run inventory-anomaly-detection-production

# Ou executar localmente
prefect flow run src/pipeline.py:inventory_anomaly_detection_flow
```

#### Opção 4: Executar Notebooks Jupyter

Para análise exploratória e testes:

```bash
# Iniciar Jupyter
jupyter notebook

# Abrir notebooks:
# - 01_eda.ipynb (Análise Exploratória)
# - 02_prophet.ipynb (Treinamento Prophet)
# - 03_anomalias.ipynb (Detecção de Anomalias)
```

### Gerar Dados de Teste

Se você não tiver dados, pode gerar dados fake:

```bash
python generate_fake_data.py
```

Isso criará `data/inventory_data.csv` com dados sintéticos.

### Parâmetros do Pipeline

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `data_file` | `Path\|None` | `None` | Caminho do CSV. Se `None`, usa `data/inventory_data.csv` |
| `send_alerts` | `bool` | `True` | Enviar alertas via webhook |
| `send_email` | `bool` | `False` | Enviar alertas por email |
| `generate_pdf_report` | `bool` | `True` | Gerar relatório PDF |

---

## 📸 Prints e Exemplos

### 1. Execução do Pipeline

```
============================================================
INICIANDO PIPELINE DE DETECÇÃO DE ANOMALIAS
============================================================
[INFO] Carregando dados de: data/inventory_data.csv
[INFO] Dados carregados: 1000 registros
[INFO] Limpando dados de consumo...
[INFO] Features criadas: lag_1, lag_7, lag_30
[INFO] Treinando modelos Prophet para 5 produtos...
[INFO] Modelo PROD_001 treinado com sucesso
[INFO] Modelo PROD_002 treinado com sucesso
...
[INFO] Detectando anomalias com Isolation Forest...
[INFO] 45 anomalias detectadas (4.5% dos registros)
[INFO] Enviando alertas...
[INFO] Relatório PDF gerado: outputs/reports/anomaly_report.pdf
============================================================
PIPELINE CONCLUÍDO COM SUCESSO
============================================================
Total de registros: 1000
Anomalias detectadas: 45 (4.50%)
Modelos Prophet treinados: 5
Alertas enviados: {'discord': True, 'teams': True}
Relatório PDF: outputs/reports/anomaly_report_20251203_104036.pdf
```

### 2. Estrutura de Saídas

```
outputs/
├── models/
│   ├── isolation_forest_model.pkl.gz
│   ├── prophet_model_PROD_001.pkl.gz
│   ├── prophet_model_PROD_002.pkl.gz
│   └── ...
├── reports/
│   └── anomaly_report_20251203_104036.pdf
├── temp_charts/
│   ├── chart_1_score_distribution.png
│   ├── chart_2_consumo_estoque.png
│   ├── chart_3_anomalies_by_product.png
│   └── chart_4_anomalies_by_date.png
├── anomalies_detected.csv
├── anomalies_detected.parquet
├── anomalies_only.csv
├── consumo_with_features.csv
├── daily_aggregated_by_item.csv
├── forecast_7d.csv
└── forecast_30d.csv
```

### 3. Exemplo de Alerta Discord

```
============================================================
ALERTA: 45 ANOMALIA(S) DETECTADA(S)
============================================================

Estatísticas:
  - Score médio: 0.6234
  - Score máximo: 0.8921

------------------------------------------------------------
DETALHES DAS ANOMALIAS:
------------------------------------------------------------

[1] Anomalia Detectada
----------------------------------------
  Data: 2024-11-15
  Produto: PROD_001
  Consumo: 1250.50
  Estoque: 450.00
  Score: 0.8921 (CRÍTICA)

[2] Anomalia Detectada
----------------------------------------
  Data: 2024-11-20
  Produto: PROD_003
  Consumo: 980.25
  Estoque: 120.00
  Score: 0.7456 (ALTA)

...
```

### 4. Exemplo de Relatório PDF

O relatório PDF contém:

- **Capa**: Título e data de geração
- **Resumo Executivo**: 
  - Total de registros analisados
  - Número de anomalias detectadas
  - Percentual de anomalias
  - Score médio e máximo
- **Gráficos**:
  - Distribuição de scores de anomalia
  - Consumo vs Estoque (com destaque para anomalias)
  - Anomalias por produto
  - Anomalias por data
- **Tabela Detalhada**: Lista completa de anomalias com todas as informações

### 5. Exemplo de Resultados do Pipeline

```python
{
    "total_records": 1000,
    "anomalies_detected": 45,
    "anomaly_percentage": 4.5,
    "prophet_models_trained": 5,
    "alert_results": {
        "discord": True,
        "teams": True,
        "email": False
    },
    "pdf_report_path": "outputs/reports/anomaly_report_20251203_104036.pdf",
    "anomalies_file": "outputs/anomalies_detected.csv",
    "anomalies_only_file": "outputs/anomalies_only.csv"
}
```

### 6. Visualização de Anomalias (Notebook)

Os notebooks Jupyter incluem visualizações interativas:

- Gráficos de séries temporais com anomalias destacadas
- Distribuições de consumo e estoque
- Heatmaps de anomalias por produto e data
- Análises estatísticas detalhadas

---

## 🏃 Sprints

### Sprint 1: Estrutura e Configuração Inicial
**Objetivo:** Criar estrutura base do projeto

- ✅ Criar estrutura de pastas (`src/`, `data/`, `outputs/`)
- ✅ Criar `.gitignore`
- ✅ Criar `requirements.txt`
- ✅ Criar `src/config.py` com configurações centralizadas
- ✅ Criar script `generate_fake_data.py` para gerar dados de teste

**Arquivos Criados:**
- `src/config.py`
- `generate_fake_data.py`
- `.gitignore`
- `requirements.txt`

---

### Sprint 2: Carregamento e Validação de Dados
**Objetivo:** Implementar leitura e validação de dados CSV

- ✅ Criar `src/data_loader.py`
- ✅ Implementar `load_inventory_data()` - carregar dados do CSV
- ✅ Implementar `load_raw_consumo()` - extrair dados de consumo
- ✅ Implementar `validate_data()` - validar schema e tipos
- ✅ Criar notebook `01_eda.ipynb` para análise exploratória

**Arquivos Criados:**
- `src/data_loader.py`
- `01_eda.ipynb`

---

### Sprint 3: Limpeza e Preparação de Dados
**Objetivo:** Implementar pipeline de limpeza de dados

- ✅ Criar `src/data_cleaning/data_cleaner.py`
- ✅ Implementar `clean_consumo()` - remover outliers, preencher faltantes
- ✅ Implementar `save_processed()` - salvar dados processados
- ✅ Adicionar tratamento de duplicatas e valores inválidos

**Arquivos Criados:**
- `src/data_cleaning/data_cleaner.py`
- `src/data_cleaning/__init__.py`

---

### Sprint 4: Engenharia de Features
**Objetivo:** Criar features de série temporal

- ✅ Criar `src/features.py`
- ✅ Implementar `create_lag_features()` - lags de 1, 7, 30 dias
- ✅ Implementar `create_rolling_features()` - estatísticas móveis
- ✅ Implementar `create_temporal_features()` - features temporais
- ✅ Criar `src/data_aggregator.py` para agregação diária

**Arquivos Criados:**
- `src/features.py`
- `src/data_aggregator.py`

---

### Sprint 5: Previsão com Prophet
**Objetivo:** Treinar modelos Prophet para previsão de consumo

- ✅ Criar `src/forecasting.py`
- ✅ Implementar `train_prophet_model()` - treinar modelo por produto
- ✅ Implementar `train_models_by_product()` - treinar todos os produtos
- ✅ Implementar `make_forecast()` - fazer previsões de 7 e 30 dias
- ✅ Implementar `save_model()` e `load_model()` - persistência
- ✅ Criar notebook `02_prophet.ipynb` para análise de previsões

**Arquivos Criados:**
- `src/forecasting.py`
- `02_prophet.ipynb`

---

### Sprint 6: Detecção de Anomalias
**Objetivo:** Implementar detecção de anomalias com Isolation Forest

- ✅ Criar `src/anomalies.py`
- ✅ Implementar `train_isolation_forest()` - treinar modelo
- ✅ Implementar `detect_anomalies_consumo_estoque()` - detectar anomalias
- ✅ Implementar `save_anomaly_model()` - salvar modelo
- ✅ Criar notebook `03_anomalias.ipynb` para análise de anomalias

**Arquivos Criados:**
- `src/anomalies.py`
- `03_anomalias.ipynb`

---

### Sprint 7: Sistema de Alertas
**Objetivo:** Implementar envio de alertas via webhook e email

- ✅ Criar `src/alerts.py`
- ✅ Implementar `send_discord_alert()` - webhook Discord
- ✅ Implementar `send_teams_alert()` - webhook Teams
- ✅ Implementar `send_email_alert()` - email SMTP
- ✅ Implementar `format_anomaly_alert()` - formatação de mensagens
- ✅ Implementar `send_anomaly_alerts()` - envio automático
- ✅ Criar scripts de teste (`test_alerts.py`, `test_email_real.py`)

**Arquivos Criados:**
- `src/alerts.py`
- `test_alerts.py`
- `test_alerts_with_mock.py`
- `test_email_real.py`
- `CONFIGURACAO_ALERTAS.md`
- `COMO_CRIAR_APP_PASSWORD.md`

---

### Sprint 8: Geração de Relatórios PDF
**Objetivo:** Criar sistema de geração de relatórios PDF

- ✅ Criar `src/reports.py`
- ✅ Implementar `create_anomaly_charts()` - gerar gráficos
- ✅ Implementar `create_anomaly_table_data()` - preparar tabelas
- ✅ Implementar `generate_anomaly_report_pdf()` - gerar PDF completo
- ✅ Criar script de teste (`test_generate_report.py`)

**Arquivos Criados:**
- `src/reports.py`
- `test_generate_report.py`
- `verify_pdf.py`
- `view_anomalies_table.py`

---

### Sprint 9: Pipeline Prefect
**Objetivo:** Orquestrar todo o pipeline com Prefect

- ✅ Criar `src/pipeline.py`
- ✅ Implementar 8 tasks Prefect:
  - `task_load_data()`
  - `task_clean_data()`
  - `task_create_features()`
  - `task_aggregate_data()`
  - `task_train_prophet_models()`
  - `task_detect_anomalies()`
  - `task_send_alerts()`
  - `task_generate_report()`
- ✅ Implementar flow principal `inventory_anomaly_detection_flow()`
- ✅ Criar `prefect.yaml` com configurações de deployment
- ✅ Criar scripts de execução e validação

**Arquivos Criados:**
- `src/pipeline.py`
- `prefect.yaml`
- `run_pipeline.py`
- `test_pipeline_prefect.py`
- `validate_prefect_yaml.py`
- `PIPELINE_PREFECT.md`
- `PIPELINE_ORDER.md`
- `PIPELINE_FLOW_DIAGRAM.md`
- `DEPLOYMENT_PREFECT.md`

---

## 📁 Estrutura do Projeto

```
inventory-anomaly-detector/
├── 📂 src/                          # Código fonte principal
│   ├── __init__.py
│   ├── config.py                    # Configurações centralizadas
│   ├── data_loader.py               # Carregamento de dados
│   ├── data_aggregator.py           # Agregação de dados
│   ├── features.py                  # Engenharia de features
│   ├── forecasting.py               # Modelos Prophet
│   ├── anomalies.py                 # Detecção de anomalias
│   ├── alerts.py                    # Sistema de alertas
│   ├── reports.py                   # Geração de relatórios PDF
│   ├── pipeline.py                  # Pipeline Prefect
│   ├── 📂 data_cleaning/
│   │   ├── __init__.py
│   │   └── data_cleaner.py
│   ├── 📂 pipeline/
│   │   └── __init__.py
│   └── 📂 alerts/
│       └── __init__.py
│
├── 📂 data/                         # Dados de entrada
│   └── inventory_data.csv
│
├── 📂 outputs/                      # Saídas do pipeline
│   ├── 📂 models/                   # Modelos treinados (.pkl)
│   ├── 📂 reports/                  # Relatórios PDF
│   ├── 📂 temp_charts/             # Gráficos temporários
│   ├── anomalies_detected.csv
│   ├── anomalies_only.csv
│   ├── consumo_with_features.csv
│   ├── daily_aggregated_by_item.csv
│   └── forecast_*.csv
│
├── 📂 tests/                        # Testes unitários
│   └── __init__.py
│
├── 📄 01_eda.ipynb                  # Notebook: Análise Exploratória
├── 📄 02_prophet.ipynb              # Notebook: Previsões Prophet
├── 📄 03_anomalias.ipynb            # Notebook: Detecção de Anomalias
│
├── 📄 generate_fake_data.py         # Gerar dados sintéticos
├── 📄 run_pipeline.py               # Script principal de execução
├── 📄 test_*.py                     # Scripts de teste
│
├── 📄 requirements.txt              # Dependências Python
├── 📄 prefect.yaml                  # Configuração Prefect
├── 📄 .gitignore                    # Arquivos ignorados pelo Git
│
└── 📄 README.md                     # Este arquivo
```

---

## ⚙️ Configuração

### Configuração de Alertas

Edite `src/config.py` para configurar:

#### Discord Webhook
```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
```

#### Microsoft Teams Webhook
```python
TEAMS_WEBHOOK_URL = "https://outlook.office.com/webhook/..."
```

#### Email (Gmail)
```python
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "seu-email@gmail.com",
    "smtp_password": "sua-app-password",  # App Password do Gmail
    "from_email": "seu-email@gmail.com",
    "to_emails": ["destinatario@gmail.com"],
    "use_tls": True,
}
```

**📖 Guias de Configuração:**
- `CONFIGURACAO_ALERTAS.md` - Configuração completa de alertas
- `COMO_CRIAR_APP_PASSWORD.md` - Como criar App Password do Gmail

### Configuração de Modelos

Edite `src/config.py` para ajustar parâmetros:

#### Prophet
```python
PROPHET_CONFIG = {
    "yearly_seasonality": True,
    "weekly_seasonality": True,
    "daily_seasonality": False,
    "seasonality_mode": "multiplicative",
    "changepoint_prior_scale": 0.05,
    "interval_width": 0.95,
}
```

#### Isolation Forest
```python
ISOLATION_FOREST_CONFIG = {
    "contamination": 0.1,  # 10% de anomalias esperadas
    "random_state": 42,
    "n_estimators": 100,
}
```

---

## 📚 Documentação Adicional

- [`PIPELINE_PREFECT.md`](PIPELINE_PREFECT.md) - Documentação completa do pipeline Prefect
- [`PIPELINE_ORDER.md`](PIPELINE_ORDER.md) - Ordem de execução das tasks
- [`PIPELINE_FLOW_DIAGRAM.md`](PIPELINE_FLOW_DIAGRAM.md) - Diagrama visual do flow
- [`DEPLOYMENT_PREFECT.md`](DEPLOYMENT_PREFECT.md) - Guia de deployment Prefect
- [`CONFIGURACAO_ALERTAS.md`](CONFIGURACAO_ALERTAS.md) - Configuração de alertas
- [`COMO_CRIAR_APP_PASSWORD.md`](COMO_CRIAR_APP_PASSWORD.md) - Criar App Password Gmail

---

## 🧪 Testes

Execute os scripts de teste para validar funcionalidades:

```bash
# Testar detecção de anomalias
python test_anomaly_detection.py

# Testar alertas (mock)
python test_alerts_with_mock.py

# Testar email real
python test_email_real.py

# Testar geração de PDF
python test_generate_report.py

# Testar pipeline Prefect
python test_pipeline_prefect.py
```

---

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

---

## 👤 Autor

Desenvolvido como parte do projeto **Inventory Anomaly Detector**.

---

## 🙏 Agradecimentos

- **Prophet** - Facebook para o modelo de previsão
- **Prefect** - Para a orquestração de pipelines
- **Scikit-learn** - Para algoritmos de ML
- **Pandas** - Para processamento de dados

---

**✨ Projeto completo e funcional! Pronto para detectar anomalias em estoque e consumo.**
