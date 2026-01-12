from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import json
import os
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Arquivo .env carregado com sucesso")
except ImportError:
    print("⚠️ python-dotenv não encontrado. Usando variáveis padrão.")

app = Flask(__name__)

# Configurações do WAHA - com suporte a variáveis de ambiente
WAHA_URL = os.getenv('WAHA_URL', 'http://localhost:3000')
WAHA_API_KEY = os.getenv('WAHA_API_KEY', 'your-api-key-here')
SESSION_NAME = os.getenv('SESSION_NAME', 'default')

headers = {
    "X-Api-Key": WAHA_API_KEY,
    "Content-Type": "application/json"
}

class WhatsAppManager:
    def __init__(self):
        self.status = 'unknown'
        self.last_check = None
        self.connection_events = []  # Para armazenar eventos de conexão

    def add_connection_event(self, event):
        """Adiciona evento de conexão"""
        self.connection_events.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'event': event
        })
        # Manter apenas os últimos 10 eventos
        if len(self.connection_events) > 10:
            self.connection_events.pop(0)

    def get_instance_status(self):
        """Obtém status da sessão WAHA"""
        try:
            print(f"🔍 Verificando status da sessão...")
            response = requests.get(f"{WAHA_URL}/api/sessions/{SESSION_NAME}", headers=headers, timeout=10)
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
                    'connected': status == 'WORKING',
                    'events': self.connection_events
                }
            elif response.status_code == 404:
                # Sessão não existe, tentar criar
                print(f"⚠️ Sessão '{SESSION_NAME}' não encontrada. Tentando criar...")
                return self.create_session()
            else:
                print(f"❌ Erro no status: {response.status_code} - {response.text}")
                return {'status': 'error', 'message': f'Erro {response.status_code}', 'connected': False}
        except Exception as e:
            print(f"❌ Exceção no status: {str(e)}")
            return {'status': 'error', 'message': str(e), 'connected': False}

    def get_qr_code(self):
        """Obtém o QR code para conexão"""
        try:
            print(f"🔗 Tentando gerar QR Code...")

            # Primeiro verifica se a sessão existe
            status_response = requests.get(f"{WAHA_URL}/api/sessions/{SESSION_NAME}", headers=headers, timeout=10)

            if status_response.status_code == 404:
                # Criar sessão
                print(f"📝 Criando nova sessão...")
                create_data = {"name": SESSION_NAME}
                requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=10)

            # Buscar QR Code
            print(f"🌐 URL: {WAHA_URL}/api/{SESSION_NAME}/auth/qr")
            response = requests.get(f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr", headers=headers, timeout=10)
            print(f"📡 QR Status Code: {response.status_code}")

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
                else:
                    data = response.json()
                    if 'value' in data:
                        return {
                            'success': True,
                            'qr_code': data['value'],
                            'message': 'QR Code gerado com sucesso'
                        }

            return {'success': False, 'message': 'QR code não disponível no momento'}

        except Exception as e:
            print(f"❌ Erro na requisição QR: {str(e)}")
            return {'success': False, 'message': f'Erro de conexão: {str(e)}'}

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
                timeout=30
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
                'message': f'Erro de conexão: {str(e)}'
            }

    def create_session(self):
        """Cria uma nova sessão no WAHA"""
        try:
            print(f"🔧 Criando nova sessão '{SESSION_NAME}'...")

            session_data = {
                "name": SESSION_NAME
            }

            response = requests.post(
                f"{WAHA_URL}/api/sessions/start",
                headers=headers,
                json=session_data,
                timeout=10
            )

            print(f"📡 Create Session Status Code: {response.status_code}")
            print(f"📝 Create Session Response: {response.text}")

            if response.status_code in [200, 201]:
                print(f"✅ Sessão '{SESSION_NAME}' criada com sucesso!")
                return {
                    'status': 'STARTING',
                    'message': 'Sessão criada. Aguardando conexão...',
                    'connected': False,
                    'last_check': datetime.now().strftime('%H:%M:%S')
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Erro ao criar sessão: {response.status_code} - {response.text}',
                    'connected': False
                }

        except Exception as e:
            print(f"❌ Erro ao criar sessão: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erro ao criar sessão: {str(e)}',
                'connected': False
            }

    def restart_instance(self):
        """Reinicia a sessão"""
        try:
            response = requests.post(f"{WAHA_URL}/api/sessions/{SESSION_NAME}/restart", headers=headers)
            if response.status_code in [200, 201]:
                return {'success': True, 'message': 'Sessão reiniciada'}
            else:
                return {'success': False, 'message': f'Erro {response.status_code}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

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
    if status_info.get('status') != 'WORKING':
        return redirect(url_for('connect'))
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

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para receber webhooks do WAHA"""
    try:
        data = request.get_json()
        event_type = data.get('event')
        session_name = data.get('session')

        print(f"🔔 WEBHOOK RECEBIDO: {event_type} para sessão {session_name}")
        print(f"📄 Dados: {json.dumps(data, indent=2)}")

        # Adicionar evento à lista de eventos
        whatsapp_manager.add_connection_event({
            'type': event_type,
            'data': data
        })

        # Processar eventos específicos do WAHA
        if event_type == 'session.status':
            status = data.get('payload', {}).get('status')
            print(f"🔗 Status de sessão atualizado: {status}")

            if status == 'WORKING':
                print("✅ WhatsApp conectado com sucesso via WEBHOOK!")
                whatsapp_manager.status = 'WORKING'

        elif event_type == 'message':
            print("💬 Nova mensagem recebida via WEBHOOK!")
            payload = data.get('payload', {})
            print(f"📨 Mensagem: {payload.get('body', 'Sem texto')}")

        elif event_type == 'message.any':
            print("📤 Evento de mensagem recebido")

        return jsonify({'status': 'success', 'received': True}), 200

    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook-test')
def webhook_test():
    """Página para testar webhook"""
    return f"""
    <h2>🔔 Webhook Test - WAHA</h2>
    <p><strong>URL do Webhook:</strong> <code>http://localhost:5000/webhook</code></p>
    <p><strong>Eventos Recentes:</strong></p>
    <ul>
    {''.join([f'<li>{event["timestamp"]} - {event["event"]["type"]}</li>' for event in whatsapp_manager.connection_events])}
    </ul>
    <a href="/">← Voltar ao Dashboard</a>
    """

if __name__ == '__main__':
    print("🚀 INICIANDO APLICAÇÃO WHATSAPP FLASK COM WEBHOOKS")
    print("=" * 60)
    print("📱 Sistema de Automação WhatsApp com WAHA")
    print(f"🌐 WAHA API: {WAHA_URL}")
    print(f"🔧 Session: {SESSION_NAME}")
    print(f"🔔 Webhook URL: http://localhost:5000/webhook")
    print("=" * 60)

    # Configuração para produção ou desenvolvimento
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'  # Permite acesso externo no container

    app.run(host=host, port=port, debug=debug_mode)
