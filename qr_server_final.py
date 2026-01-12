import requests
import base64
from flask import Flask, render_template_string

app = Flask(__name__)

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

# Template HTML atualizado
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp QR Code - WAHA</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #25d366;
            margin-bottom: 20px;
        }
        .qr-container {
            margin: 20px 0;
            padding: 20px;
            border: 2px solid #25d366;
            border-radius: 10px;
            background-color: #fafafa;
        }
        .qr-code {
            max-width: 300px;
            height: auto;
            margin: 0 auto;
            display: block;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .status.connecting {
            background-color: #fff3cd;
            color: #856404;
        }
        .status.connected {
            background-color: #d4edda;
            color: #155724;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .instructions {
            margin-top: 20px;
            text-align: left;
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
        }
        .refresh-btn {
            background-color: #25d366;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 16px;
        }
        .refresh-btn:hover {
            background-color: #1eb856;
        }
    </style>
    <script>
        function refreshPage() {
            location.reload();
        }

        // Auto-refresh a cada 10 segundos
        setTimeout(function() {
            location.reload();
        }, 10000);
    </script>
</head>
<body>
    <div class="container">
        <h1>Conectar WhatsApp</h1>

        {% if qr_code %}
        <div class="qr-container">
            <h3>Escaneie o QR Code com seu WhatsApp:</h3>
            <img src="{{ qr_code }}" alt="QR Code" class="qr-code">
        </div>

        <div class="instructions">
            <h4>Como conectar:</h4>
            <ol>
                <li>Abra o <strong>WhatsApp</strong> no seu celular</li>
                <li>Toque em <strong>(tres pontos)</strong> -> <strong>Dispositivos conectados</strong></li>
                <li>Toque em <strong>Conectar um dispositivo</strong></li>
                <li>Aponte a camera para o QR Code acima</li>
            </ol>
        </div>

        <div class="status connecting">
            Aguardando conexao...
        </div>

        {% elif status == 'connected' %}
        <div class="status connected">
            WhatsApp conectado com sucesso!
        </div>
        <p>Voce ja pode fechar esta pagina e usar a API para enviar mensagens.</p>

        {% elif status == 'error' %}
        <div class="status error">
            Erro ao obter QR Code: {{ error_message }}
        </div>

        {% else %}
        <div class="status connecting">
            Iniciando sessao...
        </div>
        {% endif %}

        <button onclick="refreshPage()" class="refresh-btn">Atualizar</button>
        <p><small>Esta pagina atualiza automaticamente a cada 10 segundos</small></p>

        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <p><strong>Status:</strong> WAHA rodando em http://localhost:3000</p>
            <p><strong>Sessao:</strong> {{ session_name }}</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def qr_code_page():
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        # Verificar status da sessão primeiro
        status_response = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
            headers=headers,
            timeout=5
        )

        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('status') == 'WORKING':
                return render_template_string(HTML_TEMPLATE, status='connected', session_name=SESSION_NAME)

        # Se sessão não existe, criar
        if status_response.status_code == 404:
            create_data = {"name": SESSION_NAME}
            requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=5)

        # Tentar obter o QR Code
        qr_response = requests.get(
            f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr",
            headers=headers,
            timeout=10
        )

        if qr_response.status_code == 200:
            content_type = qr_response.headers.get('Content-Type', '')

            if 'image' in content_type:
                qr_base64 = base64.b64encode(qr_response.content).decode('utf-8')
                return render_template_string(HTML_TEMPLATE,
                                           qr_code=f"data:image/png;base64,{qr_base64}",
                                           session_name=SESSION_NAME)
            else:
                data = qr_response.json()
                if 'value' in data:
                    return render_template_string(HTML_TEMPLATE,
                                               qr_code=data['value'],
                                               session_name=SESSION_NAME)

            return render_template_string(HTML_TEMPLATE,
                                       status='error',
                                       error_message="QR Code nao encontrado na resposta",
                                       session_name=SESSION_NAME)
        else:
            return render_template_string(HTML_TEMPLATE,
                                       status='error',
                                       error_message=f"Erro na API: {qr_response.status_code}",
                                       session_name=SESSION_NAME)

    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
                                   status='error',
                                   error_message=f"Erro de conexao: {str(e)}",
                                   session_name=SESSION_NAME)

if __name__ == '__main__':
    print("Iniciando servidor QR Code...")
    print("Servidor disponivel em: http://localhost:5000")
    print("Abra este link no navegador para ver o QR Code")

    app.run(host='0.0.0.0', port=5000, debug=False)
