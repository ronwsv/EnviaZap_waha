import csv
import random
import time
from datetime import datetime
import requests

API_URL = 'http://localhost:5065/api/send'  # Ajuste se necessário

# Mensagens de saudação
MENSAGEM_DIA = 'Bom dia, tudo bom?'
MENSAGEM_TARDE = 'Boa tarde, tudo bom?'
MENSAGEM_RESPOSTA = (
    'Me chamo Ron Williams e ajudo salões como o seu a não perderem mais clientes por agendamento no papel ou no WhatsApp.\n'
    'Posso te mostrar uma forma de organizar melhor os horários e aumentar o número de clientes por dia em 2 minutos?\n'
    'Se quiser, te passo um link rápido pra ver como funciona.'
)

# Função para decidir saudação
def saudacao():
    hora = datetime.now().hour
    return MENSAGEM_DIA if hora < 12 else MENSAGEM_TARDE

# Lê os 10 primeiros contatos do CSV
contatos = []
with open('lista.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i >= 10:
            break
        contatos.append(row['telefone'])

# Envia mensagem simulando comportamento humano
for numero in contatos:
    mensagem = saudacao()
    tempo_escrita = random.uniform(2.5, 7.5)  # tempo para "escrever" a mensagem
    print(f"Digitando para {numero}... ({tempo_escrita:.1f}s)")
    time.sleep(tempo_escrita)
    response = requests.post(API_URL, json={"number": numero, "message": mensagem})
    print(f"Enviado para {numero}: {mensagem} | Status: {response.status_code}")
    tempo_entre = random.uniform(8, 22)  # tempo entre envios
    print(f"Aguardando {tempo_entre:.1f}s antes do próximo...")
    time.sleep(tempo_entre)

print("Envio inicial concluído. Aguarde respostas para enviar a segunda mensagem.")

# Para responder automaticamente, implemente um webhook que detecta respostas e use requests.post(API_URL, ...) para enviar MENSAGEM_RESPOSTA.