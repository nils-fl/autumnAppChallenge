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
    path="/analytics_countries",
    name="Countries")

######################################################################
# subplot
######################################################################

@callback(
    Output("graph-country", "children"),
    Input("data-store", "data"),
    Input("country-sort-by", "value")
    )
def update_analytics_graph(df:pd.DataFrame, sort_by:str):
    df_country = (df.groupby(['country'])
                        .agg(
                            stars_3_sum=('Award', lambda x: len(x[x == "3 Stars"])),
                            stars_2_sum=('Award', lambda x: len(x[x == "2 Stars"])),
                            stars_1_sum=('Award', lambda x: len(x[x == "1 Star"])),
                            bib_sum=('Award', lambda x: len(x[x == "Bib Gourmand"])),
                            selected_sum=('Award', lambda x: len(x[x == "Selected Restaurants"])),
                            restaurants_count=('Name', 'count'),
                            population=('population', 'first'),
                            mean_price=('Price', 'mean')
                            )
                        .sort_values(sort_by, ascending=False)
                        .reset_index())

    fig = make_subplots(
        rows=8,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=[
            "3 Stars",
            "2 Stars",
            "1 Star",
            "Bib Gourmand",
            "Selected Restaurant",
            "Sum of Restaurants",
            "Price",
            "Population",
        ]
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.stars_3_sum,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='3 Stars',
        ), row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.stars_2_sum,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='2 Stars',
        ), row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.stars_1_sum,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='1 Stars',
        ), row=3, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.bib_sum,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='Bib Gourmand',
        ), row=4, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.selected_sum,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='Selected Restaurant',
        ), row=5, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.restaurants_count,
            hovertemplate=f'<b>%{{x}}</b><br>Restaurants: %{{y}}',
            name=f'Sum of Restaurants',
            showlegend=True,
        ), row=6, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.mean_price,
            hovertemplate=f'<b>%{{x}}</b><br>Price Niveau: %{{y}}',
            name=f'Mean Price',
            showlegend=True,
        ), row=7, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.population,
            hovertemplate=f'<b>%{{x}}</b><br>Population: %{{y}}',
            name=f'Population',
            showlegend=True,
        ), row=8, col=1
    )

    fig.update_layout(
        title_text="Stars and Restaurants per Country",
        title_x=0.5,
        height=8*200,
        showlegend=False,
        barcornerradius=7,
        barmode='stack'
    )
    fig.update_xaxes(row=1, col=1, showticklabels=False)
    fig.update_xaxes(row=2, col=1, showticklabels=False)
    fig.update_xaxes(row=3, col=1, showticklabels=False)
    fig.update_xaxes(row=4, col=1, showticklabels=False)
    fig.update_xaxes(row=5, col=1, showticklabels=False)
    fig.update_xaxes(row=6, col=1, showticklabels=False)
    fig.update_xaxes(row=7, col=1, showticklabels=False)
    fig.update_xaxes(row=8, col=1, showticklabels=True)
    fig.update_yaxes(title_text="Restaurants", row=1, col=1)
    fig.update_yaxes(title_text="Restaurants", row=2, col=1)
    fig.update_yaxes(title_text="Restaurants", row=3, col=1)
    fig.update_yaxes(title_text="Restaurants", row=4, col=1)
    fig.update_yaxes(title_text="Restaurants", row=5, col=1)
    fig.update_yaxes(title_text="Restaurants", row=6, col=1)
    fig.update_yaxes(title_text="Mean Price Niveau", row=7, col=1)
    fig.update_yaxes(title_text="Population", row=8, col=1)

    graph = dcc.Graph(figure=fig, style={"width": "100%"})
    return graph


######################################################################
# Layout
######################################################################

sort_options = [["stars_3_sum", "Stars"], ["restaurants_count", "Restaurants"], ["population", "Population"]]

layout = html.Div([
    html.Div(
        [
            dmc.Space(h=10),
            dmc.RadioGroup(
                children=dmc.Group([dmc.Radio(l, value=k) for k,l in sort_options], my=10),
                id="country-sort-by",
                value="stars_3_sum",
                label="Sort by",
                size="sm",
                mb=10,
            ),
            dmc.Space(h=10),
            dmc.Text(id="radio-output"),
        ]
    ),
    dmc.Card(id="graph-country", className="analytics-card"),
    ])
