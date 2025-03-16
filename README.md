# api_minipreco_inventario_hermes
Api que coleta dados do nosso inventario


Código da Loja
Código do Operador
Código da TAG
Código do Produto
Quantidade Contada


usar:
uvicorn main:app --reload
uvicorn teste_api:app --reload


#Criar Dashboard para Acompanhar contagem do Inventario
#Iniciar o inventario
#Opções se sim ou não para o envio
#Criar botão que vai iniciar o inventario perguntando se deseja iniciar
#FAzer upload de arquivo csv/excel para a contagem
#Iniciar a API a baixar os dados que serão enviados para a APi, de minuto em muinuto verifica se tem arquivo novo e faz o download
#Dados vem em json e eles precisam ser convertidos para CSV para pode trabalhar na API com eles
#Criar tabela com os dados que vem do arquivo inicial do inventario
#Tabela deve mostrar os dados de produto, quantidade_em_estoque, quantidade_contada que sera atualizada cada vez que os dados aparecerem
#Deixar a tabela sendo atualizada automaticamente
#criar uma coluna chamada "diferenca" fazendo a diferença entre a quantidade_contada - quantidade_estoque e deixar a tabela ordenada para ficar do maior pro menor da coluna diferença
#tem que ter um check para o usuario selecionar se daquele produto ele vai considerar a recontagem ou não e quando ele pedir para considerar a recontagem, ele vai somar dados só onde a coluna la do arquivo for 1
