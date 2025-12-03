"""
Script de teste para executar o pipeline Prefect.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar diretamente do arquivo (não do diretório)
import importlib.util
spec = importlib.util.spec_from_file_location("pipeline_module", "src/pipeline.py")
pipeline_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline_module)

inventory_anomaly_detection_flow = pipeline_module.inventory_anomaly_detection_flow

print("=" * 60)
print("TESTE DO PIPELINE PREFECT")
print("=" * 60)
print()

# Executar pipeline
print("Executando pipeline Prefect...")
print("-" * 60)

results = inventory_anomaly_detection_flow(
    data_file=None,  # Usar arquivo padrão
    send_alerts=False,  # Não enviar alertas no teste
    send_email=False,  # Não enviar email no teste
    generate_pdf_report=True  # Gerar PDF
)

print()
print("=" * 60)
print("RESULTADOS DO PIPELINE")
print("=" * 60)
for key, value in results.items():
    print(f"{key}: {value}")
print("=" * 60)

