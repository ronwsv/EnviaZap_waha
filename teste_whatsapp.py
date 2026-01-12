import requests

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

def verificar_status_conexao():
    """Verifica se o WhatsApp está conectado"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        response = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            print(f"Status da sessao: {status}")

            if status == 'WORKING':
                me = data.get('me', {})
                print(f"WhatsApp CONECTADO!")
                print(f"Perfil: {me.get('pushName', 'N/A')}")
                numero = me.get('id', '').split('@')[0] if me.get('id') else 'N/A'
                print(f"Numero: {numero}")
                return True
            else:
                print(f"WhatsApp nao conectado. Status: {status}")
                return False
        elif response.status_code == 404:
            print("Sessao nao encontrada")
            return False
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao verificar status: {e}")
        return False

def enviar_mensagem_teste(numero, mensagem):
    """Envia uma mensagem de teste"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        # Formatar número
        clean_number = ''.join(filter(str.isdigit, numero))
        if len(clean_number) == 11:
            clean_number = f"55{clean_number}"
        elif len(clean_number) == 10:
            clean_number = f"559{clean_number}"

        data = {
            "chatId": f"{clean_number}@c.us",
            "text": mensagem,
            "session": SESSION_NAME
        }

        print(f"\nEnviando mensagem para: {clean_number}")
        print(f"Mensagem: {mensagem}")

        response = requests.post(
            f"{WAHA_URL}/api/sendText",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code in [200, 201]:
            print("SUCESSO! Mensagem enviada!")
            return True
        else:
            print(f"ERRO: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False

def listar_chats():
    """Lista os chats disponíveis"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        response = requests.get(
            f"{WAHA_URL}/api/{SESSION_NAME}/chats",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print("\nChats disponiveis:")
            for chat in data[:10]:  # Mostrar apenas os 10 primeiros
                chat_id = chat.get('id', {})
                name = chat.get('name', 'Sem nome')
                print(f"  - {name}: {chat_id}")
            return data
        else:
            print(f"Erro ao listar chats: {response.status_code}")
            return None

    except Exception as e:
        print(f"Erro ao listar chats: {e}")
        return None

def main():
    print("TESTE DE CONEXAO WHATSAPP - WAHA")
    print("=" * 50)

    # Verificar conexão
    if not verificar_status_conexao():
        print("\nWhatsApp nao esta conectado!")
        print("Execute o servidor de QR Code primeiro:")
        print("   python qr_server.py")
        print("E escaneie o QR Code com seu WhatsApp")
        return

    print("\n" + "=" * 50)

    # Listar chats
    print("\nListando chats...")
    listar_chats()

    print("\n" + "=" * 50)

    # Enviar mensagem de teste
    numero_teste = input("\nDigite o numero para teste (com DDD, ex: 11999999999): ").strip()
    if numero_teste:
        mensagem = "Mensagem de teste do sistema WAHA!"
        enviar_mensagem_teste(numero_teste, mensagem)
    else:
        print("Nenhum numero informado, pulando teste de envio")

if __name__ == "__main__":
    main()
