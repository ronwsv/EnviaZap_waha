import requests
import time

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

headers = {
    "X-Api-Key": WAHA_API_KEY,
    "Content-Type": "application/json"
}

def tentar_codigo_pareamento():
    print("METODO DE CODIGO DE PAREAMENTO - WAHA")
    print("=" * 60)
    print("Este metodo e mais confiavel que QR code quando ha bloqueios")
    print("=" * 60)

    try:
        # Verificar status atual
        status_response = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
            headers=headers,
            timeout=10
        )

        if status_response.status_code == 200:
            data = status_response.json()
            if data.get('status') == 'WORKING':
                print("\nWhatsApp ja esta conectado!")
                me = data.get('me', {})
                print(f"Perfil: {me.get('pushName', 'N/A')}")
                return True

        # Solicitar número do telefone
        print("\nDigite o numero do telefone para gerar o codigo de pareamento")
        print("Formato: DDI + DDD + Numero (ex: 5511999999999)")
        phone_number = input("Numero: ").strip()

        if not phone_number:
            print("Numero nao informado")
            return False

        # Limpar número
        phone_number = ''.join(filter(str.isdigit, phone_number))

        print(f"\nSolicitando codigo de pareamento para: {phone_number}")

        # Criar sessão com código de pareamento
        create_data = {
            "name": SESSION_NAME,
            "config": {
                "proxy": None,
                "webhooks": []
            }
        }

        # Primeiro criar/iniciar a sessão
        create_response = requests.post(
            f"{WAHA_URL}/api/sessions/start",
            headers=headers,
            json=create_data,
            timeout=30
        )

        print(f"Status criacao sessao: {create_response.status_code}")

        # Solicitar código de pareamento
        # Nota: O WAHA pode ter endpoint diferente para pairing code
        pairing_response = requests.post(
            f"{WAHA_URL}/api/{SESSION_NAME}/auth/request-code",
            headers=headers,
            json={"phoneNumber": phone_number},
            timeout=30
        )

        if pairing_response.status_code in [200, 201]:
            data = pairing_response.json()
            code = data.get('code', data.get('pairingCode', 'N/A'))
            print("\n" + "=" * 60)
            print(f"CODIGO DE PAREAMENTO: {code}")
            print("=" * 60)
            print("\nDigite este codigo no seu WhatsApp:")
            print("1. Abra o WhatsApp no celular")
            print("2. Va em Configuracoes > Dispositivos conectados")
            print("3. Toque em 'Conectar um dispositivo'")
            print("4. Escolha 'Conectar com numero de telefone'")
            print("5. Digite o codigo acima")
            print("=" * 60)
            return True
        else:
            print(f"Erro ao solicitar codigo: {pairing_response.status_code}")
            print(f"Resposta: {pairing_response.text}")

            # Tentar método alternativo - QR Code
            print("\nTentando metodo alternativo (QR Code)...")
            print("Acesse http://localhost:5000/connect para escanear o QR Code")
            return False

    except Exception as e:
        print(f"Erro: {e}")
        return False

def aguardar_conexao():
    """Aguarda a conexão ser estabelecida"""
    print("\nAguardando conexao...")

    for i in range(60):  # 5 minutos
        try:
            response = requests.get(
                f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')

                if status == 'WORKING':
                    print("\nCONECTADO COM SUCESSO!")
                    me = data.get('me', {})
                    print(f"Perfil: {me.get('pushName', 'N/A')}")
                    return True

            print(f"  Tentativa {i+1}/60 - Status: {status if 'status' in dir() else 'aguardando'}")

        except Exception as e:
            print(f"  Tentativa {i+1}/60 - Erro: {e}")

        time.sleep(5)

    print("\nTempo limite atingido. Tente novamente.")
    return False

def main():
    print("CONEXAO WHATSAPP - CODIGO DE PAREAMENTO")
    print("=" * 60)

    if tentar_codigo_pareamento():
        print("\nAguardando voce digitar o codigo no WhatsApp...")
        aguardar_conexao()
    else:
        print("\nFalha ao gerar codigo de pareamento")
        print("Tente usar o QR Code: python qr_server.py")

if __name__ == "__main__":
    main()
