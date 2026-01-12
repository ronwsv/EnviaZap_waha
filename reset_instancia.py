import requests
import json

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

def deletar_sessao(nome):
    """Deleta uma sessão existente"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        response = requests.post(
            f"{WAHA_URL}/api/sessions/{nome}/stop",
            headers=headers
        )

        print(f"Parando sessao '{nome}': {response.status_code}")
        if response.status_code in [200, 201]:
            print("Sessao parada com sucesso!")
            return True
        else:
            print(f"Resposta: {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao parar: {e}")
        return False

def criar_nova_sessao(nome):
    """Cria uma nova sessão"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        data = {
            "name": nome
        }

        response = requests.post(
            f"{WAHA_URL}/api/sessions/start",
            headers=headers,
            json=data
        )

        print(f"Criando nova sessao '{nome}': {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            print("Nova sessao criada com sucesso!")
            print(f"Detalhes:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Erro: {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao criar: {e}")
        return False

def main():
    print("RESET DA SESSAO WHATSAPP - WAHA")
    print("=" * 50)

    print("\n1. Parando sessao atual...")
    deletar_sessao(SESSION_NAME)

    print("\n2. Criando nova sessao...")
    if criar_nova_sessao(SESSION_NAME):
        print("\nRESET CONCLUIDO!")
        print("Agora voce pode escanear um novo QR Code")
        print("Acesse: http://localhost:5000")
    else:
        print("Falha ao criar nova sessao")

if __name__ == "__main__":
    main()
