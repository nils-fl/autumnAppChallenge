import os

import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash_extensions.enrich import (Input, Output, Serverside, callback, dcc,
                                    html, no_update)
from dotenv import load_dotenv
from geopy import distance
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from groq import Groq

from modules.country_map import *
from modules.helpers import *

load_dotenv()

pio.templates.default = "plotly_white"
colors = px.colors.qualitative.Pastel
colors = [*colors * 100]

dash.register_page(
    __name__,
    path="/",
    name="Map")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

geolocator = Nominatim(user_agent="dash_challenge")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

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
    number_1_star = df[df['Award'] == '1 Star'].shape[0]
    number_2_star = df[df['Award'] == '2 Stars'].shape[0]
    number_3_star = df[df['Award'] == '3 Stars'].shape[0]

    cards = dmc.Stack([
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            DashIconify(icon="mdi:map", height=30),
                        ])
                    ),
                    dmc.Text("Countries"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_of_countries:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            DashIconify(icon="mdi:storefront-outline", height=30),
                        ])
                    ),
                    dmc.Text("Restaurants"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_of_restaurants:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            DashIconify(icon="mdi:star", height=30),
                            DashIconify(icon="mdi:star", height=30),
                            DashIconify(icon="mdi:star", height=30),
                        ])
                    ),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_3_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            DashIconify(icon="mdi:star", height=30),
                            DashIconify(icon="mdi:star", height=30),
                        ])
                    ),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_2_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            DashIconify(icon="mdi:star", height=30),
                        ])
                    ),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_1_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            ],
            align="center",
            gap="xl",
            justify="space-between")
    return cards

######################################################################
# Map
######################################################################

@callback(
    Output("map-fig", "figure"),
    Input("data-store", "data"),
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

######################################################################
# Modal
######################################################################

@callback(
    Output("restaurant-description", "children"),
    Output("restaurant-description", "opened"),
    Output("click-data", "data"),
    Input("data-store", "data"),
    Input("map-fig", "clickData"),
    )
def update_map(df:pd.DataFrame, click_data):
    if click_data is None:
        return no_update
    else:
        name = click_data['points'][0]['text']
        desc = df[df['Name'] == name]['Description'].iloc[0]
        city = df[df['Name'] == name]['city'].iloc[0]
        url = df[df['Name'] == name]['Url'].iloc[0]
        restaurant_url = df[df['Name'] == name]['WebsiteUrl'].iloc[0]

        children = [
            dmc.Card(
                children=[
                    dmc.CardSection([
                        dmc.Center(DashIconify(icon="mdi:silverware", height=50)),
                        dmc.Space(h=20),
                        dmc.Center(dmc.Text(name.title(), fw=700))
                        ], h=60
                    ),
                    dmc.Space(h=20),
                    html.Hr(),
                    dmc.Space(h=20),
                    dmc.Text(desc),
                    dmc.Space(h=20),
                    html.Hr(),
                    dmc.Space(h=20),
                    dmc.Stack([
                        dmc.Flex([
                            dcc.Link(dmc.Button("Website"), href=restaurant_url, target="_blank"),
                            dcc.Link(dmc.Button("Google"), href=f"https://www.google.com/search?q={name}+restaurant+{city}", target="_blank"),
                            dcc.Link(dmc.Button("Guide"), href=url, target="_blank"),
                            ],
                            direction={"base": "column", "sm": "row"},
                            gap={"base": "sm", "sm": "lg"},
                            justify={"sm": "center"}
                            ),
                        dmc.Flex([
                            dmc.Button("Plan My Day", id="plan-my-day-btn", n_clicks=0),
                            dmc.Button("Alternatives", id="alternatives-btn", n_clicks=0),
                        ],
                        direction={"base": "column", "sm": "row"},
                        gap={"base": "sm", "sm": "lg"},
                        justify={"sm": "center"}
                        )
                    ])
                ]
            )
        ]
        return children, True, Serverside([name, city])

######################################################################
# Drawer Day Plan
######################################################################

@callback(
    Output("plan-my-day-drawer", "opened"),
    Output("plan-my-day-drawer", "children"),
    Input("plan-my-day-btn", "n_clicks"),
    Input("click-data", "data"),
    prevent_initial_call=True,
    )
def update_map(n_clicks, click_data):
    if n_clicks>0:
        name = click_data[0]
        city = click_data[1]
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Please create a short day plan of a visit in {city} where I will eat at the restaurant named {name}.",
                }
            ],
            model="llama3-8b-8192",
        )
        day_plan = chat_completion.choices[0].message.content
        children = [
            dmc.Text(f"My day at {name.title()}", fw=700),
            dmc.Space(h=20),
            html.Hr(),
            dmc.Space(h=20),
            dcc.Markdown(day_plan),
            dmc.Space(h=20),
        ]
        return True, children
    else:
        return False, no_update

######################################################################
# Drawer Alternatives
######################################################################

def get_alt_entry(row):
    entry = dmc.Card(
        children=[
            dmc.Group([
                dmc.Text(row["Name"], fw=700),
                dmc.Badge(f"{row['distance']:,.0f} km", color="blue"),
                dmc.Badge(row['Price']*"$", color="green"),
                dmc.Badge(row['Award'], color="red"),
            ]),
            dmc.Text(f" in {row['city']}, {row['country']}", fw=300),
            dmc.Space(h=10),
            dcc.Link(dmc.Button("Get me there"), href=f"http://maps.google.com/maps?z=10&q={row['Latitude']},{row['Longitude']}", target="_blank"),
        ], className="alt-card")
    return entry

@callback(
    Output("alternatives-drawer", "opened"),
    Output("alternatives-drawer", "children"),
    Input("alternatives-btn", "n_clicks"),
    Input("click-data", "data"),
    Input("data-store", "data"),
    prevent_initial_call=True,
    )
def update_map(n_clicks, click_data, df:pd.DataFrame):
    if n_clicks>0:
        name = click_data[0]
        long = df[df['Name'] == name]['Longitude'].iloc[0]
        lat = df[df['Name'] == name]['Latitude'].iloc[0]
        
        df = df[df.Name!=name].copy()
        df["distance"] = df.apply(lambda x: distance.distance((lat, long), (x['Latitude'], x['Longitude'])).km, axis=1)
        df = df.sort_values("distance")[:5]
        
        children = [
            dmc.Text(f"Alternatives to {name.title()}", fw=700),
            dmc.Space(h=20),
            html.Hr(),
            dmc.Space(h=20),
            *[get_alt_entry(row) for i,row in df.iterrows()],
        ]
        return True, children
    else:
        return False, no_update

######################################################################
# Layout
######################################################################

layout = html.Div([
    dmc.Drawer(
            id="plan-my-day-drawer",
            radius="10px",
            zIndex=1000,
            position="left",
            size="lg",
        ),
    dmc.Drawer(
            id="alternatives-drawer",
            radius="10px",
            zIndex=1000,
            position="left",
            size="lg",
        ),
    dmc.Grid(children=[
        dmc.GridCol(dmc.Card([dcc.Graph(style={"width": "100%"}, id="map-fig")], className="map-card"), span=10, miw=400),
        dmc.GridCol(html.Div(id="stats"), span=2, miw=200),
        ],
        gutter="md"),
    dmc.Modal(
        id="restaurant-description",
        size="lg",
        ),
    dcc.Store(id="click-data"),
])
