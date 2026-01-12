# 📱 WhatsSender com WAHA

Sistema de automação WhatsApp usando [WAHA (WhatsApp HTTP API)](https://github.com/devlikeapro/waha) integrado com Flask.

## ✨ Funcionalidades

- ✅ Autenticação via QR Code
- ✅ Envio de mensagens simples e em lotes
- ✅ Monitoramento de conexão em tempo real
- ✅ Interface web intuitiva
- ✅ Geração de QR Code estático
- ✅ Docker support para fácil deploy
- ✅ API REST para integração

## 📋 Requisitos

- Docker e Docker Compose
- Python 3.8+ (se rodar sem Docker)
- Internet
- Smartphone com WhatsApp

## 🚀 Início Rápido com Docker

### 1. Gerar API Key

Gere uma chave segura (64 caracteres):

**Windows (PowerShell):**
```powershell
"$([guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N'))"
```

**Linux/Mac:**
```bash
openssl rand -hex 32
```

### 2. Configurar variáveis de ambiente

Edite o arquivo `docker-compose.yml` e substitua `your-api-key-here` pela sua chave em:
- `WAHA_API_KEY` (serviço `waha`)
- `FLASK_API_KEY` (serviço `whatsapp-flask`)

```yaml
environment:
  - WAHA_API_KEY=sua-chave-aqui
  - FLASK_API_KEY=sua-chave-aqui
```

### 3. Iniciar os containers

```bash
docker compose up -d
```

Os serviços estarão disponíveis em:
- **Flask Web**: http://localhost:5065
- **WAHA API**: http://localhost:3000

### 4. Conectar WhatsApp

1. Abra http://localhost:5065 no navegador
2. Clique em "Conectar WhatsApp"
3. Escaneie o QR Code com seu smartphone
4. Aguarde a confirmação de conexão

## 🛠️ Configuração Manual (Sem Docker)

### 1. Clonar o repositório

```bash
git clone https://github.com/ronwsv/EnviaZap_waha.git
cd EnviaZap_waha
```

### 2. Instalar dependências

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env`:

```env
WAHA_URL=http://localhost:3000
WAHA_API_KEY=sua-chave-aqui
SESSION_NAME=default
FLASK_ENV=production
PORT=5065
```

### 4. Iniciar WAHA (em outro terminal)

```bash
docker run -d --name waha \
  -e WHATSAPP_API_KEY=sua-chave-aqui \
  -e WHATSAPP_DEFAULT_ENGINE=WEBJS \
  -p 3000:3000 \
  -v waha_sessions:/app/.sessions \
  devlikeapro/waha:latest
```

### 5. Iniciar Flask

```bash
python app.py
```

## 📚 Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `app.py` | Aplicação Flask principal |
| `envio_simples.py` | Enviar mensagem individual |
| `envio_lote.py` | Enviar múltiplas mensagens |
| `monitor_conexao.py` | Monitorar status da conexão |
| `qr_generator.py` | Gerar QR Codes |
| `requirements.txt` | Dependências Python |
| `docker-compose.yml` | Configuração Docker |
| `Dockerfile` | Imagem Docker da aplicação |

## 🌐 Interface Web

### Dashboard (/)
- Status da conexão WhatsApp
- Informações da sessão
- Atalhos rápidos

### Conectar (/connect)
- Exibição de QR Code
- Status da autenticação

### Enviar Mensagem (/send)
- Envio individual ou em lote
- Upload de CSV
- Histórico de envios

## 🔌 Endpoints da API

### Obter Status
```bash
curl -X GET http://localhost:5065/api/status \
  -H "X-Api-Key: sua-chave-aqui"
```

### Enviar Mensagem
```bash
curl -X POST http://localhost:5065/api/send \
  -H "X-Api-Key: sua-chave-aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "message": "Olá!"
  }'
```

### Obter QR Code
```bash
curl -X GET http://localhost:5065/api/qr \
  -H "X-Api-Key: sua-chave-aqui"
```

## 📊 Formato CSV para Envio em Lote

Crie um arquivo `lista.csv`:

```csv
numero,mensagem
5511999999999,Olá! Como está?
5511988888888,Testando sistema
5511977777777,Mensagem automática
```

Ou use o formato simplificado (`lista_simplificada.csv`):

```csv
5511999999999
5511988888888
5511977777777
```

## 🔐 Segurança

- ⚠️ **Nunca exponha sua API Key**
- ⚠️ **Use HTTPS em produção**
- ⚠️ **Mantenha o arquivo `.env` fora do repositório**
- ✅ Use variáveis de ambiente para secrets
- ✅ Configure firewall para aceitar apenas conexões autorizadas

## 🐛 Troubleshooting

### Erro: "Connection refused" na porta 3000
```bash
# Verificar se container está rodando
docker ps | grep waha

# Ver logs do WAHA
docker logs waha
```

### Erro: "API Key inválida"
- Verifique se a chave está configurada corretamente
- Confirme se ela está em ambos os serviços (Flask e WAHA)

### QR Code não aparece
- Aguarde 5-10 segundos após iniciar
- Recarregue a página
- Verifique logs: `docker logs whatsapp_flask_app`

### Mensagens não são enviadas
- Confirme se WhatsApp está conectado (status WORKING)
- Verifique se o número tem o formato correto (55 + DDD + 9 + número)
- Veja logs da aplicação para detalhes

## 📞 Suporte

Para reportar problemas ou sugerir melhorias, abra uma issue no [repositório GitHub](https://github.com/ronwsv/EnviaZap_waha/issues).

## 📄 Licença

Este projeto é fornecido como está, sem garantias.

## 🙏 Créditos

- [WAHA](https://github.com/devlikeapro/waha) - WhatsApp HTTP API
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Docker](https://www.docker.com/) - Containerização

---

**Desenvolvido com ❤️ para automação de WhatsApp**
