"""
Script para validar o arquivo prefect.yaml
"""

import yaml
from pathlib import Path

try:
    with open('prefect.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("=" * 60)
    print("VALIDAÇÃO DO prefect.yaml")
    print("=" * 60)
    print()
    
    print(f"Arquivo válido: Sim")
    print(f"Deployments configurados: {len(config.get('deployments', []))}")
    print()
    
    if 'deployments' in config:
        for i, deployment in enumerate(config['deployments'], 1):
            print(f"Deployment {i}:")
            print(f"  Nome: {deployment.get('name', 'N/A')}")
            print(f"  Entrypoint: {deployment.get('entrypoint', 'N/A')}")
            print(f"  Tags: {deployment.get('tags', [])}")
            print()
    
    print("=" * 60)
    print("Validação concluída com sucesso!")
    print("=" * 60)
    
except Exception as e:
    print(f"Erro ao validar prefect.yaml: {e}")
    import traceback
    traceback.print_exc()

