"""
Script para iniciar a aplicação Streamlit.
Execute: py start_app.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("Iniciando Inventory Anomaly Detector - Interface Web")
    print("=" * 60)
    print()
    
    # Verificar se os arquivos necessários existem
    if not Path("app.py").exists():
        print("ERRO: app.py não encontrado!")
        return
    
    if not Path("outputs/anomalies_detected.csv").exists():
        print("AVISO: Arquivos de saída não encontrados.")
        print("Execute o pipeline primeiro: py run_pipeline.py")
        print()
    
    print("Iniciando servidor Streamlit...")
    print("Aguarde alguns segundos...")
    print()
    print("=" * 60)
    print("Acesse no navegador:")
    print("  http://localhost:8501")
    print("  ou")
    print("  http://127.0.0.1:8501")
    print("=" * 60)
    print()
    print("Para parar o servidor, pressione Ctrl+C")
    print()
    
    # Iniciar Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo usuário.")
    except Exception as e:
        print(f"\nERRO ao iniciar servidor: {e}")
        print("\nTente executar manualmente:")
        print("  py -m streamlit run app.py")

if __name__ == "__main__":
    main()
