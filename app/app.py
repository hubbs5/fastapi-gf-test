import dash
import dash_bootstrap_components as dbc
import dash_html_components as html

# Themes:
# CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, 
# LUMEN, LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, 
# SLATE, SOLAR, SPACELAB, SUPERHERO, UNITED, YETI

external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    prevent_initial_callbacks=False
)