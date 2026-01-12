import requests
import base64

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

def gerar_pagina_qr_estatica():
    """Gera uma página HTML estática com o QR Code"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        # Primeiro verifica se a sessão existe, se não, cria
        status_response = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
            headers=headers,
            timeout=10
        )

        if status_response.status_code == 404:
            print("📝 Criando nova sessão...")
            create_data = {"name": SESSION_NAME}
            requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=10)

        # Buscar QR Code
        response = requests.get(
            f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')

            qr_base64 = None
            if 'image' in content_type:
                qr_base64 = f"data:image/png;base64,{base64.b64encode(response.content).decode('utf-8')}"
            else:
                data = response.json()
                if 'value' in data:
                    qr_base64 = data['value']

            if qr_base64:
                # Criar página HTML estática
                html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp QR Code - WAHA</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #25d366, #128c7e);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 500px;
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #25d366;
            margin-bottom: 20px;
            font-size: 28px;
        }}
        .qr-container {{
            margin: 30px 0;
            padding: 20px;
            border: 3px solid #25d366;
            border-radius: 15px;
            background-color: #f8f9fa;
        }}
        .qr-code {{
            max-width: 280px;
            height: auto;
            margin: 0 auto;
            display: block;
            border-radius: 10px;
        }}
        .instructions {{
            text-align: left;
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        .step {{
            margin: 10px 0;
            padding: 5px 0;
        }}
        .refresh-btn {{
            background: linear-gradient(45deg, #25d366, #128c7e);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            margin-top: 20px;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        .refresh-btn:hover {{
            transform: scale(1.05);
        }}
        .status {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
            background-color: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Conectar WhatsApp Business</h1>

        <div class="qr-container">
            <h3>Escaneie o QR Code:</h3>
            <img src="{qr_base64}" alt="QR Code WhatsApp" class="qr-code">
        </div>

        <div class="instructions">
            <h4>Como conectar:</h4>
            <div class="step">1. Abra o <strong>WhatsApp Business</strong> no seu celular</div>
            <div class="step">2. Toque em <strong>(tres pontos)</strong> no canto superior direito</div>
            <div class="step">3. Selecione <strong>"Dispositivos conectados"</strong></div>
            <div class="step">4. Toque em <strong>"Conectar um dispositivo"</strong></div>
            <div class="step">5. <strong>Aponte a camera</strong> para o QR Code acima</div>
        </div>

        <div class="status">
            Aguardando conexao... Escaneie o QR Code com seu WhatsApp Business
        </div>

        <button onclick="location.reload()" class="refresh-btn">
            Atualizar QR Code
        </button>

        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <p><strong>API:</strong> WAHA (WhatsApp HTTP API)</p>
            <p><strong>Status:</strong> Pronto para conexao</p>
            <p><strong>Sessao:</strong> {SESSION_NAME}</p>
        </div>
    </div>
</body>
</html>
                '''

                # Salvar arquivo
                with open('qr_whatsapp_estatico.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)

                print("Pagina HTML gerada com sucesso!")
                print("Arquivo: qr_whatsapp_estatico.html")
                print("Abra este arquivo no navegador")

                return True
            else:
                print("QR Code nao encontrado na resposta")
                return False
        else:
            print(f"Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False

    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    print("GERADOR DE PAGINA QR CODE ESTATICA - WAHA")
    print("=" * 50)
    gerar_pagina_qr_estatica()
