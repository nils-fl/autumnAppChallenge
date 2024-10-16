import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash_extensions.enrich import (Input, Output, Serverside, callback, dash,
                                    dcc, html, no_update)
from plotly.subplots import make_subplots

from modules.country_map import *
from modules.helpers import *

pio.templates.default = "plotly_white"
colors = px.colors.qualitative.Pastel
colors = [*colors * 100]

dash.register_page(
    __name__,
    path="/analytics_cuisines",
    name="Cousines")

######################################################################
# subplot
######################################################################

@callback(
    Output("graph-cuisines", "children"),
    Input("data-store", "data"),
    )
def update_analytics_graph(df:pd.DataFrame):
    most_frequent_words_3star = df[df.Award == "3 Stars"].Cuisine.str.lower().str.replace("cuisine", "").str.split(",").explode().str.strip().str.split(" ").explode().value_counts()
    most_frequent_words_2star = df[df.Award == "2 Stars"].Cuisine.str.lower().str.replace("cuisine", "").str.split(",").explode().str.strip().str.split(" ").explode().value_counts()
    most_frequent_words_1star = df[df.Award == "1 Star"].Cuisine.str.lower().str.replace("cuisine", "").str.split(",").explode().str.strip().str.split(" ").explode().value_counts()
    most_frequent_words_bib = df[df.Award == "Bib Gourmand"].Cuisine.str.lower().str.replace("cuisine", "").str.split(",").explode().str.strip().str.split(" ").explode().value_counts()
    most_frequent_words_selected = df[df.Award == "Selected Restaurants"].Cuisine.str.lower().str.replace("cuisine", "").str.split(",").explode().str.strip().str.split(" ").explode().value_counts()
    most_frequent_words_all = df.Cuisine.str.lower().str.replace("cuisine", "").str.split(",").explode().str.strip().str.split(" ").explode().value_counts()

    fig = make_subplots(
        rows=6,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[
            "3 Stars",
            "2 Stars",
            "1 Star",
            "Bib Gourmand",
            "Selected Restaurant",
            "All Restaurants",
        ]
    )
    fig.add_trace(
        go.Bar(
            x=most_frequent_words_3star.index,
            y=most_frequent_words_3star.values,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='3 Stars',
        ), row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=most_frequent_words_2star.index,
            y=most_frequent_words_2star.values,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='2 Stars',
        ), row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=most_frequent_words_1star.index,
            y=most_frequent_words_1star.values,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='1 Stars',
        ), row=3, col=1
    )
    fig.add_trace(
        go.Bar(
            x=most_frequent_words_bib.index,
            y=most_frequent_words_bib.values,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='Bib Gourmand',
        ), row=4, col=1
    )
    fig.add_trace(
        go.Bar(
            x=most_frequent_words_selected.index,
            y=most_frequent_words_selected.values,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='Selected Restaurants',
        ), row=5, col=1
    )
    fig.add_trace(
        go.Bar(
            x=most_frequent_words_all.index,
            y=most_frequent_words_all.values,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='All Restaurants',
        ), row=6, col=1
    )

    fig.update_layout(
        title_text="Words used to describe Cuisines",
        title_x=0.5,
        height=6*200,
        barcornerradius=7,
        showlegend=False,
    )
    fig.update_xaxes(row=1, col=1, showticklabels=False, range=[-1, 51])
    fig.update_xaxes(row=2, col=1, showticklabels=False, range=[-1, 51])
    fig.update_xaxes(row=3, col=1, showticklabels=False, range=[-1, 51])
    fig.update_xaxes(row=4, col=1, showticklabels=False, range=[-1, 51])
    fig.update_xaxes(row=5, col=1, showticklabels=False, range=[-1, 51])
    fig.update_xaxes(row=6, col=1, showticklabels=True, range=[-1, 51])
    fig.update_yaxes(title_text="count", row=1, col=1)
    fig.update_yaxes(title_text="count", row=2, col=1)
    fig.update_yaxes(title_text="count", row=3, col=1)
    fig.update_yaxes(title_text="count", row=4, col=1)
    fig.update_yaxes(title_text="count", row=5, col=1)
    fig.update_yaxes(title_text="count", row=6, col=1)

    graph = dcc.Graph(figure=fig, style={"width": "100%"})
    return graph


######################################################################
# Layout
######################################################################

layout = html.Div([
    dmc.Card(id="graph-cuisines", className="analytics-card"),
    ])
