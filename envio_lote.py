import csv
import random
import time
from datetime import datetime
import requests
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
API_URL = 'http://localhost:5065/api/send'

MENSAGEM_DIA = 'Bom dia, tudo bom?'
MENSAGEM_TARDE = 'Boa tarde, tudo bom?'
MENSAGEM_RESPOSTA = (
    'Me chamo Ron Williams e ajudo salões como o seu a não perderem mais clientes por agendamento no papel ou no WhatsApp.\n'
    'Posso te mostrar uma forma de organizar melhor os horários e aumentar o número de clientes por dia em 2 minutos?\n'
    'Se quiser, te passo um link rápido pra ver como funciona.'
)

def saudacao():
    hora = datetime.now().hour
    return MENSAGEM_DIA if hora < 12 else MENSAGEM_TARDE

@app.route('/api/envio_lote', methods=['POST'])
def envio_lote():
    # Envia para os 10 primeiros contatos da lista.csv
    contatos = []
    with open('lista.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:
                break
            contatos.append(row['telefone'])
    resultados = []
    for numero in contatos:
        mensagem = saudacao()
        tempo_escrita = random.uniform(2.5, 7.5)
        time.sleep(tempo_escrita)
        response = requests.post(API_URL, json={"number": numero, "message": mensagem})
        resultados.append({"numero": numero, "status": response.status_code, "mensagem": mensagem})
        tempo_entre = random.uniform(8, 22)
        time.sleep(tempo_entre)
    return jsonify({"resultados": resultados})

if __name__ == '__main__':
    app.run(debug=True, port=5070)
