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
# top cards
######################################################################

@callback(
    Output("stats", "children"),
    Input("data-store", "data")
    )
def update_analytics_graph(df:pd.DataFrame):
    number_of_countries = df["country"].nunique()
    number_of_restaurants = df["Name"].nunique()
    number_of_stars = df["stars"].sum()
    population_per_restaurant = df["population"].sum() / number_of_restaurants
    population_per_star = df["population"].sum() / number_of_stars
    average_price_niveau = df["Price"].mean()

    cards = dmc.Flex([
            dmc.Card(
                children=[
                    dmc.Text("Number of Countries"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(number_of_countries, order=1)
                    ],
                className="stats-card"
                
                ),
            dmc.Card(
                children=[
                    dmc.Text("Number of Restaurants"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(number_of_restaurants, order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Text("Number of Stars"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(number_of_stars, order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Text("Population per Restaurant"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{population_per_restaurant:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Text("Population per Star"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{population_per_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Text("Average Price Niveau ($ - $$$$)"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{average_price_niveau:,.2f}", order=1)
                    ],
                className="stats-card"
                ),
            ],
            direction={"base": "column", "sm": "row"},
            gap={"base": "sm", "sm": "lg"},
            justify={"sm": "start"})
    return cards

######################################################################
# subplot
######################################################################

@callback(
    Output("graph-country", "children"),
    Input("data-store", "data"),
    Input("country-sort-by", "value")
    )
def update_analytics_graph(df:pd.DataFrame, sort_by:str):
    print(sort_by)
    df_country = (df.groupby(['country'])
                        .agg(
                            stars_sum=('stars', 'sum'),
                            restaurants_count=('Name', 'count'),
                            population=('population', 'first'),
                            )
                        .sort_values(sort_by, ascending=False)
                        .reset_index())

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.stars_sum,
            hovertemplate='<b>%{x}</b><br>Stars: %{y}',
            name='Sum of Stars',
        ), row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.restaurants_count,
            hovertemplate=f'<b>%{{x}}</b><br>Restaurants: %{{y}}',
            name=f'Sum of Restaurants',
            showlegend=True,
        ), row=2, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_country.country,
            y=df_country.population,
            hovertemplate=f'<b>%{{x}}</b><br>Population: %{{y}}',
            name=f'Population',
            showlegend=True,
        ), row=3, col=1
    )

    fig.update_layout(
        title_text="Stars and Restaurants per Country",
        title_x=0.5,
        height=800,
        # showlegend=False,
        barcornerradius=7,
        barmode='stack'
    )
    fig.update_xaxes(row=1, col=1, showticklabels=False)
    fig.update_xaxes(row=2, col=1, showticklabels=False)
    fig.update_xaxes(row=3, col=1, showticklabels=True)
    fig.update_yaxes(title_text="Number of Stars", row=1, col=1)
    fig.update_yaxes(title_text="Number of Restaurants", row=2, col=1)
    fig.update_yaxes(title_text="Population", row=3, col=1)

    graph = dcc.Graph(figure=fig, style={"width": "100%"})
    return graph


@callback(
    Output("graph-country-price", "children"),
    Input("data-store", "data")
    )
def update_analytics_graph(df:pd.DataFrame):
    df_grp = (df.groupby(['country'])
                        .agg(
                            price_mean=('Price', 'mean'),
                            restaurant_count=('Name', 'count'),
                            )
                        .sort_values('price_mean', ascending=False)
                        .reset_index())

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.4],
    )
    fig.add_trace(
        go.Box(
            x=df.country,
            y=df.Price,
            name='Price Niveau',
            boxmean=True,
        ), row=1, col=1
    )
    fig.add_trace(
        go.Bar(
            x=df_grp.country,
            y=df_grp.restaurant_count,
            hovertemplate='<b>%{x}</b><br>Restaurants: %{y}',
            name='Number of Restaurants',
        ), row=2, col=1
    )
    fig.update_layout(
        title_text="Price Range per Country",
        title_x=0.5,
        height=600,
        barcornerradius=7,
    )
    fig.update_xaxes(row=1, col=1, showticklabels=False, categoryorder='array', categoryarray=df_grp.country)
    fig.update_xaxes(row=2, col=1, showticklabels=True, categoryorder='array', categoryarray=df_grp.country)
    fig.update_yaxes(title_text="price niveau", row=1, col=1)
    fig.update_yaxes(title_text="restaurants", row=2, col=1)

    graph = dcc.Graph(figure=fig, style={"width": "100%"})
    return graph

######################################################################
# Layout
######################################################################

sort_options = [["stars_sum", "Stars"], ["restaurants_count", "Restaurants"], ["population", "Population"]]

layout = html.Div([
    html.Div(id="stats"),
    html.Div(
        [
            dmc.RadioGroup(
                children=dmc.Group([dmc.Radio(l, value=k) for k,l in sort_options], my=10),
                id="country-sort-by",
                value="stars_sum",
                label="Sort by",
                size="sm",
                mb=10,
            ),
            dmc.Text(id="radio-output"),
        ]
    ),
    dmc.Card(id="graph-country", className="analytics-card"),
    dmc.Card(id="graph-country-price", className="analytics-card"),
    ])
