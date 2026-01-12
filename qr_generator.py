import requests
import webbrowser
import os

# Configurações do WAHA
WAHA_URL = "http://localhost:3000"
WAHA_API_KEY = "your-api-key-here"
SESSION_NAME = "default"

def get_qr_code():
    """Obtém o QR Code da API WAHA"""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": WAHA_API_KEY
        }

        # Primeiro verifica se a sessão existe
        status_response = requests.get(
            f"{WAHA_URL}/api/sessions/{SESSION_NAME}",
            headers=headers,
            timeout=10
        )

        if status_response.status_code == 404:
            print("Criando nova sessao...")
            create_data = {"name": SESSION_NAME}
            requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=10)

        # Buscar QR Code
        response = requests.get(
            f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr",
            headers=headers,
            timeout=10
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image' in content_type:
                return {"qr_image": response.content}
            else:
                return response.json()
        else:
            return None

    except Exception as e:
        print(f"Erro ao obter QR Code: {e}")
        return None

def create_qr_page():
    """Cria uma página HTML simples com instruções"""

    html_content = """
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
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            font-weight: bold;
        }
        .info {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        .instructions {
            margin-top: 20px;
            text-align: left;
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
        }
        .btn {
            background-color: #25d366;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            font-size: 16px;
        }
        .btn:hover {
            background-color: #1eb856;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WhatsApp QR Code - WAHA</h1>

        <div class="status info">
            O WAHA esta funcionando e gerando QR Codes!
        </div>

        <div class="instructions">
            <h3>Como conectar:</h3>
            <ol>
                <li>Acesse <strong>http://localhost:5000/connect</strong> no navegador</li>
                <li>Escaneie o QR Code com seu WhatsApp</li>
                <li>Aguarde a conexao ser estabelecida</li>
            </ol>
        </div>

        <button class="btn" onclick="window.location.href='http://localhost:5000/connect'">
            Ir para pagina de conexao
        </button>
        <button class="btn" onclick="location.reload()">Atualizar</button>

        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <p><strong>Dica:</strong> O QR Code e renovado automaticamente.</p>
            <p><strong>Status:</strong> WAHA rodando em http://localhost:3000</p>
        </div>
    </div>
</body>
</html>
    """

    # Salvar o arquivo HTML
    with open('qr_whatsapp.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Arquivo HTML criado: qr_whatsapp.html")
    return 'qr_whatsapp.html'

def main():
    print("Configurando QR Code para WhatsApp...")

    # Verificar se o WAHA está rodando
    try:
        headers = {"X-Api-Key": WAHA_API_KEY}
        requests.get(f"{WAHA_URL}/api/sessions", headers=headers, timeout=5)
        print("WAHA esta rodando!")
    except Exception:
        print("WAHA nao esta acessivel. Certifique-se de que o Docker esta rodando.")
        return

    # Criar página informativa
    html_file = create_qr_page()

    # Abrir no navegador
    file_path = os.path.abspath(html_file)
    webbrowser.open(f'file://{file_path}')

    print("\n" + "="*60)
    print("COMO ESCANEAR O QR CODE:")
    print("="*60)
    print("1. Acesse http://localhost:5000/connect")
    print("2. Escaneie o QR Code com seu WhatsApp")
    print("3. Aguarde a conexao")
    print("="*60)

    # Tentar obter informações da API
    print("\nVerificando status da sessao...")
    qr_data = get_qr_code()

    if qr_data:
        print(f"Dados retornados da API: {type(qr_data)}")

    print(f"\nPagina informativa aberta: {file_path}")

if __name__ == "__main__":
    main()
