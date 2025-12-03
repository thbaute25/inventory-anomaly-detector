"""
Script para verificar o PDF gerado e listar seus conteúdos.
"""

from pathlib import Path

print("=" * 60)
print("VERIFICAÇÃO DO PDF GERADO")
print("=" * 60)
print()

# Verificar PDF
pdf_path = Path("outputs/reports/anomaly_report.pdf")
if pdf_path.exists():
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"[OK] PDF encontrado: {pdf_path}")
    print(f"     Tamanho: {size_mb:.2f} MB")
else:
    print(f"[ERRO] PDF não encontrado: {pdf_path}")
    exit(1)

print()

# Verificar gráficos temporários
charts_dir = Path("outputs/temp_charts")
if charts_dir.exists():
    chart_files = list(charts_dir.glob("*.png"))
    print(f"[OK] Gráficos temporários encontrados: {len(chart_files)}")
    for chart in chart_files:
        size_kb = chart.stat().st_size / 1024
        print(f"     - {chart.name} ({size_kb:.1f} KB)")
else:
    print("[INFO] Diretório de gráficos temporários não encontrado")

print()
print("=" * 60)
print("CONTEÚDO DO PDF:")
print("=" * 60)
print("1. Página de Título e Resumo Executivo")
print("   - Título do relatório")
print("   - Data de geração")
print("   - Estatísticas gerais (total de registros, anomalias, scores)")
print()
print("2. Gráficos de Anomalias")
print("   - Distribuição de scores de anomalia")
print("   - Consumo vs Estoque (scatter plot)")
print("   - Top 10 produtos com mais anomalias")
print("   - Top 10 datas com mais anomalias")
print()
print("3. Tabela Detalhada")
print("   - Top 50 anomalias ordenadas por score")
print("   - Colunas: Data, Produto, Consumo, Estoque, Score")
print()
print("=" * 60)
print(f"Para visualizar o PDF, abra: {pdf_path.absolute()}")
print("=" * 60)

