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

def aguardar_e_tentar():
    print("⏰ ESTRATÉGIA DE ESPERA INTELIGENTE")
    print("=" * 50)
    print("💡 Você conseguiu conectar antes - vamos aguardar o bloqueio passar")
    print("=" * 50)
    
    # Criar página de status com timer
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp - Aguardando Desbloqueio</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 600px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border-radius: 25px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        .title {{
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        .timer-container {{
            background: rgba(255, 255, 255, 0.2);
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }}
        .timer {{
            font-size: 4em;
            font-weight: bold;
            color: #FFD700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin: 20px 0;
        }}
        .status {{
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 12px;
            margin: 25px 0;
        }}
        .success-msg {{
            background: rgba(0, 255, 0, 0.3);
            padding: 20px;
            border-radius: 12px;
            margin: 25px 0;
            border-left: 5px solid #00FF00;
        }}
        .instructions {{
            background: rgba(0, 0, 0, 0.2);
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            text-align: left;
        }}
        .step {{
            margin: 15px 0;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .step:last-child {{
            border-bottom: none;
        }}
        .highlight {{
            background: rgba(255, 255, 0, 0.3);
            padding: 3px 8px;
            border-radius: 5px;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
            border-radius: 10px;
            transition: width 1s ease;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .footer {{
            margin-top: 30px;
            font-style: italic;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">⏰ Aguardando Desbloqueio</div>
        
        <div class="success-msg">
            ✅ <strong>VOCÊ JÁ CONSEGUIU CONECTAR ANTES!</strong><br>
            O bloqueio é temporário - vamos aguardar passar
        </div>
        
        <div class="timer-container">
            <div>Tempo restante:</div>
            <div class="timer" id="timer">15:00</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress" style="width: 0%"></div>
            </div>
        </div>
        
        <div class="status">
            <strong>📊 Status atual:</strong><br>
            • Contador QR: 12 (muitas tentativas)<br>
            • Status: "Tente mais tarde" ativo<br>
            • Estimativa: 15 minutos para desbloqueio<br>
            • Método: Aguardar reset automático
        </div>
        
        <div class="instructions">
            <h3>📱 ENQUANTO AGUARDA:</h3>
            
            <div class="step">
                1. <span class="highlight">FECHE</span> o WhatsApp Business completamente
            </div>
            
            <div class="step">
                2. <span class="highlight">REINICIE</span> o celular (opcional, mas recomendado)
            </div>
            
            <div class="step">
                3. <span class="highlight">AGUARDE</span> este timer chegar a zero
            </div>
            
            <div class="step">
                4. Quando o timer acabar, <span class="highlight">recarregue esta página</span>
            </div>
            
            <div class="step">
                5. Tente conectar <span class="highlight">UMA ÚNICA VEZ</span>
            </div>
        </div>
        
        <div class="footer">
            Evolution API - Sistema de Desbloqueio Automático<br>
            Iniciado em: {time.strftime('%H:%M:%S')}
        </div>
    </div>
    
    <script>
        let timeLeft = 15 * 60; // 15 minutos em segundos
        const totalTime = timeLeft;
        
        function updateTimer() {{
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            document.getElementById('timer').textContent = 
                `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
            
            // Atualizar barra de progresso
            const progress = ((totalTime - timeLeft) / totalTime) * 100;
            document.getElementById('progress').style.width = `${{progress}}%`;
            
            if (timeLeft <= 0) {{
                // Timer acabou - recarregar para nova tentativa
                document.getElementById('timer').textContent = "00:00";
                document.getElementById('timer').style.color = "#00FF00";
                document.querySelector('.timer-container').innerHTML = `
                    <div style="color: #00FF00; font-size: 2em; font-weight: bold;">
                        ✅ TEMPO ESGOTADO!<br>
                        <button onclick="location.reload()" style="background: #00FF00; color: black; border: none; padding: 15px 30px; border-radius: 10px; font-size: 18px; cursor: pointer; margin-top: 20px;">
                            🔄 TENTAR NOVA CONEXÃO
                        </button>
                    </div>
                `;
                return;
            }}
            
            timeLeft--;
            setTimeout(updateTimer, 1000);
        }}
        
        updateTimer();
    </script>
</body>
</html>"""
    
    with open("aguardar_desbloqueio.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ PÁGINA DE ESPERA CRIADA!")
    print("📄 Arquivo: aguardar_desbloqueio.html")
    print("\n🎯 ESTRATÉGIA:")
    print("1. Aguardar 15 minutos para o WhatsApp resetar o bloqueio")
    print("2. Durante este tempo, feche o WhatsApp Business")
    print("3. Opcionalmente, reinicie o celular")
    print("4. Quando o timer acabar, tente UMA única vez")
    print("5. Como você já conseguiu conectar antes, deve funcionar!")
    
    print(f"\n⏰ Iniciando contagem regressiva de 15 minutos...")
    print(f"   Horário atual: {time.strftime('%H:%M:%S')}")
    print(f"   Fim estimado: {time.strftime('%H:%M:%S', time.localtime(time.time() + 900))}")
    
    return True

def verificar_periodicamente():
    """Verifica o status a cada 5 minutos"""
    print("\n🔍 INICIANDO MONITORAMENTO PERIÓDICO")
    print("   (Verificando a cada 5 minutos se o bloqueio passou)")
    
    for i in range(3):  # 3 verificações = 15 minutos
        print(f"\n⏳ Aguardando {5} minutos... (Verificação {i+1}/3)")
        time.sleep(300)  # 5 minutos
        
        try:
            response = requests.get(f"{EVOLUTION_URL}/instance/fetchInstances/{INSTANCE_NAME}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                qr_data = data.get('qrcode', {})
                count = qr_data.get('count', 0)
                
                print(f"   📊 Contador atual: {count}")
                
                if count < 5:  # Se o contador resetou
                    print("   🎉 CONTADOR RESETOU! Bloqueio pode ter passado!")
                    break
                else:
                    print(f"   ⏳ Ainda bloqueado (contador: {count})")
            else:
                print(f"   ❌ Erro na verificação: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro na verificação: {e}")
    
    print("\n✅ PERÍODO DE ESPERA COMPLETO!")
    print("🎯 Agora tente conectar UMA única vez")

if __name__ == "__main__":
    if aguardar_e_tentar():
        verificar_periodicamente()
