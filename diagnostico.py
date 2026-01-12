import requests
import json

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

def verificar_todas_sessoes():
    """Verifica todas as sessões disponíveis"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        response = requests.get(
            f"{WAHA_URL}/api/sessions",
            headers=headers
        )

        print(f"Status da requisicao: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("Todas as sessoes:")
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"Erro: {response.text}")
            return None

    except Exception as e:
        print(f"Erro de conexao: {e}")
        return None

def verificar_status_detalhado():
    """Verifica status detalhado da sessão"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        # Status da sessão
        response1 = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
            headers=headers
        )

        print(f"Status da sessao ({response1.status_code}):")
        if response1.status_code == 200:
            data = response1.json()
            print(json.dumps(data, indent=2))

            status = data.get('status', 'unknown')
            if status == 'WORKING':
                print("\nWhatsApp esta CONECTADO!")
            elif status == 'SCAN_QR_CODE':
                print("\nAguardando escaneamento do QR Code...")
            elif status == 'STARTING':
                print("\nSessao esta iniciando...")
            else:
                print(f"\nStatus atual: {status}")
        elif response1.status_code == 404:
            print("Sessao nao encontrada. Criando nova sessao...")
            create_data = {"name": SESSION_NAME}
            create_response = requests.post(
                f"{WAHA_URL}/api/sessions/start",
                headers=headers,
                json=create_data
            )
            print(f"Criar sessao: {create_response.status_code}")
            print(create_response.text)
        else:
            print(response1.text)

        print("\n" + "-" * 50)

        # Tentar obter QR Code
        response2 = requests.get(
            f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr",
            headers=headers
        )

        print(f"Status do QR Code ({response2.status_code}):")
        if response2.status_code == 200:
            content_type = response2.headers.get('Content-Type', '')
            if 'image' in content_type:
                print("QR Code disponivel como imagem!")
                print("Acesse o servidor web para escanear")
            else:
                print("QR Code disponivel em formato JSON")
        elif response2.status_code == 404:
            print("Sessao ja conectada ou QR Code nao disponivel")
        else:
            print(response2.text)

    except Exception as e:
        print(f"Erro: {e}")

def main():
    print("DIAGNOSTICO DO WAHA")
    print("=" * 50)

    print("\n1. Verificando todas as sessoes...")
    verificar_todas_sessoes()

    print("\n2. Verificando status detalhado...")
    verificar_status_detalhado()

    print("\n" + "=" * 50)
    print("DICAS:")
    print("- Se a sessao nao existe, ela sera criada automaticamente")
    print("- Acesse: http://localhost:5000 para escanear QR Code")
    print("- O status deve mudar para 'WORKING' quando conectado")

if __name__ == "__main__":
    main()
