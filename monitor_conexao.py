import requests
import time

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

def verificar_status_continuamente():
    """Verifica o status da conexão continuamente"""
    print("Monitorando conexao WhatsApp...")
    print("Escaneie o QR Code na pagina: http://localhost:5000")
    print("=" * 60)

    tentativas = 0
    max_tentativas = 60  # 5 minutos (60 x 5 segundos)

    while tentativas < max_tentativas:
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Api-Key": WAHA_API_KEY
            }

            response = requests.get(
                f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')

                print(f"{time.strftime('%H:%M:%S')} - Status: {status}", end="")

                if status == 'WORKING':
                    print(" CONECTADO!")
                    print("\nWhatsApp conectado com sucesso!")
                    print("Agora voce pode enviar mensagens!")

                    # Obter informações do perfil conectado
                    me = data.get('me', {})
                    if me:
                        print(f"Perfil: {me.get('pushName', 'N/A')}")
                        print(f"Numero: {me.get('id', 'N/A').split('@')[0] if me.get('id') else 'N/A'}")

                    return True

                elif status == 'SCAN_QR_CODE':
                    print(" Aguardando QR Code...")
                elif status == 'STARTING':
                    print(" Iniciando...")
                else:
                    print(f" Status: {status}")

            elif response.status_code == 404:
                print(f"{time.strftime('%H:%M:%S')} - Sessao nao encontrada, criando...")
                create_data = {"name": SESSION_NAME}
                requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=5)
            else:
                print(f"Erro na API: {response.status_code}")

        except Exception as e:
            print(f"Erro: {e}")

        tentativas += 1
        time.sleep(5)  # Espera 5 segundos

    print("\nTempo limite atingido (5 minutos)")
    print("Tente escanear o QR Code novamente")
    return False

def main():
    print("MONITOR DE CONEXAO WHATSAPP - WAHA")
    print("=" * 60)

    if verificar_status_continuamente():
        print("\nCONEXAO ESTABELECIDA!")
        print("Execute o teste de mensagem:")
        print("   python teste_whatsapp.py")
    else:
        print("\nFalha na conexao")
        print("Tente novamente")

if __name__ == "__main__":
    main()
