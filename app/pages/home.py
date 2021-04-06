import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import requests
import json
import pandas as pd

from app import app

base_url = "http://127.0.0.1:8000"

layout = html.Div([
    dcc.Location(id='home-url', refresh=True),
    dbc.Row([
        html.H1('Select Region and Year')
    ]),
    dbc.Row([
        dbc.Col([
            html.H4('Region'),
            html.Div(id='region-response')
        ],
            width=3
        ),
        dbc.Col([
            html.H4('Year'),
            html.Div(id='year-response')
        ],
            width=3
        ),
    ]),
    html.Br(),
    dbc.Row([
        html.Button('Get Data', id='get-data')
    ]),
    html.Br(),
    dbc.Row([
        html.Div(id='greenfield-data')
    ])
])

@app.callback(
    Output('region-response', 'children'),
    Input('home-url', 'pathname')
)
def get_regions(pathname):
    url = base_url + '/regions/'
    response = requests.get(url)
    if response.status_code == 200:
        regions = [i['region'] for i in response.json()]
        out = dcc.Dropdown(
            id='region-dropdown',
            options=[{'label': i, 'value': i} for i in regions]
        )
    else:
        out = html.H1('Error: Invalid API call to "regions".')

    return out

@app.callback(
    Output('year-response', 'children'),
    Input('home-url', 'pathname')
)
def get_years(pathname):
    url = base_url + '/years/'
    response = requests.get(url)
    if response.status_code == 200:
        years = [i for i in response.json()]
        out = dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': i, 'value': i} for i in years]
        )
    else:
        out = html.H1('Error: Invalid API call to "years".')
    
    return out

@app.callback(
    Output('greenfield-data', 'children'),
    [Input('get-data', 'n_clicks')],
    [State('region-response', 'children'),
     State('year-response', 'children')]
)
def get_data(n_clicks, region, year):
    url = base_url + '/data/'
    params = {'region': region, 'year': year}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        out = json.loads(response.json())
        data = pd.DataFrame(out)
    else:
        out = html.H1('Error: Invalid API call to "data".')

    return out
