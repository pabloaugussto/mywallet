import requests

# URL do seu bot local
url = 'http://127.0.0.1:8000/webhook/'

# Dados falsos fingindo ser o WhatsApp
dados = {
    'Body': 'Uber 20.00',
    'From': 'whatsapp:+551199999999'
}

try:
    print(f"🤖 Enviando 'Uber 20.00' para {url}...")
    response = requests.post(url, data=dados)
    print(f"Resposta do Servidor: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Erro: {e}")