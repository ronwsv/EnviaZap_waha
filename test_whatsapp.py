import requests
import json

class WhatsAppSender:
    def __init__(self, base_url="http://localhost:8080", api_key=""):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    def create_instance(self, instance_name):
        """Cria uma nova instância do WhatsApp"""
        payload = {
            "instanceName": instance_name,
            "token": instance_name,  # usando o nome da instância como token
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            result = response.json()
            print(f"✅ Instância criada: {result}")
            return result
        except Exception as e:
            print(f"❌ Erro ao criar instância: {e}")
            return None
    
    def get_qr_code(self, instance_name):
        """Obtém o QR Code para conectar o WhatsApp"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/connect/{instance_name}",
                headers=self.headers,
                timeout=10
            )
            result = response.json()
            print(f"📱 QR Code: {result}")
            return result
        except Exception as e:
            print(f"❌ Erro ao obter QR Code: {e}")
            return None
    
    def check_instance_status(self, instance_name):
        """Verifica o status da instância"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/connectionState/{instance_name}",
                headers=self.headers,
                timeout=10
            )
            result = response.json()
            print(f"📊 Status da instância: {result}")
            return result
        except Exception as e:
            print(f"❌ Erro ao verificar status: {e}")
            return None
    
    def send_message(self, instance_name, phone_number, message):
        """Envia uma mensagem de texto para um número"""
        # Remove caracteres especiais do número
        clean_number = phone_number.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        payload = {
            "number": clean_number,
            "text": message
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/message/sendText/{instance_name}",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            result = response.json()
            
            if response.status_code in [200, 201]:
                print(f"✅ Mensagem enviada com sucesso!")
                print(f"📱 Para: {phone_number}")
                print(f"💬 Mensagem: {message}")
                print(f"📋 Resposta: {result}")
                return True
            else:
                print(f"❌ Erro ao enviar mensagem: {result}")
                return False
                
        except Exception as e:
            print(f"⚠️ Falha na requisição: {e}")
            return False

def main():
    print("🚀 Testando Evolution API para WhatsApp")
    print("=" * 50)
    
    # Inicializa o cliente com a API Key
    whatsapp = WhatsAppSender(api_key="429683C4C977415CAAFCCE10F7D57E11")
    
    # Nome da instância (você pode mudar)
    instance_name = "teste_instancia"
    
    print(f"\n1. Criando instância: {instance_name}")
    whatsapp.create_instance(instance_name)
    
    print(f"\n2. Obtendo QR Code para conectar...")
    qr_result = whatsapp.get_qr_code(instance_name)
    
    if qr_result and 'base64' in qr_result:
        print("📱 QR Code gerado! Use o WhatsApp do seu celular para escanear.")
        print("👆 Vá em: WhatsApp > Dispositivos Vinculados > Vincular um Dispositivo")
        print("\n⏳ Aguarde conectar e pressione Enter para continuar...")
        input()
    
    print(f"\n3. Verificando status da conexão...")
    status = whatsapp.check_instance_status(instance_name)
    
    if status and status.get('state') == 'open':
        print("🎉 WhatsApp conectado com sucesso!")
        
        # Exemplo de envio de mensagem
        print(f"\n4. Testando envio de mensagem...")
        print("💡 Para testar, digite o número e mensagem:")
        
        phone = input("📱 Número (formato: 5511999999999): ")
        message = input("💬 Mensagem: ")
        
        if phone and message:
            whatsapp.send_message(instance_name, phone, message)
        else:
            print("❌ Número ou mensagem não informados. Usando exemplo...")
            whatsapp.send_message(
                instance_name, 
                "5511999999999",  # substitua pelo seu número
                "🚀 Teste da Evolution API funcionando!"
            )
    else:
        print("❌ WhatsApp não está conectado. Verifique o QR Code.")

if __name__ == "__main__":
    main()
