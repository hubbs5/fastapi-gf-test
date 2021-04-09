import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table as dt
import requests
import pandas as pd
import numpy as np
import json
import folium
from folium import plugins

# from pages import home, optimize
from app import app
import utils

# PAGES = ['/home', '/optimization']

base_url = "http://127.0.0.1:8000"

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div([
    html.H1("Greenfield Optimization"),
    html.Hr(),
    # html.P(
        # "", className="lead"
    # ),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink("Digital Twin Home", href="/home")), 
        dbc.NavItem(dbc.NavLink("Greenfield Algo", 
            href="https://emrahcimren.github.io/data%20science/Greenfield-Analysis-with-Weighted-Clustering/"))
        ],
        vertical=True,
        pills=True,
    ),
    ],
    style=SIDEBAR_STYLE,
)

layout = html.Div([
    # sidebar,
    dcc.Location(id='base-url', refresh=True),
    dbc.Row([
        dbc.Col([
            sidebar,
        ],
            width=3
        ),
        dbc.Col([
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
            ]),

            # Optimization
            html.Br(),
            dbc.Row([
                    html.H1('Optimization')]
                ),
            dbc.Row([
                dbc.Col([
                    html.H5('Select Number of Distribution Centers'),
                    dcc.Slider(id='dc-loc-number',
                        min=1, max=20, step=1, value=5,
                        marks={i:str(i) for i in range(1, 21)}),
                ],
                ),
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5('Max Distribution Center Capacity'),
                    dcc.Input(id='capacity-max-input',
                        type='text',
                        placeholder='Capacity in annual KG'),
                    html.Br(),
                    html.H5('Min Distribution Center Capacity'),
                    dcc.Input(id='capacity-min-input',
                        type='text',
                        placeholder='Capacity in annual KG'),
                    html.Br(),
                ]),
                dbc.Col([
                    html.H5('Max Customer Distance'),
                    # html.Caption('Enter 0 or None to remove limits.'),
                    dcc.Input(id='distance-max-input',
                        type='text',
                        placeholder='Shipping distance in KM'),
                    html.Br(),
                    html.H5('Number of Iterations'),
                    dcc.Input(id='iterations-input',
                        type='number',
                        value=5,
                        min=1,
                        max=20,
                        step=1)
                ]),
            ]),
            html.Br(),
            dbc.Row([
                html.Button('Run Optimization Algorithm', id='opt-button')
            ]),
            html.Br(),
            dbc.Row([
                html.Div(id='optimization-response')
            ])
        ],
            width=8
        ),
    ])
])

@app.callback(
    Output('region-response', 'children'),
    Input('base-url', 'pathname')
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
    Input('base-url', 'pathname')
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
def get_data(n_clicks, region_dict, year_dict):
    if year_dict is None or region_dict is None:
        return html.Div()
    # Using children instead of value to avoid non existent attribute error
    region = region_dict['props']['value']
    year = year_dict['props']['value']
    url = base_url + '/data/'
    params = {'region': region, 'year': year}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        out = response.json()
        data = pd.DataFrame(json.loads(out))
        data.reset_index(inplace=True)
        cols = [i if 'DEMAND' not in i.upper() else i.split('_')[0]
            for i in data.columns]
        cols[0] = 'City'
        data.columns = cols
        out = dt.DataTable(
            id='api-data-table',
            columns=[{'name': i, 'id': i} for i in cols],
            data=data.to_dict('records'),
            sort_action='native',
            row_selectable='multi'
        )
    else:
        out = html.H1('Error: Invalid API call to "data".')

    return out

@app.callback(
    Output('optimization-response', 'children'),
    Input('opt-button', 'n_clicks'),
    [State('greenfield-data', 'children'),
     State('dc-loc-number', 'value'),
     State('distance-max-input', 'value'),
     State('capacity-max-input', 'value'),
     State('capacity-min-input', 'value'),
     State('iterations-input', 'value')]
)
def run_optimization(n_clicks, data, n_locs, dist_max, cap_max, cap_min, iters):
    out = html.Div()

    if n_clicks is not None:
        url = base_url + '/greenfield/'

        # Check for None or odd inputs
        dist_max = utils._check_max_input(dist_max)
        cap_max = utils._check_max_input(cap_max)
        cap_min = utils._check_min_input(cap_min)

        # Add errors in case of missing data or improper input
        msg = ''
        if dist_max is None:
            msg += 'Check your maximum distance input, should be a number or' 
            msg += ' "None" to remove constraint.\n'
        if cap_max is None:
            msg += 'Check your maximum capacity input, should be a number or' 
            msg += ' "None" to remove constraint.\n'
        if cap_min is None:
            msg += 'Check your minimum capacity input, should be a number or' 
            msg += ' "None" to remove constraint.\n'

        if data is None:
            msg += 'Get data before running optimization.'
        else:
            # Parse data table
            try:
                cust_data = data['props']['derived_viewport_data']
            except KeyError:
                return html.P('Check data inputs.')
            demand = [i['Demand'] for i in cust_data]
            lat = [i['Latitude'] for i in cust_data]
            lon = [i['Longitude'] for i in cust_data]

        if len(msg) > 0:
            return html.P('Error:\n' + msg)

        params = {
            'n_locs': int(n_locs),
            'iters': int(iters),
            'dist_max': dist_max,
            'cap_max': cap_max,
            'cap_min': cap_min,
            'demand': demand,
            'custLat': lat,
            'custLon': lon
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            msg = html.H1('Optimization Successful!')
            res = json.loads(response.json())
            # Plot best results
            best_iter = np.argmin([i['obj'] for i in res.values()])
            m = utils.plot_customer_assignment(res[f'iter_{best_iter}'])
            m.save("folium_map.html")
            out = html.Div([msg, 
                html.Iframe(srcDoc=open("folium_map.html", "r").read(),
                    height="100%", width="100%")])
        else:
            out = html.H1('Error: Invalid API Call')

    return out

