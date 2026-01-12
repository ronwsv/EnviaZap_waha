from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import time
import json
import os
from datetime import datetime
import csv

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
                    'connected': status == 'WORKING'
                }
            elif response.status_code == 404:
                # Sessão não existe
                return {'status': 'not_found', 'message': 'Sessão não encontrada', 'connected': False}
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

            # Primeiro verifica se a sessão existe, se não, cria
            status_response = requests.get(f"{WAHA_URL}/api/sessions/{SESSION_NAME}", headers=headers, timeout=10)

            if status_response.status_code == 404:
                # Criar sessão
                print(f"📝 Criando nova sessão...")
                create_data = {"name": SESSION_NAME}
                create_response = requests.post(f"{WAHA_URL}/api/sessions/start", headers=headers, json=create_data, timeout=10)
                print(f"📡 Create Session Response: {create_response.status_code}")

            # Buscar QR Code
            print(f"🌐 URL: {WAHA_URL}/api/sessions/{SESSION_NAME}/auth/qr")
            response = requests.get(f"{WAHA_URL}/api/{SESSION_NAME}/auth/qr", headers=headers, timeout=10)
            print(f"📡 QR Status Code: {response.status_code}")

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')

                if 'image' in content_type:
                    # QR Code retornado como imagem
                    import base64
                    qr_base64 = base64.b64encode(response.content).decode('utf-8')
                    return {
                        'success': True,
                        'qr_code': f"data:image/png;base64,{qr_base64}",
                        'message': 'QR Code gerado com sucesso'
                    }
                else:
                    # Pode ser JSON com base64
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

            print(f"📤 ENVIANDO MENSAGEM:")
            print(f"   📞 Número original: {number}")
            print(f"   📞 Número formatado: {clean_number}")
            print(f"   💬 Mensagem: {message[:50]}...")
            print(f"   🌐 URL: {WAHA_URL}/api/sendText")

            # Formato WAHA para envio de mensagem
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

            print(f"   📡 Status Code: {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}...")

            if response.status_code in [200, 201]:
                print(f"   ✅ SUCESSO - Mensagem enviada!")
                return {
                    'success': True,
                    'message': 'Mensagem enviada com sucesso!',
                    'number': clean_number
                }
            else:
                print(f"   ❌ ERRO - Status: {response.status_code}")
                return {
                    'success': False,
                    'message': f'Erro ao enviar: {response.status_code} - {response.text}'
                }

        except Exception as e:
            print(f"   💥 EXCEÇÃO: {str(e)}")
            return {
                'success': False,
                'message': f'Erro de conexão: {str(e)}'
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

# Webhook endpoint para receber eventos do WAHA
@app.route('/webhook', methods=['POST'])
def webhook():
    """Recebe eventos do WAHA via webhook"""
    try:
        webhook_data = request.get_json()

        if not webhook_data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        # Log do evento recebido
        event_type = webhook_data.get('event', 'unknown')
        session_name = webhook_data.get('session', 'unknown')

        print(f"🔔 WEBHOOK RECEBIDO:")
        print(f"   📍 Evento: {event_type}")
        print(f"   🏷️  Sessão: {session_name}")
        print(f"   📦 Dados: {json.dumps(webhook_data, indent=2)}")

        # Processar eventos específicos do WAHA
        if event_type == 'session.status':
            status = webhook_data.get('payload', {}).get('status')
            print(f"   🔗 Status de sessão: {status}")

            if status == 'WORKING':
                print(f"   ✅ WhatsApp conectado com sucesso!")
                whatsapp_manager.status = 'WORKING'

        elif event_type == 'message':
            message_data = webhook_data.get('payload', {})
            print(f"   📱 Nova mensagem recebida")

        elif event_type == 'message.any':
            print(f"   📤 Evento de mensagem")

        return jsonify({'success': True, 'message': 'Webhook processed successfully'}), 200

    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return jsonify({'success': False, 'message': f'Webhook error: {str(e)}'}), 500

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

@app.route('/api/contatos_lote')
def api_contatos_lote():
    import pandas as pd
    contatos = []
    try:
        df = pd.read_csv('lista_simplificada.csv', dtype=str)
        for _, row in df.iterrows():
            telefone = str(row.get('telefone', '')).strip()
            nome = str(row.get('nome', '')).strip()
            if telefone:
                contatos.append({
                    'nome': nome,
                    'telefone': telefone
                })
    except Exception as e:
        print(f"Erro ao ler lista_simplificada.csv com pandas: {e}")
    return jsonify(contatos)

@app.route('/api/carregar_csv')
def api_carregar_csv():
    """API para carregar contatos do CSV lista_simplificada.csv"""
    contatos = []
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None

        # Tentar com pandas primeiro
        try:
            import pandas as pd
            for encoding in encodings:
                try:
                    df = pd.read_csv('lista_simplificada.csv', dtype=str, encoding=encoding)
                    print(f"CSV carregado com encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue

            if df is not None:
                for _, row in df.iterrows():
                    telefone = str(row.get('telefone', '')).strip()
                    nome = str(row.get('nome', '')).strip()
                    if telefone and nome:
                        contatos.append({
                            'nome': nome,
                            'telefone': telefone
                        })
            else:
                raise Exception("Não foi possível decodificar o CSV com nenhum encoding")

        except ImportError:
            # Fallback para csv nativo se pandas não estiver disponível
            for encoding in encodings:
                try:
                    with open('lista_simplificada.csv', 'r', encoding=encoding) as file:
                        reader = csv.DictReader(file)
                        contatos = []
                        for row in reader:
                            telefone = row.get('telefone', '').strip()
                            nome = row.get('nome', '').strip()
                            if telefone and nome:
                                contatos.append({
                                    'nome': nome,
                                    'telefone': telefone
                                })
                        print(f"CSV carregado com encoding: {encoding}")
                        break
                except UnicodeDecodeError:
                    continue

            if not contatos:
                raise Exception("Não foi possível decodificar o CSV com nenhum encoding")

    except FileNotFoundError:
        return jsonify({'error': 'Arquivo lista_simplificada.csv não encontrado'}), 404
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return jsonify({'error': f'Erro ao carregar CSV: {str(e)}'}), 500

    print(f"Total de contatos carregados: {len(contatos)}")
    return jsonify(contatos)

if __name__ == '__main__':
    print("INICIANDO APLICACAO WHATSAPP FLASK")
    print("=" * 50)
    print("Sistema de Automacao WhatsApp com WAHA")
    print(f"WAHA API: {WAHA_URL}")
    print(f"Session: {SESSION_NAME}")
    print("=" * 50)

    # Configuração para produção ou desenvolvimento
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    port = int(os.getenv('PORT', 5065))
    host = '0.0.0.0'  # Permite acesso externo no container

    app.run(host=host, port=port, debug=debug_mode)
