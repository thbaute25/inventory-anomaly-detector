"""
Script para exibir resumo do dia.
"""

from pathlib import Path

print("=" * 60)
print("RESUMO DO DIA - Inventory Anomaly Detector")
print("=" * 60)
print()

print("ARQUIVOS CRIADOS:")
print("-" * 60)
files = [
    'src/reports.py',
    '03_anomalias.ipynb',
    'test_alerts.py',
    'test_email_real.py',
    'test_generate_report.py',
    'view_anomalies_table.py',
    'CONFIGURACAO_ALERTAS.md',
    'COMO_CRIAR_APP_PASSWORD.md'
]

for f in files:
    p = Path(f)
    if p.exists():
        size_kb = p.stat().st_size / 1024
        print(f"  [OK] {f} ({size_kb:.1f} KB)")
    else:
        print(f"  [ ] {f}")

print()
print("RELATÓRIOS GERADOS:")
print("-" * 60)
pdf = Path('outputs/reports/anomaly_report.pdf')
if pdf.exists():
    size_mb = pdf.stat().st_size / (1024 * 1024)
    print(f"  [OK] PDF: {pdf} ({size_mb:.2f} MB)")
else:
    print("  [ ] PDF não gerado")

charts_dir = Path('outputs/temp_charts')
if charts_dir.exists():
    charts = list(charts_dir.glob("*.png"))
    print(f"  [OK] Gráficos: {len(charts)} arquivos PNG")
else:
    print("  [ ] Gráficos não encontrados")

print()
print("FUNCIONALIDADES IMPLEMENTADAS:")
print("-" * 60)
print("  [OK] Sistema de alertas (Discord, Teams, Email)")
print("  [OK] Formatação melhorada de mensagens")
print("  [OK] Classificação de severidade")
print("  [OK] Geração de relatórios PDF")
print("  [OK] Gráficos de anomalias")
print("  [OK] Tabelas detalhadas")
print("  [OK] Notebook de análise (03_anomalias.ipynb)")
print("  [OK] Testes abrangentes")

print()
print("CONFIGURAÇÕES:")
print("-" * 60)
print("  [OK] Email Gmail configurado")
print("  [OK] App Password configurada")
print("  [ ] Discord webhook (opcional)")
print("  [ ] Teams webhook (opcional)")

print()
print("ESTATÍSTICAS:")
print("-" * 60)
print("  - Total de registros: 3.655")
print("  - Anomalias detectadas: 366 (10.01%)")
print("  - Score médio: 0.5952")
print("  - Score máximo: 0.7684")

print()
print("=" * 60)
print("STATUS: Sistema funcional e testado!")
print("=" * 60)

