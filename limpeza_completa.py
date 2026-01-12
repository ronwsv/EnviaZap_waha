import requests
import time
import json

# Configurações da Evolution API
EVOLUTION_URL = "http://localhost:8080"
API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
INSTANCE_NAME = "minhaloja"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def verificar_sessoes_ativas():
    print("🔍 VERIFICANDO SESSÕES ATIVAS E LIMPEZA COMPLETA")
    print("=" * 60)
    
    try:
        # 1. Verificar todas as instâncias existentes
        print("1️⃣ Listando todas as instâncias...")
        response = requests.get(f"{EVOLUTION_URL}/instance/fetchInstances", headers=headers)
        if response.status_code == 200:
            instances = response.json()
            print(f"   Encontradas {len(instances)} instâncias:")
            for inst in instances:
                print(f"   - {inst['name']}: {inst.get('connectionStatus', 'N/A')}")
        
        # 2. Forçar logout de todas as instâncias
        print("\n2️⃣ Forçando logout de todas as instâncias...")
        for inst_name in ["minhaloja", "teste_instancia"]:
            try:
                response = requests.delete(f"{EVOLUTION_URL}/instance/logout/{inst_name}", headers=headers)
                print(f"   Logout {inst_name}: {response.status_code}")
            except Exception as e:
                print(f"   Erro logout {inst_name}: {e}")
        
        time.sleep(3)
        
        # 3. Deletar todas as instâncias
        print("\n3️⃣ Deletando todas as instâncias...")
        for inst_name in ["minhaloja", "teste_instancia"]:
            try:
                response = requests.delete(f"{EVOLUTION_URL}/instance/delete/{inst_name}", headers=headers)
                print(f"   Delete {inst_name}: {response.status_code}")
            except Exception as e:
                print(f"   Erro delete {inst_name}: {e}")
        
        time.sleep(5)
        
        # 4. Verificar se ainda há instâncias
        print("\n4️⃣ Verificando limpeza...")
        response = requests.get(f"{EVOLUTION_URL}/instance/fetchInstances", headers=headers)
        if response.status_code == 200:
            instances = response.json()
            print(f"   Instâncias restantes: {len(instances)}")
            if len(instances) == 0:
                print("   ✅ Todas as instâncias foram removidas!")
            else:
                for inst in instances:
                    print(f"   - {inst['name']}: {inst.get('connectionStatus', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🚨 AGUARDANDO 30 SEGUNDOS PARA ESTABILIZAÇÃO...")
        print("   (Tempo necessário para WhatsApp esquecer as tentativas)")
        print("=" * 60)
        
        # Countdown visual
        for i in range(30, 0, -1):
            print(f"\r⏳ Aguardando: {i:2d} segundos restantes", end="", flush=True)
            time.sleep(1)
        
        print("\n\n5️⃣ Criando nova instância limpa...")
        
        # Criar instância com configuração mais específica
        instance_data = {
            "instanceName": INSTANCE_NAME,
            "token": API_KEY,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
            "webhookUrl": "",
            "webhookByEvents": False,
            "webhookBase64": False,
            "events": [],
            "disableWebhook": True,  # Desabilitar webhooks para evitar conflitos
            "chatwoot_account_id": None,
            "chatwoot_token": None,
            "chatwoot_url": None,
            "chatwoot_sign_msg": False
        }
        
        response = requests.post(
            f"{EVOLUTION_URL}/instance/create",
            headers=headers,
            json=instance_data
        )
        print(f"   Status criação: {response.status_code}")
        
        if response.status_code == 201:
            print("   ✅ Instância criada com sucesso!")
            
            time.sleep(5)
            
            # 6. Conectar
            print("\n6️⃣ Conectando à nova instância...")
            response = requests.get(f"{EVOLUTION_URL}/instance/connect/{INSTANCE_NAME}", headers=headers)
            print(f"   Status conexão: {response.status_code}")
            
            time.sleep(8)  # Aguardar mais tempo para estabilizar
            
            # 7. Obter QR code
            print("\n7️⃣ Obtendo novo QR code...")
            response = requests.get(f"{EVOLUTION_URL}/instance/fetchInstances/{INSTANCE_NAME}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                qr_data = data.get('qrcode', {})
                
                if qr_data and qr_data.get('code'):
                    print(f"   ✅ QR Code obtido! Contador: {qr_data.get('count', 'N/A')}")
                    
                    # Criar página especial com instruções detalhadas
                    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Business - Conexão Limpa</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #25D366, #128C7E, #075E54);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 600px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .title {{
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        .qr-container {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            display: inline-block;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        .qr-code {{
            max-width: 280px;
            width: 100%;
            height: auto;
        }}
        .status-box {{
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #25D366;
        }}
        .warning-box {{
            background: rgba(255, 69, 0, 0.3);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #FF4500;
        }}
        .instructions {{
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 12px;
            margin: 25px 0;
            text-align: left;
        }}
        .step {{
            margin: 12px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .step:last-child {{
            border-bottom: none;
        }}
        .step-number {{
            background: #25D366;
            color: white;
            padding: 4px 8px;
            border-radius: 50%;
            margin-right: 10px;
            font-weight: bold;
        }}
        .highlight {{
            background: rgba(255, 255, 0, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            font-style: italic;
            opacity: 0.8;
        }}
        .blink {{
            animation: blink 2s infinite;
        }}
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0.5; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">🔄 Conexão Limpa</div>
        
        <div class="warning-box">
            <strong>⚠️ SESSÃO COMPLETAMENTE RESETADA</strong><br>
            Todas as instâncias anteriores foram removidas!
        </div>
        
        <div class="status-box">
            <strong>📊 Status:</strong> Nova instância criada<br>
            <strong>📱 Nome:</strong> {INSTANCE_NAME}<br>
            <strong>🔢 Contador QR:</strong> {qr_data.get('count', 'N/A')}<br>
            <strong>⏰ Gerado em:</strong> {time.strftime('%H:%M:%S')}
        </div>
        
        <div class="qr-container">
            <img src="{qr_data.get('base64')}" alt="QR Code WhatsApp" class="qr-code">
        </div>
        
        <div class="instructions">
            <h3>📱 PROTOCOLO DE CONEXÃO LIMPA:</h3>
            
            <div class="step">
                <span class="step-number">1</span>
                <span class="highlight">FECHE COMPLETAMENTE</span> o WhatsApp Business
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                Vá em <strong>Configurações do Android → Apps → WhatsApp Business</strong>
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                Toque em <span class="highlight">"Forçar parada"</span> e depois <span class="highlight">"Armazenamento"</span>
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                Toque em <span class="highlight">"Limpar Cache"</span> (NÃO limpar dados!)
            </div>
            
            <div class="step">
                <span class="step-number">5</span>
                <span class="highlight">AGUARDE 2 MINUTOS</span> (tempo crítico)
            </div>
            
            <div class="step">
                <span class="step-number">6</span>
                Abra o WhatsApp Business novamente
            </div>
            
            <div class="step">
                <span class="step-number">7</span>
                Vá em <strong>⚙️ Configurações → Dispositivos conectados</strong>
            </div>
            
            <div class="step">
                <span class="step-number">8</span>
                <span class="highlight">DESCONECTE TODOS</span> os dispositivos se houver
            </div>
            
            <div class="step">
                <span class="step-number">9</span>
                Toque em <span class="highlight">"Conectar um dispositivo"</span>
            </div>
            
            <div class="step">
                <span class="step-number">10</span>
                <span class="highlight blink">ESCANEIE ESTE QR CODE</span>
            </div>
        </div>
        
        <div class="warning-box">
            🚨 <strong>IMPORTANTE:</strong><br>
            • Se der erro "tente mais tarde", aguarde 10 minutos<br>
            • Este QR code expira em alguns minutos<br>
            • Não tente múltiplas vezes seguidas
        </div>
        
        <div class="footer">
            Sistema Evolution API - Conexão estabelecida com sucesso = Status "open"
        </div>
    </div>
    
    <script>
        // Auto-refresh a cada 45 segundos para pegar QR atualizado
        setTimeout(() => {{
            location.reload();
        }}, 45000);
        
        // Mostrar tempo restante
        let timeLeft = 45;
        setInterval(() => {{
            timeLeft--;
            if (timeLeft > 0) {{
                document.title = `WhatsApp (${timeLeft}s) - Conexão Limpa`;
            }}
        }}, 1000);
    </script>
</body>
</html>"""
                    
                    with open("qr_conexao_limpa.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    
                    print("\n✅ PROCESSO COMPLETO!")
                    print("📄 Arquivo criado: qr_conexao_limpa.html")
                    print("\n🎯 PRÓXIMOS PASSOS:")
                    print("1. Abra o arquivo qr_conexao_limpa.html")
                    print("2. SIGA O PROTOCOLO EXATO da página")
                    print("3. Limpe o cache do WhatsApp Business")
                    print("4. Aguarde 2 minutos antes de tentar")
                    
                    return True
                else:
                    print("   ❌ Erro: QR code não encontrado")
                    return False
            else:
                print(f"   ❌ Erro ao obter QR: {response.status_code}")
                return False
        else:
            print(f"   ❌ Erro ao criar instância: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante limpeza completa: {e}")
        return False

if __name__ == "__main__":
    verificar_sessoes_ativas()
