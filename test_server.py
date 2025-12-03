"""
Script para testar se o servidor Streamlit está funcionando
"""
import requests
import time
import sys

def test_server(url="http://localhost:8501", timeout=5):
    """Testa se o servidor está respondendo"""
    print(f"Testando servidor em: {url}")
    print("Aguarde...")
    
    for i in range(10):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print(f"\n✅ SUCESSO! Servidor está respondendo!")
                print(f"   Status Code: {response.status_code}")
                print(f"   URL: {url}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"   Tentativa {i+1}/10: Servidor não está respondendo ainda...")
            time.sleep(2)
        except Exception as e:
            print(f"   Erro: {e}")
            time.sleep(2)
    
    print(f"\n❌ Servidor não está respondendo após 10 tentativas")
    print(f"\nTente:")
    print(f"  1. Executar: py -m streamlit run app.py")
    print(f"  2. Verificar se há erros no terminal")
    print(f"  3. Tentar porta diferente: py -m streamlit run app.py --server.port 8502")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CONEXÃO - Streamlit Server")
    print("=" * 60)
    print()
    
    # Testar localhost
    if not test_server("http://localhost:8501"):
        print("\nTentando com 127.0.0.1...")
        test_server("http://127.0.0.1:8501")
    
    print("\n" + "=" * 60)

