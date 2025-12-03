"""
Interface web Streamlit para visualizar resultados do Inventory Anomaly Detector.
Execute com: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

# Configuração da página
st.set_page_config(
    page_title="Inventory Anomaly Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🔍 Inventory Anomaly Detector")
st.markdown("---")

# Sidebar
st.sidebar.title("📊 Navegação")
page = st.sidebar.radio(
    "Selecione uma página:",
    ["🏠 Dashboard", "📈 Anomalias", "🔮 Previsões", "📄 Relatórios", "⚙️ Executar Pipeline"]
)

# Função para carregar dados
@st.cache_data
def load_data():
    """Carrega dados do pipeline"""
    try:
        df_all = pd.read_csv('outputs/anomalies_detected.csv')
        df_anomalies = pd.read_csv('outputs/anomalies_only.csv')
        df_forecast = pd.read_csv('outputs/forecast_7d.csv')
        return df_all, df_anomalies, df_forecast
    except FileNotFoundError:
        st.error("⚠️ Arquivos não encontrados! Execute o pipeline primeiro.")
        return None, None, None

# Dashboard
if page == "🏠 Dashboard":
    st.header("Dashboard Principal")
    
    df_all, df_anomalies, df_forecast = load_data()
    
    if df_all is not None:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", f"{len(df_all):,}")
        
        with col2:
            n_anomalies = len(df_anomalies) if df_anomalies is not None else 0
            st.metric("Anomalias Detectadas", f"{n_anomalies:,}")
        
        with col3:
            if df_anomalies is not None and len(df_anomalies) > 0:
                pct = (len(df_anomalies) / len(df_all)) * 100
                st.metric("Percentual de Anomalias", f"{pct:.2f}%")
            else:
                st.metric("Percentual de Anomalias", "0%")
        
        with col4:
            if df_anomalies is not None and len(df_anomalies) > 0:
                avg_score = df_anomalies['anomaly_score'].mean()
                st.metric("Score Médio", f"{avg_score:.4f}")
            else:
                st.metric("Score Médio", "N/A")
        
        st.markdown("---")
        
        # Gráfico de distribuição de scores
        if df_anomalies is not None and len(df_anomalies) > 0:
            st.subheader("📊 Distribuição de Scores de Anomalia")
            fig = px.histogram(
                df_anomalies,
                x='anomaly_score',
                nbins=30,
                title="Distribuição dos Scores de Anomalia",
                labels={'anomaly_score': 'Score de Anomalia', 'count': 'Frequência'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Anomalias por produto
        if df_anomalies is not None and len(df_anomalies) > 0:
            st.subheader("📦 Anomalias por Produto")
            col1, col2 = st.columns(2)
            
            with col1:
                anomalies_by_product = df_anomalies['produto_id'].value_counts().reset_index()
                anomalies_by_product.columns = ['Produto', 'Quantidade']
                fig = px.bar(
                    anomalies_by_product,
                    x='Produto',
                    y='Quantidade',
                    title="Anomalias Detectadas por Produto",
                    color='Quantidade',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(anomalies_by_product, use_container_width=True)
        
        # Timeline de anomalias
        if df_anomalies is not None and len(df_anomalies) > 0:
            st.subheader("📅 Timeline de Anomalias")
            df_anomalies['data'] = pd.to_datetime(df_anomalies['data'])
            anomalies_by_date = df_anomalies.groupby(df_anomalies['data'].dt.date).size().reset_index()
            anomalies_by_date.columns = ['Data', 'Quantidade']
            
            fig = px.line(
                anomalies_by_date,
                x='Data',
                y='Quantidade',
                title="Anomalias ao Longo do Tempo",
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# Página de Anomalias
elif page == "📈 Anomalias":
    st.header("Detalhes das Anomalias")
    
    df_all, df_anomalies, df_forecast = load_data()
    
    if df_anomalies is not None and len(df_anomalies) > 0:
        # Filtros
        st.subheader("🔍 Filtros")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            produtos = ['Todos'] + sorted(df_anomalies['produto_id'].unique().tolist())
            produto_selected = st.selectbox("Produto", produtos)
        
        with col2:
            min_score = float(df_anomalies['anomaly_score'].min())
            max_score = float(df_anomalies['anomaly_score'].max())
            score_range = st.slider("Score Mínimo", min_score, max_score, min_score)
        
        with col3:
            st.write("")  # Espaçamento
            st.write("")  # Espaçamento
        
        # Aplicar filtros
        df_filtered = df_anomalies.copy()
        if produto_selected != 'Todos':
            df_filtered = df_filtered[df_filtered['produto_id'] == produto_selected]
        df_filtered = df_filtered[df_filtered['anomaly_score'] >= score_range]
        
        st.markdown(f"**{len(df_filtered)} anomalias encontradas**")
        st.markdown("---")
        
        # Gráfico de consumo vs estoque
        st.subheader("📊 Consumo vs Estoque (Anomalias)")
        fig = px.scatter(
            df_filtered,
            x='consumo_mean',
            y='estoque_mean',
            color='anomaly_score',
            size='anomaly_score',
            hover_data=['data', 'produto_id'],
            title="Anomalias: Consumo vs Estoque",
            color_continuous_scale='Reds',
            labels={
                'consumo_mean': 'Consumo Médio',
                'estoque_mean': 'Estoque Médio',
                'anomaly_score': 'Score'
            }
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de anomalias
        st.subheader("📋 Tabela de Anomalias")
        columns_to_show = ['data', 'produto_id', 'consumo_mean', 'estoque_mean', 'anomaly_score']
        df_display = df_filtered[columns_to_show].copy()
        df_display = df_display.sort_values('anomaly_score', ascending=False)
        df_display.columns = ['Data', 'Produto', 'Consumo Médio', 'Estoque Médio', 'Score']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
        
        # Download
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Anomalias (CSV)",
            data=csv,
            file_name="anomalies_filtered.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Nenhuma anomalia encontrada ou pipeline não executado.")

# Página de Previsões
elif page == "🔮 Previsões":
    st.header("Previsões Prophet")
    
    df_all, df_anomalies, df_forecast = load_data()
    
    if df_forecast is not None:
        st.subheader("📈 Previsões para os Próximos 7 Dias")
        
        # Selecionar produto
        produtos = df_forecast['produto_id'].unique()
        produto_selected = st.selectbox("Selecione um produto", produtos)
        
        df_produto = df_forecast[df_forecast['produto_id'] == produto_selected]
        
        # Gráfico de previsão
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_produto['ds'],
            y=df_produto['yhat'],
            mode='lines+markers',
            name='Previsão',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df_produto['ds'],
            y=df_produto['yhat_lower'],
            mode='lines',
            name='Limite Inferior',
            line=dict(color='lightblue', dash='dash'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df_produto['ds'],
            y=df_produto['yhat_upper'],
            mode='lines',
            name='Limite Superior',
            line=dict(color='lightblue', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(173, 216, 230, 0.3)',
            showlegend=False
        ))
        
        fig.update_layout(
            title=f"Previsão de Consumo - {produto_selected}",
            xaxis_title="Data",
            yaxis_title="Consumo Previsto",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de previsões
        st.subheader("📋 Detalhes das Previsões")
        df_display = df_produto[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        df_display.columns = ['Data', 'Previsão', 'Limite Inferior', 'Limite Superior']
        df_display = df_display.round(2)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("⚠️ Previsões não encontradas. Execute o pipeline primeiro.")

# Página de Relatórios
elif page == "📄 Relatórios":
    st.header("Relatórios PDF")
    
    # Listar PDFs disponíveis
    pdf_dir = Path("outputs/reports")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        pdfs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if pdfs:
            st.subheader("📄 Relatórios Disponíveis")
            
            for pdf in pdfs:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{pdf.name}**")
                    st.caption(f"Criado em: {pd.Timestamp.fromtimestamp(pdf.stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')}")
                    st.caption(f"Tamanho: {pdf.stat().st_size / 1024:.2f} KB")
                
                with col2:
                    with open(pdf, "rb") as f:
                        st.download_button(
                            label="📥 Baixar",
                            data=f.read(),
                            file_name=pdf.name,
                            mime="application/pdf",
                            key=f"download_{pdf.name}"
                        )
                
                with col3:
                    st.write("")  # Espaçamento
                
                st.markdown("---")
        else:
            st.warning("⚠️ Nenhum relatório PDF encontrado.")
    else:
        st.warning("⚠️ Diretório de relatórios não encontrado.")

# Página de Executar Pipeline
elif page == "⚙️ Executar Pipeline":
    st.header("Executar Pipeline")
    
    st.info("⚠️ Esta funcionalidade executa o pipeline completo. Pode levar alguns minutos.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        send_alerts = st.checkbox("Enviar Alertas", value=False)
        send_email = st.checkbox("Enviar Email", value=False)
    
    with col2:
        generate_pdf = st.checkbox("Gerar Relatório PDF", value=True)
    
    if st.button("🚀 Executar Pipeline", type="primary"):
        with st.spinner("Executando pipeline..."):
            try:
                # Importar e executar pipeline
                import importlib.util
                spec = importlib.util.spec_from_file_location("pipeline_module", "src/pipeline.py")
                pipeline_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(pipeline_module)
                
                results = pipeline_module.inventory_anomaly_detection_flow(
                    data_file=None,
                    send_alerts=send_alerts,
                    send_email=send_email,
                    generate_pdf_report=generate_pdf
                )
                
                st.success("✅ Pipeline executado com sucesso!")
                
                # Mostrar resultados
                st.subheader("📊 Resultados")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Registros", results['total_records'])
                
                with col2:
                    st.metric("Anomalias Detectadas", results['anomalies_detected'])
                
                with col3:
                    st.metric("Percentual", f"{results['anomaly_percentage']:.2f}%")
                
                st.json(results)
                
                # Limpar cache para recarregar dados
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao executar pipeline: {str(e)}")
                st.exception(e)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Inventory Anomaly Detector - Pipeline de Detecção de Anomalias"
    "</div>",
    unsafe_allow_html=True
)

