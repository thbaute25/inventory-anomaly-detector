"""
Interface web Streamlit moderna e elegante para Inventory Anomaly Detector.
Execute com: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# PALETA DE CORES
# ============================================================================
COLORS = {
    'dark_blue': '#0B263B',
    'orange': '#C4731F',
    'light_gray': '#9DA3AC',
    'medium_blue': '#496483',
    'white': '#FFFFFF',
    'dark_gray': '#2C3E50',
    'light_bg': '#F5F7FA'
}

# ============================================================================
# CONFIGURAÇÃO E ESTILO
# ============================================================================

st.set_page_config(
    page_title="Inventory Anomaly Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado com a paleta de cores
st.markdown(f"""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Estilo geral */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .main {{
        padding-top: 1rem;
        background-color: {COLORS['light_bg']};
    }}
    
    /* Título principal */
    h1 {{
        color: {COLORS['dark_blue']};
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }}
    
    h2 {{
        color: {COLORS['dark_blue']};
        font-weight: 600;
        border-bottom: 2px solid {COLORS['orange']};
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }}
    
    h3 {{
        color: {COLORS['medium_blue']};
        font-weight: 600;
    }}
    
    /* Cards de métricas elegantes */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
        padding: 1.8rem;
        border-radius: 12px;
        color: {COLORS['white']};
        box-shadow: 0 8px 16px rgba(11, 38, 59, 0.2);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid {COLORS['orange']};
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(11, 38, 59, 0.3);
    }}
    
    .metric-card-danger {{
        background: linear-gradient(135deg, {COLORS['orange']} 0%, #E67E22 100%);
        border-left-color: {COLORS['dark_blue']};
    }}
    
    .metric-card-success {{
        background: linear-gradient(135deg, {COLORS['medium_blue']} 0%, {COLORS['dark_blue']} 100%);
        border-left-color: {COLORS['orange']};
    }}
    
    .metric-card-warning {{
        background: linear-gradient(135deg, {COLORS['light_gray']} 0%, {COLORS['medium_blue']} 100%);
        border-left-color: {COLORS['orange']};
    }}
    
    .metric-card-info {{
        background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
        border-left-color: {COLORS['orange']};
    }}
    
    /* Sidebar elegante */
    .css-1d391kg {{
        background: linear-gradient(180deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
    }}
    
    [data-testid="stSidebar"] .css-1d391kg {{
        background: transparent;
    }}
    
    [data-testid="stSidebar"] label {{
        color: {COLORS['white']} !important;
        font-weight: 500;
    }}
    
    [data-testid="stSidebar"] [class*="stRadio"] label {{
        color: {COLORS['white']} !important;
        padding: 0.5rem;
        border-radius: 8px;
        transition: background 0.3s ease;
    }}
    
    [data-testid="stSidebar"] [class*="stRadio"] label:hover {{
        background: rgba(255, 255, 255, 0.1);
    }}
    
    /* Botões elegantes */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['orange']} 0%, #E67E22 100%);
        color: {COLORS['white']};
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(196, 115, 31, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(196, 115, 31, 0.4);
        background: linear-gradient(135deg, #E67E22 0%, {COLORS['orange']} 100%);
    }}
    
    /* Tabs elegantes */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {COLORS['light_bg']};
        padding: 0.5rem;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 12px 24px;
        background-color: {COLORS['white']};
        color: {COLORS['medium_blue']};
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['orange']} 0%, #E67E22 100%);
        color: {COLORS['white']};
    }}
    
    /* Alertas elegantes */
    .stAlert {{
        border-radius: 12px;
        border-left: 4px solid {COLORS['orange']};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    
    /* Dataframe elegante */
    .dataframe {{
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}
    
    /* Badge de status elegante */
    .status-badge {{
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .status-critical {{
        background: linear-gradient(135deg, {COLORS['orange']} 0%, #E67E22 100%);
        color: {COLORS['white']};
        box-shadow: 0 2px 8px rgba(196, 115, 31, 0.3);
    }}
    
    .status-high {{
        background: linear-gradient(135deg, #E67E22 0%, {COLORS['orange']} 100%);
        color: {COLORS['white']};
        box-shadow: 0 2px 8px rgba(196, 115, 31, 0.2);
    }}
    
    .status-medium {{
        background: linear-gradient(135deg, {COLORS['light_gray']} 0%, {COLORS['medium_blue']} 100%);
        color: {COLORS['white']};
    }}
    
    /* Header com gradiente elegante */
    .main-header {{
        background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: {COLORS['white']};
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(11, 38, 59, 0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(196, 115, 31, 0.2) 0%, transparent 70%);
        border-radius: 50%;
    }}
    
    .main-header h1 {{
        color: {COLORS['white']};
        margin: 0;
        padding: 0;
        border: none;
        position: relative;
        z-index: 1;
    }}
    
    .main-header p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
        position: relative;
        z-index: 1;
    }}
    
    /* Cards de conteúdo */
    .content-card {{
        background: {COLORS['white']};
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border-top: 3px solid {COLORS['orange']};
    }}
    
    /* Animações suaves */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.6s ease-out;
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    .slide-in {{
        animation: slideIn 0.5s ease-out;
    }}
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['light_bg']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {COLORS['orange']} 0%, #E67E22 100%);
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, #E67E22 0%, {COLORS['orange']} 100%);
    }}
    
    /* Inputs elegantes */
    .stSelectbox label, .stSlider label, .stCheckbox label {{
        color: {COLORS['dark_blue']};
        font-weight: 500;
    }}
    
    /* Footer elegante */
    .footer {{
        background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
        padding: 2rem;
        border-radius: 15px;
        color: {COLORS['white']};
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 4px 12px rgba(11, 38, 59, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

@st.cache_data
def load_data():
    """Carrega dados do pipeline"""
    try:
        df_all = pd.read_csv('outputs/anomalies_detected.csv')
        df_anomalies = pd.read_csv('outputs/anomalies_only.csv')
        df_forecast = pd.read_csv('outputs/forecast_7d.csv')
        return df_all, df_anomalies, df_forecast
    except FileNotFoundError:
        return None, None, None

def get_severity_badge(score):
    """Retorna badge de severidade baseado no score"""
    if score >= 0.7:
        return '<span class="status-badge status-critical">CRÍTICA</span>'
    elif score >= 0.6:
        return '<span class="status-badge status-high">ALTA</span>'
    else:
        return '<span class="status-badge status-medium">MÉDIA</span>'

def create_metric_card(title, value, delta=None, card_type="info"):
    """Cria um card de métrica estilizado"""
    card_class = f"metric-card-{card_type}" if card_type != "info" else "metric-card"
    delta_html = ""
    if delta:
        delta_html = f'<div style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">{delta}</div>'
    
    return f"""
    <div class="{card_class} fade-in" style="text-align: center;">
        <div style="font-size: 0.95rem; opacity: 0.95; margin-bottom: 0.8rem; font-weight: 500;">{title}</div>
        <div style="font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">{value}</div>
        {delta_html}
    </div>
    """

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown(f"""
<div class="main-header fade-in">
    <h1>🔍 Inventory Anomaly Detector</h1>
    <p>Sistema Inteligente de Detecção de Anomalias em Estoque e Consumo</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1.5rem; background: rgba(255, 255, 255, 0.1); border-radius: 12px; margin-bottom: 2rem; border: 2px solid rgba(255, 255, 255, 0.2);">
    <h2 style="color: {COLORS['white']}; margin: 0; font-weight: 700;">📊 Navegação</h2>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Selecione uma página:",
    ["🏠 Dashboard", "📈 Anomalias", "🔮 Previsões", "📄 Relatórios", "⚙️ Executar Pipeline"],
    label_visibility="collapsed"
)

# Informações na sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid {COLORS['orange']};">
    <h3 style="color: {COLORS['white']}; margin-top: 0;">📊 Informações</h3>
    <p style="color: {COLORS['white']}; opacity: 0.9; margin: 0.5rem 0;">
        <strong>Data/Hora:</strong><br>
        {datetime.now().strftime('%d/%m/%Y')}<br>
        {datetime.now().strftime('%H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# DASHBOARD
# ============================================================================

if page == "🏠 Dashboard":
    st.markdown("## 📊 Dashboard Principal")
    st.markdown("---")
    
    df_all, df_anomalies, df_forecast = load_data()
    
    if df_all is not None and df_anomalies is not None:
        # Métricas principais em cards estilizados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card(
                "📦 Total de Registros",
                f"{len(df_all):,}",
                "Registros analisados",
                "success"
            ), unsafe_allow_html=True)
        
        with col2:
            n_anomalies = len(df_anomalies)
            st.markdown(create_metric_card(
                "🚨 Anomalias Detectadas",
                f"{n_anomalies:,}",
                f"{(n_anomalies/len(df_all)*100):.2f}% do total",
                "danger"
            ), unsafe_allow_html=True)
        
        with col3:
            if len(df_anomalies) > 0:
                avg_score = df_anomalies['anomaly_score'].mean()
                st.markdown(create_metric_card(
                    "📊 Score Médio",
                    f"{avg_score:.4f}",
                    "Score de anomalia",
                    "warning"
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card(
                    "📊 Score Médio",
                    "N/A",
                    "Sem anomalias",
                    "warning"
                ), unsafe_allow_html=True)
        
        with col4:
            if len(df_anomalies) > 0:
                max_score = df_anomalies['anomaly_score'].max()
                st.markdown(create_metric_card(
                    "⚠️ Score Máximo",
                    f"{max_score:.4f}",
                    "Anomalia mais crítica",
                    "danger"
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card(
                    "⚠️ Score Máximo",
                    "N/A",
                    "Sem anomalias",
                    "danger"
                ), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos principais em tabs
        tab1, tab2, tab3 = st.tabs(["📈 Distribuição de Scores", "📦 Anomalias por Produto", "📅 Timeline"])
        
        with tab1:
            if len(df_anomalies) > 0:
                fig = px.histogram(
                    df_anomalies,
                    x='anomaly_score',
                    nbins=30,
                    title="Distribuição dos Scores de Anomalia",
                    labels={'anomaly_score': 'Score de Anomalia', 'count': 'Frequência'},
                    color_discrete_sequence=[COLORS['orange']]
                )
                fig.update_layout(
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12, family='Inter'),
                    title_font_size=20,
                    title_font_color=COLORS['dark_blue'],
                    xaxis=dict(gridcolor=COLORS['light_gray'], gridwidth=1),
                    yaxis=dict(gridcolor=COLORS['light_gray'], gridwidth=1)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                anomalies_by_product = df_anomalies['produto_id'].value_counts().reset_index()
                anomalies_by_product.columns = ['Produto', 'Quantidade']
                
                fig = px.bar(
                    anomalies_by_product,
                    x='Produto',
                    y='Quantidade',
                    title="Anomalias Detectadas por Produto",
                    color='Quantidade',
                    color_continuous_scale=[[0, COLORS['medium_blue']], [1, COLORS['orange']]],
                    labels={'Quantidade': 'Nº de Anomalias'}
                )
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12, family='Inter'),
                    title_font_color=COLORS['dark_blue'],
                    xaxis=dict(gridcolor=COLORS['light_gray']),
                    yaxis=dict(gridcolor=COLORS['light_gray'])
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📋 Detalhes")
                st.dataframe(
                    anomalies_by_product,
                    use_container_width=True,
                    hide_index=True
                )
        
        with tab3:
            if len(df_anomalies) > 0:
                df_anomalies['data'] = pd.to_datetime(df_anomalies['data'])
                anomalies_by_date = df_anomalies.groupby(df_anomalies['data'].dt.date).size().reset_index()
                anomalies_by_date.columns = ['Data', 'Quantidade']
                
                fig = px.line(
                    anomalies_by_date,
                    x='Data',
                    y='Quantidade',
                    title="Anomalias ao Longo do Tempo",
                    markers=True,
                    color_discrete_sequence=[COLORS['orange']]
                )
                fig.update_traces(
                    line=dict(width=3, color=COLORS['orange']),
                    marker=dict(size=8, color=COLORS['dark_blue'])
                )
                fig.update_layout(
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12, family='Inter'),
                    title_font_color=COLORS['dark_blue'],
                    xaxis_title="Data",
                    yaxis_title="Número de Anomalias",
                    xaxis=dict(gridcolor=COLORS['light_gray']),
                    yaxis=dict(gridcolor=COLORS['light_gray'])
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Top 10 anomalias mais críticas
        st.markdown("---")
        st.markdown("## 🔥 Top 10 Anomalias Mais Críticas")
        
        top_anomalies = df_anomalies.nlargest(10, 'anomaly_score')[
            ['data', 'produto_id', 'consumo_mean', 'estoque_mean', 'anomaly_score']
        ].copy()
        top_anomalies.columns = ['Data', 'Produto', 'Consumo Médio', 'Estoque Médio', 'Score']
        top_anomalies['Severidade'] = top_anomalies['Score'].apply(
            lambda x: 'CRÍTICA' if x >= 0.7 else ('ALTA' if x >= 0.6 else 'MÉDIA')
        )
        
        st.dataframe(
            top_anomalies,
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.error("⚠️ Arquivos não encontrados! Execute o pipeline primeiro.")
        st.info("💡 Execute: `py run_pipeline.py` para gerar os dados")

# ============================================================================
# ANOMALIAS
# ============================================================================

elif page == "📈 Anomalias":
    st.markdown("## 📈 Detalhes das Anomalias")
    st.markdown("---")
    
    df_all, df_anomalies, df_forecast = load_data()
    
    if df_anomalies is not None and len(df_anomalies) > 0:
        # Filtros em card elegante
        st.markdown(f"""
        <div class="content-card fade-in">
            <h3 style="margin-top: 0; color: {COLORS['dark_blue']};">🔍 Filtros de Busca</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            produtos = ['Todos'] + sorted(df_anomalies['produto_id'].unique().tolist())
            produto_selected = st.selectbox("📦 Produto", produtos)
        
        with col2:
            min_score = float(df_anomalies['anomaly_score'].min())
            max_score = float(df_anomalies['anomaly_score'].max())
            score_range = st.slider("📊 Score Mínimo", min_score, max_score, min_score, 0.01)
        
        with col3:
            severity_filter = st.selectbox("⚠️ Severidade", ['Todas', 'CRÍTICA', 'ALTA', 'MÉDIA'])
        
        # Aplicar filtros
        df_filtered = df_anomalies.copy()
        if produto_selected != 'Todos':
            df_filtered = df_filtered[df_filtered['produto_id'] == produto_selected]
        df_filtered = df_filtered[df_filtered['anomaly_score'] >= score_range]
        
        if severity_filter != 'Todas':
            if severity_filter == 'CRÍTICA':
                df_filtered = df_filtered[df_filtered['anomaly_score'] >= 0.7]
            elif severity_filter == 'ALTA':
                df_filtered = df_filtered[(df_filtered['anomaly_score'] >= 0.6) & (df_filtered['anomaly_score'] < 0.7)]
            else:
                df_filtered = df_filtered[df_filtered['anomaly_score'] < 0.6]
        
        st.success(f"✅ **{len(df_filtered)} anomalias encontradas** com os filtros aplicados")
        st.markdown("---")
        
        # Gráfico de consumo vs estoque
        st.markdown("### 📊 Visualização: Consumo vs Estoque")
        
        fig = px.scatter(
            df_filtered,
            x='consumo_mean',
            y='estoque_mean',
            color='anomaly_score',
            size='anomaly_score',
            hover_data=['data', 'produto_id'],
            title="Anomalias: Consumo vs Estoque",
            color_continuous_scale=[[0, COLORS['medium_blue']], [0.5, COLORS['orange']], [1, '#E67E22']],
            labels={
                'consumo_mean': 'Consumo Médio',
                'estoque_mean': 'Estoque Médio',
                'anomaly_score': 'Score de Anomalia'
            },
            size_max=20
        )
        fig.update_layout(
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, family='Inter'),
            title_font_color=COLORS['dark_blue'],
            xaxis=dict(gridcolor=COLORS['light_gray']),
            yaxis=dict(gridcolor=COLORS['light_gray'])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de anomalias
        st.markdown("### 📋 Tabela Detalhada de Anomalias")
        columns_to_show = ['data', 'produto_id', 'consumo_mean', 'estoque_mean', 'anomaly_score']
        df_display = df_filtered[columns_to_show].copy()
        df_display = df_display.sort_values('anomaly_score', ascending=False)
        df_display.columns = ['Data', 'Produto', 'Consumo Médio', 'Estoque Médio', 'Score']
        df_display['Severidade'] = df_display['Score'].apply(
            lambda x: 'CRÍTICA' if x >= 0.7 else ('ALTA' if x >= 0.6 else 'MÉDIA')
        )
        
        st.dataframe(
            df_display,
            use_container_width=True,
            height=400
        )
        
        # Download
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Anomalias Filtradas (CSV)",
            data=csv,
            file_name=f"anomalies_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Nenhuma anomalia encontrada ou pipeline não executado.")

# ============================================================================
# PREVISÕES
# ============================================================================

elif page == "🔮 Previsões":
    st.markdown("## 🔮 Previsões Prophet")
    st.markdown("---")
    
    df_all, df_anomalies, df_forecast = load_data()
    
    if df_forecast is not None:
        st.markdown("### 📈 Previsões para os Próximos 7 Dias")
        
        # Selecionar produto
        produtos = df_forecast['produto_id'].unique()
        produto_selected = st.selectbox("Selecione um produto", produtos)
        
        df_produto = df_forecast[df_forecast['produto_id'] == produto_selected]
        
        # Gráfico de previsão estilizado
        fig = go.Figure()
        
        # Intervalo de confiança
        fig.add_trace(go.Scatter(
            x=df_produto['ds'],
            y=df_produto['yhat_upper'],
            mode='lines',
            name='Limite Superior',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df_produto['ds'],
            y=df_produto['yhat_lower'],
            mode='lines',
            name='Intervalo de Confiança',
            line=dict(color='rgba(0,0,0,0)'),
            fillcolor=f'rgba(196, 115, 31, 0.2)',
            fill='tonexty',
            showlegend=True
        ))
        
        # Previsão principal
        fig.add_trace(go.Scatter(
            x=df_produto['ds'],
            y=df_produto['yhat'],
            mode='lines+markers',
            name='Previsão',
            line=dict(color=COLORS['orange'], width=3),
            marker=dict(size=10, color=COLORS['dark_blue'])
        ))
        
        fig.update_layout(
            title=f"Previsão de Consumo - {produto_selected}",
            xaxis_title="Data",
            yaxis_title="Consumo Previsto",
            height=600,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, family='Inter'),
            title_font_color=COLORS['dark_blue'],
            xaxis=dict(gridcolor=COLORS['light_gray']),
            yaxis=dict(gridcolor=COLORS['light_gray']),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de previsões
        st.markdown("### 📋 Detalhes das Previsões")
        df_display = df_produto[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        df_display.columns = ['Data', 'Previsão', 'Limite Inferior', 'Limite Superior']
        df_display = df_display.round(2)
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ Previsões não encontradas. Execute o pipeline primeiro.")

# ============================================================================
# RELATÓRIOS
# ============================================================================

elif page == "📄 Relatórios":
    st.markdown("## 📄 Relatórios PDF")
    st.markdown("---")
    
    pdf_dir = Path("outputs/reports")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        pdfs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if pdfs:
            st.markdown("### 📚 Relatórios Disponíveis")
            
            for idx, pdf in enumerate(pdfs):
                st.markdown(f"""
                <div class="content-card fade-in">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin-top: 0; color: {COLORS['dark_blue']};">📄 {pdf.name}</h3>
                            <p style="color: {COLORS['medium_blue']}; margin: 0.5rem 0;">
                                📅 Criado em: {pd.Timestamp.fromtimestamp(pdf.stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')}<br>
                                💾 Tamanho: {pdf.stat().st_size / 1024:.2f} KB
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with open(pdf, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório",
                        data=f.read(),
                        file_name=pdf.name,
                        mime="application/pdf",
                        key=f"download_{idx}",
                        use_container_width=True
                    )
                
                if idx < len(pdfs) - 1:
                    st.markdown("---")
        else:
            st.warning("⚠️ Nenhum relatório PDF encontrado.")
    else:
        st.warning("⚠️ Diretório de relatórios não encontrado.")

# ============================================================================
# EXECUTAR PIPELINE
# ============================================================================

elif page == "⚙️ Executar Pipeline":
    st.markdown("## ⚙️ Executar Pipeline")
    st.markdown("---")
    
    st.info("💡 Esta funcionalidade executa o pipeline completo de detecção de anomalias. O processo pode levar alguns minutos.")
    
    st.markdown(f"""
    <div class="content-card fade-in">
        <h3 style="margin-top: 0; color: {COLORS['dark_blue']};">⚙️ Configurações do Pipeline</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Configurações")
        send_alerts = st.checkbox("🔔 Enviar Alertas", value=False, help="Envia alertas via webhook (Discord/Teams)")
        send_email = st.checkbox("📧 Enviar Email", value=False, help="Envia alertas por email")
    
    with col2:
        st.markdown("### 📊 Saídas")
        generate_pdf = st.checkbox("📄 Gerar Relatório PDF", value=True, help="Gera relatório PDF com gráficos e tabelas")
    
    st.markdown("---")
    
    if st.button("🚀 Executar Pipeline Completo", type="primary", use_container_width=True):
        with st.spinner("⏳ Executando pipeline... Isso pode levar alguns minutos."):
            try:
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
                
                # Mostrar resultados em cards
                st.markdown("### 📊 Resultados da Execução")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Registros", f"{results['total_records']:,}")
                
                with col2:
                    st.metric("Anomalias Detectadas", f"{results['anomalies_detected']:,}")
                
                with col3:
                    st.metric("Percentual", f"{results['anomaly_percentage']:.2f}%")
                
                st.json(results)
                
                # Limpar cache para recarregar dados
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao executar pipeline: {str(e)}")
                with st.expander("🔍 Detalhes do Erro"):
                    st.exception(e)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div class="footer fade-in">
    <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
        <strong>Inventory Anomaly Detector</strong>
    </p>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        Sistema Inteligente de Detecção de Anomalias<br>
        Desenvolvido com ❤️ usando Python, Streamlit e Plotly
    </p>
</div>
""", unsafe_allow_html=True)
