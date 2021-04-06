import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# from pages import home, optimize
from app import app

# PAGES = ['/home', '/optimization']

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
        dbc.NavItem(dbc.NavLink("Home", href="/home")), 
        dbc.NavItem(dbc.NavLink("Optimization", href="/optimization"))
        ],
        vertical=True,
        pills=True,
    ),
    ],
    style=SIDEBAR_STYLE,
)

layout = html.Div([
    sidebar,
    dcc.Location(id='base-url', refresh=True),
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
    dbc.Row([
            html.H1('Optimization')]
        ),
        dbc.Row([
            html.Div(id='optimization-response')
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
# @app.callback(
#     [Output('home-display', 'style'),
#      Output('opt-display', 'style')],
#     Input('base-url', 'pathname')
# )
# def router(pathname):
#     output = []
#     for p in PAGES:
#         if pathname in p and pathname != '/':
#             output.append({'display': 'block'})
#         elif pathname == '/' and '/home' in pathname:
#             output.append({'display': 'block'})
#         else:
#             output.append({'display': 'none'})

#     return output

