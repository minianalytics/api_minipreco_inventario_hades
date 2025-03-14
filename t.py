import requests
import json

# URL do endpoint que retorna os dados
api_url = "https://api-minipreco-inventario-hermes.onrender.com/ver-dados/"

# Nome do arquivo para salvar os dados localmente
arquivo_local = "dados_baixados.json"

try:
    # Faz uma requisição GET para o endpoint
    response = requests.get(api_url)
    response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

    # Obtém os dados da resposta (em formato JSON)
    dados = response.json()

    # Salva os dados no arquivo local
    with open(arquivo_local, "w") as file:
        json.dump(dados, file, indent=4)

    print(f"Dados baixados com sucesso e salvos no arquivo '{arquivo_local}'!")

except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar a API: {e}")
except Exception as e:
    print(f"Erro ao salvar os dados: {e}")