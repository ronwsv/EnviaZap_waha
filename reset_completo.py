import requests
import time

# Configurações da Evolution API
EVOLUTION_URL = "http://localhost:8080"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE_NAME = "minhaloja"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def reset_completo():
    print("🔄 RESET COMPLETO DA INSTÂNCIA")
    print("=" * 50)
    
    # 1. Fechar/Desconectar a instância atual
    print("1️⃣ Desconectando instância...")
    try:
        response = requests.delete(
            f"{EVOLUTION_URL}/instance/logout/{INSTANCE_NAME}",
            headers=headers
        )
        print(f"   Status logout: {response.status_code}")
    except:
        print("   Logout falhou (normal se já desconectada)")
    
    time.sleep(2)
    
    # 2. Deletar a instância
    print("2️⃣ Deletando instância...")
    try:
        response = requests.delete(
            f"{EVOLUTION_URL}/instance/delete/{INSTANCE_NAME}",
            headers=headers
        )
        print(f"   Status delete: {response.status_code}")
    except:
        print("   Delete falhou")
    
    time.sleep(3)
    
    # 3. Criar nova instância
    print("3️⃣ Criando nova instância...")
    instance_data = {
        "instanceName": INSTANCE_NAME,
        "token": API_KEY,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        "webhookUrl": "",
        "webhookByEvents": False,
        "webhookBase64": False,
        "events": []
    }
    
    try:
        response = requests.post(
            f"{EVOLUTION_URL}/instance/create",
            headers=headers,
            json=instance_data
        )
        print(f"   Status create: {response.status_code}")
        time.sleep(3)
        
        # 4. Conectar à instância
        print("4️⃣ Conectando à instância...")
        response = requests.get(
            f"{EVOLUTION_URL}/instance/connect/{INSTANCE_NAME}",
            headers=headers
        )
        print(f"   Status connect: {response.status_code}")
        
        time.sleep(5)
        
        # 5. Gerar novo QR code
        print("5️⃣ Gerando novo QR code...")
        response = requests.get(
            f"{EVOLUTION_URL}/instance/fetchInstances/{INSTANCE_NAME}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            qr_data = data.get('qrcode', {})
            if qr_data and qr_data.get('code'):
                print("✅ QR Code gerado com sucesso!")
                print(f"   Contador: {qr_data.get('count', 'N/A')}")
                
                # Criar página HTML atualizada
                html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp QR Code - Reset Completo</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: white;
        }}
        .container {{
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .qr-code {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            display: inline-block;
        }}
        .status {{
            margin: 15px 0;
            padding: 10px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
        }}
        .instructions {{
            margin-top: 20px;
            text-align: left;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
        }}
        .warning {{
            background: #FF6B6B;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 WhatsApp - QR Code (Reset Completo)</h1>
        
        <div class="warning">
            ⚠️ INSTÂNCIA RESETADA COMPLETAMENTE
        </div>
        
        <div class="status">
            <strong>Instância:</strong> {INSTANCE_NAME}<br>
            <strong>Contador QR:</strong> {qr_data.get('count', 'N/A')}<br>
            <strong>Status:</strong> Aguardando conexão
        </div>
        
        <div class="qr-code">
            <img src="{qr_data.get('base64')}" alt="QR Code WhatsApp" style="max-width: 300px;">
        </div>
        
        <div class="instructions">
            <h3>📱 INSTRUÇÕES PARA CONEXÃO:</h3>
            <ol>
                <li><strong>FECHE COMPLETAMENTE</strong> o WhatsApp Business no celular</li>
                <li><strong>AGUARDE 30 segundos</strong></li>
                <li><strong>ABRA o WhatsApp Business</strong></li>
                <li>Vá em <strong>Configurações → Dispositivos conectados</strong></li>
                <li><strong>DESCONECTE todos os dispositivos</strong> se houver</li>
                <li><strong>VOLTE</strong> e clique em "Conectar um dispositivo"</li>
                <li><strong>ESCANEIE</strong> este QR Code</li>
            </ol>
        </div>
        
        <div class="warning">
            🚨 Se der erro "tente mais tarde", aguarde 5 minutos antes de tentar novamente
        </div>
        
        <p><em>Gerado em: {time.strftime('%H:%M:%S')}</em></p>
        
        <script>
            // Auto-refresh a cada 30 segundos
            setTimeout(() => {{
                location.reload();
            }}, 30000);
        </script>
    </div>
</body>
</html>"""
                
                with open("qr_reset_completo.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                print("\n✅ RESET COMPLETO FINALIZADO!")
                print("📄 Arquivo criado: qr_reset_completo.html")
                print("\n🔍 PRÓXIMOS PASSOS:")
                print("1. Abra o arquivo qr_reset_completo.html")
                print("2. SIGA EXATAMENTE as instruções na página")
                print("3. Aguarde 5 minutos se continuar dando erro")
                
                return True
            else:
                print("❌ Erro ao gerar QR code")
                return False
        else:
            print(f"❌ Erro ao buscar instância: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante reset: {e}")
        return False

if __name__ == "__main__":
    reset_completo()
