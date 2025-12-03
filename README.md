# Inventory Anomaly Detector

Pipeline completo em Python para detectar anomalias em consumo e estoque.

## Estrutura do Projeto

```
inventory-anomaly-detector/
├── src/
│   ├── data_loading/      # Leitura de dados CSV
│   ├── data_cleaning/     # Limpeza e preparação de dados
│   ├── feature_engineering/  # Features de série temporal
│   ├── models/            # Modelos Prophet e Isolation Forest
│   ├── pipeline/          # Pipeline Prefect
│   ├── alerts/            # Alertas via webhook
│   └── reporting/         # Geração de relatórios PDF
├── data/                  # Arquivos CSV de entrada
├── outputs/               # Relatórios PDF e saídas
├── tests/                 # Testes unitários
└── requirements.txt       # Dependências do projeto
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

Em desenvolvimento - aguardando implementação das sprints.
