from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configurações do WAHA - com suporte a variáveis de ambiente
WAHA_URL = os.getenv('WAHA_URL', 'http://waha:3000')
WAHA_API_KEY = os.getenv('WAHA_API_KEY', 'your-api-key-here')
SESSION_NAME = os.getenv('SESSION_NAME', 'default')

headers = {
    "X-Api-Key": WAHA_API_KEY,
    "Content-Type": "application/json"
}

class WhatsAppManager:
    def __init__(self):
        self.status = 'containerized'
        self.last_check = None

    def get_instance_status(self):
        """Obtém status da sessão WAHA"""
        try:
            print(f"🔍 Verificando status da sessão...")
            response = requests.get(f"{WAHA_URL}/api/sessions/{SESSION_NAME}", headers=headers, timeout=5)
            print(f"📡 Status Response Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"📊 Session data: {data}")

                # Extrai dados relevantes do WAHA
                status = data.get('status', 'unknown')
                me = data.get('me', {})

                self.status = status
                self.last_check = datetime.now().strftime('%H:%M:%S')

                return {
                    'status': status,
                    'ownerJid': me.get('id', ''),
                    'profileName': me.get('pushName', ''),
                    'number': me.get('id', '').split('@')[0] if me.get('id') else '',
                    'last_check': self.last_check,
                    'connected': status == 'WORKING'
                }
            else:
                print(f"❌ Erro no status: {response.status_code} - {response.text}")
                return {'status': 'docker_demo', 'message': 'Flask app rodando no Docker!', 'connected': False}
        except Exception as e:
            print(f"❌ Exceção no status: {str(e)}")
            # Modo demonstração para Docker
            self.last_check = datetime.now().strftime('%H:%M:%S')
            return {
                'status': 'docker_demo',
                'message': 'Flask app containerizada com sucesso!',
                'connected': False,
                'last_check': self.last_check,
                'docker_info': {
                    'container': 'whatsapp_flask_app',
                    'network': 'whatsapp_network',
                    'port': '5000',
                    'waha_url': WAHA_URL
                }
            }

    def get_qr_code(self):
        """Obtém o QR code para conexão"""
        try:
            # Primeiro verifica se a sessão existe
            status_response = requests.get(f"{WAHA_URL}/api/sessions/{SESSION_NAME}", headers=headers, timeout=5)

            if status_response.status_code == 404:
                # Criar sessão
                create_data = {"name": SESSION_NAME}
                requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=5)

            response = requests.get(f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr", headers=headers, timeout=5)

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'image' in content_type:
                    import base64
                    qr_base64 = base64.b64encode(response.content).decode('utf-8')
                    return {
                        'success': True,
                        'qr_code': f"data:image/png;base64,{qr_base64}",
                        'message': 'QR Code gerado com sucesso'
                    }

            return {'success': False, 'message': 'WAHA não disponível no momento'}

        except Exception as e:
            print(f"❌ Erro na requisição QR: {str(e)}")
            return {
                'success': False,
                'message': 'Flask rodando no Docker! Para testar totalmente, inicie o WAHA.',
                'docker_demo': True
            }

    def send_message(self, number, message):
        """Envia mensagem via WhatsApp"""
        try:
            # Limpar e formatar número
            clean_number = ''.join(filter(str.isdigit, number))
            if len(clean_number) == 11:  # Número brasileiro com DDD
                clean_number = f"55{clean_number}"
            elif len(clean_number) == 10:  # Número brasileiro sem 9
                clean_number = f"559{clean_number}"

            message_data = {
                "chatId": f"{clean_number}@c.us",
                "text": message,
                "session": SESSION_NAME
            }

            response = requests.post(
                f"{WAHA_URL}/api/sendText",
                headers=headers,
                json=message_data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'message': 'Mensagem enviada com sucesso!',
                    'number': clean_number
                }
            else:
                return {
                    'success': False,
                    'message': f'Erro ao enviar: {response.status_code} - {response.text}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Demo Docker: Mensagem "{message}" seria enviada para {number} via WAHA (quando disponível)'
            }

    def restart_instance(self):
        """Reinicia a sessão"""
        try:
            response = requests.post(f"{WAHA_URL}/api/sessions/{SESSION_NAME}/restart", headers=headers, timeout=5)
            if response.status_code in [200, 201]:
                return {'success': True, 'message': 'Sessão reiniciada'}
            else:
                return {'success': False, 'message': f'Erro {response.status_code}'}
        except Exception as e:
            return {'success': False, 'message': 'Flask app containerizada funcionando! WAHA não conectado.'}

# Instância global do gerenciador
whatsapp_manager = WhatsAppManager()

@app.route('/')
def index():
    """Dashboard principal"""
    status_info = whatsapp_manager.get_instance_status()
    return render_template('index.html', status=status_info)

@app.route('/connect')
def connect():
    """Página de conexão com QR Code"""
    status_info = whatsapp_manager.get_instance_status()
    qr_info = whatsapp_manager.get_qr_code()
    return render_template('connect.html', qr=qr_info, status=status_info)

@app.route('/send')
def send():
    """Página de envio de mensagens"""
    status_info = whatsapp_manager.get_instance_status()
    return render_template('send.html', status=status_info)

# API Routes
@app.route('/api/status')
def api_status():
    """API para verificar status"""
    return jsonify(whatsapp_manager.get_instance_status())

@app.route('/api/qr')
def api_qr():
    """API para obter QR Code"""
    return jsonify(whatsapp_manager.get_qr_code())

@app.route('/api/send', methods=['POST'])
def api_send():
    """API para enviar mensagem"""
    data = request.get_json()

    if not data or not data.get('number') or not data.get('message'):
        return jsonify({'success': False, 'message': 'Número e mensagem são obrigatórios'})

    result = whatsapp_manager.send_message(data['number'], data['message'])
    return jsonify(result)

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """API para reiniciar sessão"""
    result = whatsapp_manager.restart_instance()
    return jsonify(result)

@app.route('/docker-info')
def docker_info():
    """Página com informações do Docker"""
    return jsonify({
        'container_name': 'whatsapp_flask_app',
        'network': 'whatsapp_network',
        'port': '5000',
        'waha_url': WAHA_URL,
        'status': 'containerized_successfully',
        'environment': {
            'WAHA_URL': WAHA_URL,
            'WAHA_API_KEY': WAHA_API_KEY[:10] + '...' if len(WAHA_API_KEY) > 10 else WAHA_API_KEY,
            'SESSION_NAME': SESSION_NAME,
            'FLASK_ENV': os.getenv('FLASK_ENV', 'development'),
            'PORT': os.getenv('PORT', '5000')
        }
    })

if __name__ == '__main__':
    print("APLICAÇÃO FLASK CONTAINERIZADA COM DOCKER")
    print("=" * 60)
    print("Sistema de Automação WhatsApp com WAHA")
    print(f"WAHA API: {WAHA_URL}")
    print(f"Session: {SESSION_NAME}")
    print(f"Container: whatsapp_flask_app")
    print(f"Network: whatsapp_network")
    print("=" * 60)

    # Configuração para produção ou desenvolvimento
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'  # Permite acesso externo no container

    app.run(host=host, port=port, debug=debug_mode)
