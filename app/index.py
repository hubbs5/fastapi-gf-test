import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from pages import home, optimize
from app import app

PAGES = ['/home', '/optimization']

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
    dbc.Container(
        html.Div(home.layout,
            id='home-display',
            style={'display': 'none'})
    ),
    dbc.Container(
        html.Div(optimize.layout,
            id='opt-display',
            style={'display': 'none'})
    )
])

@app.callback(
    [Output('home-display', 'style'),
     Output('opt-display', 'style')],
    Input('base-url', 'pathname')
)
def router(pathname):
    output = []
    for p in PAGES:
        if pathname in p and pathname != '/':
            output.append({'display': 'block'})
        elif pathname == '/' and '/home' in pathname:
            output.append({'display': 'block'})
        else:
            output.append({'display': 'none'})

    return output

