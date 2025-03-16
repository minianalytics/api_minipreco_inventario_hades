# Exemplo de como pegar o token para uso na API
import requests

# URL do endpoint para gerar o token
url = "http://127.0.0.1:8000/auth/gerar-token/"

# Dados de autenticação (email como string simples)
payload = "miqueias.silva@grupominopreco.com.br"  # String simples do email

# Cabeçalhos da requisição
headers = {
    "accept": "application/json",
    "Content-Type": "text/plain"  # Cabeçalho correto para texto simples
}

# Fazendo a requisição para obter o token
response = requests.post(url, data=payload, headers=headers)  # Usando 'data' para enviar a string diretamente

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    # Extraindo o token da resposta
    data = response.json()
    token = data.get("token")  # Campo 'token' contém o token
    if token:
        print(f"Token obtido: {token}")
    else:
        print("O campo 'token' não foi encontrado na resposta.")
else:
    # Caso ocorra um erro
    print(f"Erro ao obter o token: {response.status_code}")
    print(response.text)