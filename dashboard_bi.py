import dash
from dash import dcc, html, Input, Output, State
import dash_table
import pandas as pd
import requests
from flask import Flask, request, jsonify
import os
from datetime import datetime
import base64
import io

# Inicialização do aplicativo Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard de Inventário"),
    
    # Botão para iniciar o inventário
    html.Button('Iniciar Inventário', id='iniciar-inventario', n_clicks=0),
    html.Div(id='status-inventario'),
    
    # Upload de arquivo CSV/Excel
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Arraste e solte ou ',
            html.A('selecione um arquivo')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    
    # Tabela para exibir os dados
    dash_table.DataTable(
        id='tabela-inventario',
        columns=[
            {'name': 'Produto', 'id': 'produto'},
            {'name': 'Quantidade em Estoque', 'id': 'quantidade_estoque'},
            {'name': 'Quantidade Contada', 'id': 'quantidade_contada'},
            {'name': 'Diferença', 'id': 'diferenca'},
            {'name': 'Recontagem', 'id': 'recontagem', 'presentation': 'dropdown'}
        ],
        data=[],
        editable=True,
        dropdown={
            'recontagem': {
                'options': [
                    {'label': 'Sim', 'value': 1},
                    {'label': 'Não', 'value': 0}
                ]
            }
        }
    ),
    
    # Intervalo para atualização automática
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # em milissegundos
        n_intervals=0
    )
])

# Callback para iniciar o inventário
@app.callback(
    Output('status-inventario', 'children'),
    Input('iniciar-inventario', 'n_clicks')
)
def iniciar_inventario(n_clicks):
    if n_clicks > 0:
        return "Inventário iniciado!"
    return ""

# Callback para upload de arquivo
@app.callback(
    Output('tabela-inventario', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def upload_arquivo(contents, filename):
    if contents is not None:
        # Decodifica o conteúdo do arquivo
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Lê o arquivo CSV
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Calcula a diferença e ordena
        df['diferenca'] = df['quantidade_contada'] - df['quantidade_estoque']
        df = df.sort_values(by='diferenca', ascending=False)
        
        return df.to_dict('records')
    return []

# Callback para atualização automática
@app.callback(
    Output('tabela-inventario', 'data'),
    Input('interval-component', 'n_intervals')
)
def atualizar_tabela(n_intervals):
    # Aqui você pode adicionar a lógica para baixar novos dados da API
    # e atualizar a tabela automaticamente
    pass

# API para receber dados
@server.route('/api/dados', methods=['POST'])
def receber_dados():
    dados = request.json
    df = pd.DataFrame(dados)
    df.to_csv('dados_inventario.csv', index=False)
    return jsonify({"status": "sucesso"})

if __name__ == '__main__':
    app.run_server(debug=True)