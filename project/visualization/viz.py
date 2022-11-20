import os

from download import download
import pandas as pd
import plotly.express as px
import json
from dash import Dash, dcc, html, Input, Output


# Downloading data
url = 'https://data.enedis.fr/explore/dataset/consommation-annuelle-residentielle-par-adresse/download'
data_path = os.path.join(os.getcwd(), 'data_viz.csv')
path = download(url, data_path, progressbar=True, verbose=True)

# Dataframe creation, keeping only useful columns
df = pd.read_csv(data_path, sep=";", usecols=[0, 7, 8, 13])

# Dropping duplicates, renaming for convenience
df.drop_duplicates(inplace=True)
df = df.rename(columns={"code_commune": "code", "nom_commune": "nom",
                        "consommation_annuelle_moyenne_de_la_commune_mwh": "conso"})


# TODO fix path names with os
city = '../../data/communes.geojson'
dept = '../../data/departements.geojson'
region = '../../data/regions.geojson'

cities = json.load(open(city, 'r'))

# Plots
# TODO Violin plot per year per city

# Interactive map
# TODO define a class to get max min per region, dept

# App layout
app = Dash(__name__)

app.layout = html.Div([

    html.H1("French electricity consumption", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "2018", "value": 2018},
                     {"label": "2019", "value": 2019},
                     {"label": "2020", "value": 2020},
                     {"label": "2021", "value": 2021}],
                 multi=False,
                 value=2018,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='elec_map', figure={})

])
# Connect plotly to Dash
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='elec_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen by the user was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["annee"] == option_slctd]

    # Map not showing anything at >=474, memory/cache problem?
    n = 473
    fig = px.choropleth_mapbox(dff.head(n),
                               geojson=cities,
                               color="conso",
                               locations="code",
                               featureidkey="properties.code",
                               mapbox_style="carto-positron",
                               hover_data=['conso'],
                               zoom=3.7,
                               center={"lat": 47, "lon": 2},
                               opacity=0.6,
                               )

    return container, fig


if __name__ == '__main__':
    app.run_server(debug=True)
