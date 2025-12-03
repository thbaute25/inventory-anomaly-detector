"""
Script principal para executar o pipeline Prefect completo.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar pipeline diretamente do arquivo
import importlib.util
spec = importlib.util.spec_from_file_location("pipeline_module", "src/pipeline.py")
pipeline_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline_module)

inventory_anomaly_detection_flow = pipeline_module.inventory_anomaly_detection_flow

if __name__ == "__main__":
    print("=" * 60)
    print("PIPELINE PREFECT - Inventory Anomaly Detector")
    print("=" * 60)
    print()
    print("Este pipeline executa todas as etapas:")
    print("  1. Carregar dados de estoque e consumo")
    print("  2. Limpar e preparar dados")
    print("  3. Criar features de série temporal")
    print("  4. Agregar dados diários por item")
    print("  5. Treinar modelos Prophet")
    print("  6. Detectar anomalias com Isolation Forest")
    print("  7. Enviar alertas (opcional)")
    print("  8. Gerar relatório PDF")
    print()
    print("-" * 60)
    print()
    
    # Executar pipeline
    print("Iniciando execução do pipeline...")
    print()
    
    results = inventory_anomaly_detection_flow(
        data_file=None,  # Usar arquivo padrão (data/inventory_data.csv)
        send_alerts=False,  # Mudar para True para enviar alertas
        send_email=False,  # Mudar para True para enviar email
        generate_pdf_report=True  # Gerar relatório PDF
    )
    
    print()
    print("=" * 60)
    print("PIPELINE EXECUTADO COM SUCESSO!")
    print("=" * 60)
    print()
    print("RESULTADOS:")
    print("-" * 60)
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  - {k}: {v}")
        else:
            print(f"{key}: {value}")
    print()
    print("=" * 60)
    print("Arquivos gerados:")
    print(f"  - Anomalias: {results.get('anomalies_file', 'N/A')}")
    if results.get('anomalies_only_file'):
        print(f"  - Apenas anomalias: {results['anomalies_only_file']}")
    if results.get('pdf_report_path'):
        print(f"  - Relatório PDF: {results['pdf_report_path']}")
    print("=" * 60)

