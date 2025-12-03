# 🔄 Ordem do Pipeline Prefect

## Fluxo Linear de Execução

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE COMPLETO                        │
└─────────────────────────────────────────────────────────────┘

1. LOAD ──────────────────────────────────────────────────────┐
   │                                                           │
   │ task_load_data()                                          │
   │ • Carrega CSV de estoque e consumo                        │
   │ • Valida estrutura                                        │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
                              │
                              ▼
2. CLEAN ─────────────────────────────────────────────────────┐
   │                                                           │
   │ task_clean_data()                                         │
   │ • Remove outliers                                         │
   │ • Preenche valores faltantes                              │
   │ • Remove duplicatas                                       │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
                              │
                              ▼
3. FEATURES ──────────────────────────────────────────────────┐
   │                                                           │
   │ task_create_features()                                    │
   │ • Cria lags (1, 7, 30 dias)                              │
   │ • Features temporais                                      │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
                              │
                              ▼
4. FORECAST ──────────────────────────────────────────────────┐
   │                                                           │
   │ task_train_prophet_models()                              │
   │ • Treina Prophet por produto                              │
   │ • Gera previsões de 7 dias                                │
   │ • Salva modelos                                           │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
                              │
                              ▼
5. ANOMALIES ─────────────────────────────────────────────────┐
   │                                                           │
   │ task_detect_anomalies()                                  │
   │ • Treina Isolation Forest                                 │
   │ • Detecta anomalias                                       │
   │ • Salva resultados                                        │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
                              │
                              ▼
6. ALERTS ───────────────────────────────────────────────────┐
   │                                                           │
   │ task_send_alerts() [OPCIONAL]                             │
   │ • Filtra anomalias críticas                               │
   │ • Envia Discord/Teams/Email                              │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
                              │
                              ▼
7. PDF ───────────────────────────────────────────────────────┐
   │                                                           │
   │ task_generate_report() [OPCIONAL]                         │
   │ • Gera gráficos                                           │
   │ • Cria tabelas                                            │
   │ • Salva PDF                                               │
   │                                                           │
   └───────────────────────────────────────────────────────────┘
```

## 📋 Sequência de Execução

### Etapa 1: LOAD
```python
df, consumo_df = task_load_data(data_file)
```
**Saída:** Dados brutos carregados

### Etapa 2: CLEAN
```python
consumo_limpo = task_clean_data(consumo_df)
```
**Saída:** Dados limpos e preparados

### Etapa 3: FEATURES
```python
consumo_com_features = task_create_features(consumo_limpo, df)
```
**Saída:** Dados com features de lag criadas

### Etapa 4: FORECAST
```python
prophet_models = task_train_prophet_models(consumo_com_features)
```
**Saída:** Modelos Prophet treinados + previsões

### Etapa 5: ANOMALIES
```python
df_with_anomalies, anomaly_model = task_detect_anomalies(df_aggregated)
```
**Saída:** Anomalias detectadas + modelo Isolation Forest

### Etapa 6: ALERTS
```python
alert_results = task_send_alerts(df_with_anomalies, send_email=send_email)
```
**Saída:** Resultados do envio de alertas

### Etapa 7: PDF
```python
pdf_path = task_generate_report(df_with_anomalies)
```
**Saída:** Relatório PDF gerado

## 🔗 Dependências

```
LOAD
 │
 ├─> CLEAN (usa consumo_df)
 │     │
 │     └─> FEATURES (usa consumo_limpo + df)
 │           │
 │           └─> FORECAST (usa consumo_com_features)
 │
 └─> AGGREGATE (usa df) [etapa auxiliar]
       │
       └─> ANOMALIES (usa df_aggregated)
             │
             ├─> ALERTS (usa df_with_anomalies)
             │
             └─> PDF (usa df_with_anomalies)
```

## ⚡ Execução Paralela Possível

Algumas etapas podem ser executadas em paralelo:

```
LOAD
 │
 ├─> CLEAN ──> FEATURES ──> FORECAST
 │
 └─> AGGREGATE ──> ANOMALIES ──> ALERTS
                      │
                      └─> PDF
```

## 📊 Tempo de Execução Estimado

| Etapa | Tempo Estimado | Dependência |
|-------|----------------|-------------|
| LOAD | ~1s | - |
| CLEAN | ~1s | LOAD |
| FEATURES | ~1s | CLEAN |
| AGGREGATE | ~1s | LOAD |
| FORECAST | ~30-60s | FEATURES |
| ANOMALIES | ~5-10s | AGGREGATE |
| ALERTS | ~2-5s | ANOMALIES |
| PDF | ~5-10s | ANOMALIES |

**Total:** ~50-90 segundos

## ✅ Ordem Implementada

A ordem atual do pipeline segue exatamente:
```
LOAD → CLEAN → FEATURES → FORECAST → ANOMALIES → ALERTS → PDF
```

**Status:** ✅ Implementado e testado com sucesso!

