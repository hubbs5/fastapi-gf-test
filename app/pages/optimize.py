import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
import json

from app import app

base_url = "http://127.0.0.1:8000"

layout = html.Div([
    dcc.Location(id='opt-url', refresh=True),
    dbc.Row([
        html.H1('Optimization')]
    ),
    dbc.Row([
        html.Div(id='optimization-response')
    ])
])

@app.callback(
    Output('optimization-response', 'children'),
    Input('opt-url', 'pathname')
)
def get_regions(pathname):
    print(pathname)
    url = base_url + '/regions/'
    response = requests.get(url)
    if response.status_code == 200:
        regions = [i['region'] for i in response.json()]
        out = dcc.Dropdown(
            id='-dropdown',
            options=[{'label': i, 'value': i} for i in regions]
        )
    else:
        out = html.H1('Error: Invalid API Call')

    return out