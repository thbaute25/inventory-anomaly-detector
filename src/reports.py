"""
Módulo para geração de relatórios PDF com gráficos e tabelas de anomalias.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import io

from src.config import REPORT_CONFIG, REPORT_OUTPUT_DIR


def create_anomaly_charts(
    df_with_anomalies: pd.DataFrame,
    anomalies: pd.DataFrame,
    output_path: Optional[Path] = None
) -> List[Path]:
    """
    Cria gráficos de anomalias e salva em arquivos temporários.
    
    Args:
        df_with_anomalies: DataFrame completo com flag de anomalia.
        anomalies: DataFrame apenas com anomalias detectadas.
        output_path: Diretório para salvar gráficos temporários. Se None, usa temp.
    
    Returns:
        Lista de caminhos dos arquivos de gráficos criados.
    """
    if output_path is None:
        output_path = Path("outputs/temp_charts")
    output_path.mkdir(parents=True, exist_ok=True)
    
    chart_paths = []
    
    # 1. Gráfico: Distribuição de scores de anomalia
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df_with_anomalies['anomaly_score'].dropna(), bins=50, alpha=0.7, edgecolor='black', color='steelblue')
    ax.axvline(df_with_anomalies['anomaly_score'].mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {df_with_anomalies["anomaly_score"].mean():.4f}')
    ax.set_title('Distribuição de Scores de Anomalia', fontsize=14, fontweight='bold')
    ax.set_xlabel('Anomaly Score', fontsize=12)
    ax.set_ylabel('Frequência', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    chart_path_1 = output_path / "chart_1_score_distribution.png"
    plt.savefig(chart_path_1, dpi=300, bbox_inches='tight')
    plt.close()
    chart_paths.append(chart_path_1)
    
    # 2. Gráfico: Consumo vs Estoque (scatter plot com anomalias destacadas)
    if len(anomalies) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Dados normais
        normal_data = df_with_anomalies[df_with_anomalies['is_anomaly'] == False]
        if len(normal_data) > 0:
            ax.scatter(
                normal_data['consumo_mean'] if 'consumo_mean' in normal_data.columns else normal_data.get('consumo', normal_data.get('y', [])),
                normal_data['estoque_mean'] if 'estoque_mean' in normal_data.columns else normal_data.get('estoque', []),
                alpha=0.5, s=30, color='lightblue', label='Normal'
            )
        
        # Anomalias
        consumo_col = 'consumo_mean' if 'consumo_mean' in anomalies.columns else anomalies.columns[anomalies.columns.str.contains('consumo', case=False)][0] if any(anomalies.columns.str.contains('consumo', case=False)) else 'consumo'
        estoque_col = 'estoque_mean' if 'estoque_mean' in anomalies.columns else anomalies.columns[anomalies.columns.str.contains('estoque', case=False)][0] if any(anomalies.columns.str.contains('estoque', case=False)) else 'estoque'
        
        if consumo_col in anomalies.columns and estoque_col in anomalies.columns:
            ax.scatter(
                anomalies[consumo_col],
                anomalies[estoque_col],
                color='red', marker='x', s=100, linewidths=2, label='Anomalias'
            )
        
        ax.set_title('Consumo vs Estoque - Anomalias Destacadas', fontsize=14, fontweight='bold')
        ax.set_xlabel('Consumo', fontsize=12)
        ax.set_ylabel('Estoque', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        chart_path_2 = output_path / "chart_2_consumo_estoque.png"
        plt.savefig(chart_path_2, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(chart_path_2)
    
    # 3. Gráfico: Anomalias por produto
    if len(anomalies) > 0 and 'produto_id' in anomalies.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        anomalies_by_product = anomalies['produto_id'].value_counts().head(10)
        ax.barh(range(len(anomalies_by_product)), anomalies_by_product.values, color='coral')
        ax.set_yticks(range(len(anomalies_by_product)))
        ax.set_yticklabels(anomalies_by_product.index)
        ax.set_title('Top 10 Produtos com Mais Anomalias', fontsize=14, fontweight='bold')
        ax.set_xlabel('Número de Anomalias', fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        chart_path_3 = output_path / "chart_3_anomalies_by_product.png"
        plt.savefig(chart_path_3, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(chart_path_3)
    
    # 4. Gráfico: Anomalias por data
    if len(anomalies) > 0 and 'data' in anomalies.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        anomalies = anomalies.copy()  # Evitar warning do pandas
        anomalies['data'] = pd.to_datetime(anomalies['data'])
        anomalies_by_date = anomalies.groupby(anomalies['data'].dt.date).size().sort_values(ascending=False).head(10)
        ax.bar(range(len(anomalies_by_date)), anomalies_by_date.values, color='salmon')
        ax.set_xticks(range(len(anomalies_by_date)))
        ax.set_xticklabels([str(d) for d in anomalies_by_date.index], rotation=45, ha='right')
        ax.set_title('Top 10 Datas com Mais Anomalias', fontsize=14, fontweight='bold')
        ax.set_ylabel('Número de Anomalias', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        chart_path_4 = output_path / "chart_4_anomalies_by_date.png"
        plt.savefig(chart_path_4, dpi=300, bbox_inches='tight')
        plt.close()
        chart_paths.append(chart_path_4)
    
    return chart_paths


def create_anomaly_table_data(
    anomalies: pd.DataFrame,
    max_rows: int = 50
) -> List[List[str]]:
    """
    Prepara dados para tabela de anomalias no PDF.
    
    Args:
        anomalies: DataFrame com anomalias.
        max_rows: Número máximo de linhas na tabela.
    
    Returns:
        Lista de listas com dados da tabela (incluindo cabeçalho).
    """
    if len(anomalies) == 0:
        return [["Data", "Produto", "Consumo", "Estoque", "Score"], ["Nenhuma anomalia detectada", "", "", "", ""]]
    
    # Ordenar por score (maior primeiro)
    anomalies_sorted = anomalies.nlargest(max_rows, 'anomaly_score')
    
    # Preparar colunas
    table_data = []
    
    # Cabeçalho
    header = ["Data", "Produto", "Consumo", "Estoque", "Score"]
    table_data.append(header)
    
    # Dados
    for _, row in anomalies_sorted.iterrows():
        # Data
        date_val = ""
        if 'data' in row:
            date_val = str(row['data'])[:10] if pd.notna(row['data']) else ""
        elif 'ds' in row:
            date_val = str(row['ds'])[:10] if pd.notna(row['ds']) else ""
        
        # Produto
        produto_val = str(row['produto_id']) if 'produto_id' in row and pd.notna(row['produto_id']) else ""
        
        # Consumo
        consumo_val = ""
        if 'consumo_mean' in row:
            consumo_val = f"{row['consumo_mean']:.2f}" if pd.notna(row['consumo_mean']) else ""
        elif 'consumo' in row:
            consumo_val = f"{row['consumo']:.2f}" if pd.notna(row['consumo']) else ""
        elif 'y' in row:
            consumo_val = f"{row['y']:.2f}" if pd.notna(row['y']) else ""
        
        # Estoque
        estoque_val = ""
        if 'estoque_mean' in row:
            estoque_val = f"{row['estoque_mean']:.2f}" if pd.notna(row['estoque_mean']) else ""
        elif 'estoque' in row:
            estoque_val = f"{row['estoque']:.2f}" if pd.notna(row['estoque']) else ""
        
        # Score
        score_val = f"{row['anomaly_score']:.4f}" if 'anomaly_score' in row and pd.notna(row['anomaly_score']) else ""
        
        table_data.append([date_val, produto_val, consumo_val, estoque_val, score_val])
    
    return table_data


def generate_anomaly_report_pdf(
    df_with_anomalies: pd.DataFrame,
    anomalies: pd.DataFrame,
    output_path: Optional[Path] = None,
    title: Optional[str] = None,
    include_charts: bool = True
) -> Path:
    """
    Gera relatório PDF completo com gráficos e tabelas de anomalias.
    
    Args:
        df_with_anomalies: DataFrame completo com flag de anomalia.
        anomalies: DataFrame apenas com anomalias detectadas.
        output_path: Caminho do arquivo PDF de saída. Se None, usa padrão.
        title: Título do relatório. Se None, usa config padrão.
        include_charts: Se True, inclui gráficos no PDF.
    
    Returns:
        Caminho do arquivo PDF gerado.
    """
    # Preparar caminho de saída
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = REPORT_OUTPUT_DIR / f"anomaly_report_{timestamp}.pdf"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Criar documento PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    
    # Conteúdo do PDF
    story = []
    
    # Título
    report_title = title or REPORT_CONFIG.get("title", "Relatório de Anomalias")
    story.append(Paragraph(report_title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Data de geração
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    story.append(Paragraph(f"<i>Gerado em: {date_str}</i>", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Resumo executivo
    story.append(Paragraph("Resumo Executivo", heading_style))
    
    total_records = len(df_with_anomalies)
    total_anomalies = len(anomalies)
    anomaly_percentage = (total_anomalies / total_records * 100) if total_records > 0 else 0
    
    summary_text = f"""
    <b>Total de registros analisados:</b> {total_records:,}<br/>
    <b>Anomalias detectadas:</b> {total_anomalies:,} ({anomaly_percentage:.2f}%)<br/>
    """
    
    if total_anomalies > 0:
        avg_score = anomalies['anomaly_score'].mean() if 'anomaly_score' in anomalies.columns else 0
        max_score = anomalies['anomaly_score'].max() if 'anomaly_score' in anomalies.columns else 0
        summary_text += f"""
        <b>Score médio das anomalias:</b> {avg_score:.4f}<br/>
        <b>Score máximo:</b> {max_score:.4f}<br/>
        """
    
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Gráficos
    if include_charts and total_anomalies > 0:
        story.append(PageBreak())
        story.append(Paragraph("Gráficos de Anomalias", heading_style))
        
        # Criar gráficos
        temp_charts_dir = Path("outputs/temp_charts")
        chart_paths = create_anomaly_charts(df_with_anomalies, anomalies, temp_charts_dir)
        
        # Adicionar gráficos ao PDF
        for chart_path in chart_paths:
            if chart_path.exists():
                img = Image(str(chart_path), width=7*inch, height=4.2*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
        
        # Limpar gráficos temporários (opcional)
        # for chart_path in chart_paths:
        #     if chart_path.exists():
        #         chart_path.unlink()
    
    # Tabela de anomalias
    story.append(PageBreak())
    story.append(Paragraph("Detalhes das Anomalias", heading_style))
    
    table_data = create_anomaly_table_data(anomalies, max_rows=50)
    
    # Criar tabela
    table = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
    
    # Estilo da tabela
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ])
    
    table.setStyle(table_style)
    story.append(table)
    
    # Rodapé
    story.append(Spacer(1, 0.3*inch))
    footer_text = f"""
    <i>Relatório gerado automaticamente pelo Inventory Anomaly Detector<br/>
    {REPORT_CONFIG.get('author', 'Sistema de Detecção de Anomalias')}</i>
    """
    story.append(Paragraph(footer_text, normal_style))
    
    # Construir PDF
    doc.build(story)
    
    print(f"Relatório PDF gerado com sucesso: {output_path}")
    print(f"  - Total de páginas: {len(story) // 3 + 1} (aproximado)")
    print(f"  - Anomalias incluídas: {min(len(anomalies), 50)}")
    
    return output_path


def generate_report_from_file(
    anomalies_file: Path,
    output_path: Optional[Path] = None
) -> Path:
    """
    Gera relatório PDF a partir de arquivo CSV com anomalias.
    
    Args:
        anomalies_file: Caminho do arquivo CSV com anomalias.
        output_path: Caminho do arquivo PDF de saída. Se None, usa padrão.
    
    Returns:
        Caminho do arquivo PDF gerado.
    """
    # Carregar dados
    df_all = pd.read_csv(anomalies_file)
    df_all['data'] = pd.to_datetime(df_all['data']) if 'data' in df_all.columns else None
    
    # Separar anomalias
    if 'is_anomaly' in df_all.columns:
        anomalies = df_all[df_all['is_anomaly'] == True].copy()
    else:
        anomalies = df_all.copy()
    
    # Gerar relatório
    return generate_anomaly_report_pdf(df_all, anomalies, output_path)

