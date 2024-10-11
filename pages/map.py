import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash_extensions.enrich import (Input, Output, Serverside, callback, dcc,
                                    html, no_update)
from plotly.subplots import make_subplots

from modules.country_map import *
from modules.helpers import *

pio.templates.default = "plotly_white"
colors = px.colors.qualitative.Pastel
colors = [*colors * 100]

dash.register_page(
    __name__,
    path="/",
    name="Map")

######################################################################
# Map
######################################################################

@callback(
    Output("map-fig", "figure"),
    Input("data-store", "data")
    )
def update_map(df:pd.DataFrame):
    dfs_awards = [df for _,df in df.groupby('Award', sort=False)]
    fig = go.Figure()
    for tmp in dfs_awards:
        fig.add_trace(
            go.Scattermap(
                lat=tmp['Latitude'],
                lon=tmp['Longitude'],
                mode='markers',
                marker=dict(
                    size=tmp['award_size'],
                    opacity=0.8,
                    ),
                text=tmp['Name'],
                customdata=tmp['Award'],
                hoverinfo='text',
                hovertemplate='<b>%{text}</b><br>%{customdata}<br>%{lat}, %{lon}',
                showlegend=True,
                name=tmp['Award'].iloc[0],
                )
            )

    fig.update_layout(
        height=800,
        clickmode='event',
        map=dict(
            bearing=0,
            center=go.layout.map.Center(lat=48, lon=6),
            zoom=4
        ))
    return fig


@callback(
    Output("restaurant-description", "children"),
    Output("restaurant-description", "opened"),
    Input("data-store", "data"),
    Input("map-fig", "clickData"),
    )
def update_map(df:pd.DataFrame, click_data):
    if click_data is None:
        return no_update
    else:
        name = click_data['points'][0]['text']
        desc = df[df['Name'] == name]['Description'].iloc[0]
        children = [
            dmc.Text(name.title(), fw=700),
            dmc.Space(h=20),
            dmc.Text(desc),
        ]
        return children, True

######################################################################
# Layout
######################################################################

layout = html.Div([
    dmc.Card(dcc.Graph(style={"width": "100%"}, id="map-fig"), className="map-card"),
    dmc.Modal(id="restaurant-description"),
])
