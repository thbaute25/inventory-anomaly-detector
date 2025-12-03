# 🌐 Como Acessar a Interface Web

## ✅ Servidor está rodando!

O servidor Streamlit está ativo e respondendo.

## 🔗 URLs de Acesso

Tente estas URLs no seu navegador:

1. **http://localhost:8501**
2. **http://127.0.0.1:8501**

## 🚀 Como Iniciar Manualmente

Se precisar reiniciar o servidor, use uma das opções abaixo:

### Opção 1: Arquivo Batch (Mais Fácil)
```bash
# Clique duas vezes no arquivo:
run_streamlit.bat
```

### Opção 2: Linha de Comando
```bash
py -m streamlit run app.py
```

### Opção 3: Script Python
```bash
py start_app.py
```

## 🔍 Solução de Problemas

### Problema: "Não é possível acessar esse site"

**Soluções:**

1. **Verifique se o servidor está rodando:**
   ```bash
   # No PowerShell:
   Test-NetConnection -ComputerName localhost -Port 8501
   ```

2. **Verifique se a porta está em uso:**
   ```bash
   netstat -ano | findstr :8501
   ```

3. **Tente uma porta diferente:**
   ```bash
   py -m streamlit run app.py --server.port 8502
   ```
   Depois acesse: http://localhost:8502

4. **Verifique o firewall do Windows:**
   - O Windows pode estar bloqueando a conexão
   - Tente desabilitar temporariamente o firewall para testar

5. **Use o IP 127.0.0.1 ao invés de localhost:**
   - Às vezes `localhost` não resolve corretamente
   - Use: http://127.0.0.1:8501

6. **Verifique se há erros no terminal:**
   - Execute o comando manualmente e veja se há mensagens de erro
   - Verifique se todos os arquivos necessários existem:
     - `app.py`
     - `outputs/anomalies_detected.csv`
     - `outputs/anomalies_only.csv`

## 📋 Pré-requisitos

Certifique-se de que:

- ✅ Python está instalado
- ✅ Streamlit está instalado: `py -m pip install streamlit plotly`
- ✅ Pipeline foi executado pelo menos uma vez: `py run_pipeline.py`
- ✅ Arquivos de saída existem em `outputs/`

## 🎯 Funcionalidades da Interface

A interface web inclui:

1. **Dashboard Principal**
   - Métricas gerais
   - Gráficos interativos
   - Distribuição de anomalias

2. **Detalhes das Anomalias**
   - Filtros por produto e score
   - Gráficos de consumo vs estoque
   - Tabela detalhada

3. **Previsões Prophet**
   - Visualização de previsões de 7 dias
   - Gráficos com intervalos de confiança

4. **Relatórios PDF**
   - Lista de relatórios gerados
   - Download direto

5. **Executar Pipeline**
   - Executar o pipeline completo pela interface

## 💡 Dica

Se ainda não conseguir acessar:

1. Abra o PowerShell como Administrador
2. Execute: `py -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0`
3. Isso permite acesso de qualquer IP (apenas para teste local)

## 📞 Verificação Rápida

Execute este comando para verificar se está tudo OK:

```bash
py -c "import streamlit; print('Streamlit OK'); import pandas; print('Pandas OK'); import plotly; print('Plotly OK')"
```

Se todos mostrarem "OK", as dependências estão corretas!

