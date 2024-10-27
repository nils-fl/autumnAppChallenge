import os

import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash_extensions.enrich import (Input, Output, Serverside, callback, dcc,
                                    html, no_update, clientside_callback)
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
    number_of_restaurants = len(df)
    number_1_star = df[df['Award'] == '1 Star'].shape[0]
    number_2_star = df[df['Award'] == '2 Stars'].shape[0]
    number_3_star = df[df['Award'] == '3 Stars'].shape[0]

    cards = dmc.Flex([
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
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
                                h=30,
                            ),
                            dmc.Space(w=5),
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
                                h=30,
                            ),
                            dmc.Space(w=5),
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
                                h=30,
                            ),
                        ])
                    ),
                    dmc.Text("Restaurants"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_3_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
                                h=30,
                            ),
                            dmc.Space(w=5),
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
                                h=30,
                            ),
                        ])
                    ),
                    dmc.Text("Restaurants"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_2_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            dmc.Card(
                children=[
                    dmc.Center(
                        dmc.Flex([
                            dmc.Image(
                                src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
                                h=30,
                            ),
                        ])
                    ),
                    dmc.Text("Restaurants"),
                    html.Hr(className="stats-card-hr"),
                    dmc.Title(f"{number_1_star:,.0f}", order=1)
                    ],
                className="stats-card"
                ),
            ],
            direction={"base": "column", "md": "row"},
            align="center",
            gap="md",
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
        features = df[df['Name'] == name]['FacilitiesAndServices'].iloc[0].split(",") if len(df[df['Name'] == name]['FacilitiesAndServices'].iloc[0]) > 2 else []

        children = [
            dmc.Card(
                children=[
                    dmc.CardSection([
                        dmc.Center(DashIconify(icon="mdi:silverware", height=50)),
                        dmc.Space(h=20),
                        dmc.Center(dmc.Text(name.title(), fw=700))
                        ], h=60
                    ),
                    dmc.Space(h=40),
                    html.Hr(),
                    dmc.Flex([
                        dmc.Badge(f"{df[df['Name'] == name]['Award'].iloc[0]}", color="red")
                    ],
                    justify={"sm": "center"},
                    wrap="wrap"),
                    dmc.Space(h=20),
                    dmc.Text(desc),
                    dmc.Space(h=20),
                    html.Hr(),
                    dmc.Flex([
                        dmc.Badge(f, color="green") for f in features
                    ],
                    direction={"base": "column", "sm": "row"},
                    gap={"base": "sm", "sm": "lg"},
                    justify={"sm": "center"},
                    wrap="wrap"
                    ),
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

def get_alt_entry(row, i):
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
            dmc.Group([
                dcc.Link(dmc.Button("Get me there"), href=f"http://maps.google.com/maps?z=10&q={row['Latitude']},{row['Longitude']}", target="_blank"),
                dmc.Button("for the way", id=f"for-the-way-btn-{str(i)}", leftSection=DashIconify(icon="mdi:music", height=20), color="green"),
                html.P(children=row["Name"], id=f"for-the-way-name-{str(i)}", hidden=True, n_clicks=0),
                html.P(children=row["city"], id=f"for-the-way-city-{str(i)}", hidden=True, n_clicks=0),
            ])
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
        df["distance"] = df.apply(lambda x: distance.great_circle((lat, long), (x['Latitude'], x['Longitude'])).km, axis=1)
        df = df.sort_values("distance")[:5].reset_index(drop=True)
        
        children = [
            dmc.Text(f"Alternatives to {name.title()}", fw=700),
            dmc.Space(h=20),
            html.Hr(),
            dmc.Space(h=20),
            *[get_alt_entry(row, i) for i,row in df.iterrows()],
        ]
        return True, children
    else:
        return False, no_update

######################################################################
# Music Modal
######################################################################

def get_music_children(name, city):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": (f"Please recommend 3 songs that would be great to listen on my trip to {city}"
                            f" where I will eat at the restaurant named {name}."
                            f" Please return the recommendation as markdown."),
            }
        ],
        model="llama3-8b-8192",
    )
    recommendation = chat_completion.choices[0].message.content
    children = [
        dmc.Text(f"Songs for my trip to {name.title()}", fw=700),
        dmc.Space(h=20),
        html.Hr(),
        dmc.Space(h=20),
        dcc.Markdown(recommendation),
        dmc.Space(h=20),
    ]
    return children


@callback(
    Output("for-the-way-modal", "children"),
    Output("for-the-way-modal", "opened"),
    Input("for-the-way-btn-0", "n_clicks"),
    Input("for-the-way-btn-1", "n_clicks"),
    Input("for-the-way-btn-2", "n_clicks"),
    Input("for-the-way-btn-3", "n_clicks"),
    Input("for-the-way-btn-4", "n_clicks"),
    Input("for-the-way-name-0", "children"),
    Input("for-the-way-name-1", "children"),
    Input("for-the-way-name-2", "children"),
    Input("for-the-way-name-3", "children"),
    Input("for-the-way-name-4", "children"),
    Input("for-the-way-city-0", "children"),
    Input("for-the-way-city-1", "children"),
    Input("for-the-way-city-2", "children"),
    Input("for-the-way-city-3", "children"),
    Input("for-the-way-city-4", "children"),
    prevent_initial_call=True,
    )
def update_map(n_clicks_0, n_clicks_1, n_clicks_2, n_clicks_3, n_clicks_4, name_0, name_1, name_2, name_3, name_4, city_0, city_1, city_2, city_3, city_4):
    if n_clicks_0 and n_clicks_0 > 0:
        children = get_music_children(name_0, city_0)
        return children, True
    elif n_clicks_1 and n_clicks_1 > 0:
        children = get_music_children(name_1, city_1)
        return children, True
    elif n_clicks_2 and n_clicks_2 > 0:
        children = get_music_children(name_2, city_2)
        return children, True
    elif n_clicks_3 and n_clicks_3 > 0:
        children = get_music_children(name_3, city_3)
        return children, True
    elif n_clicks_4 and n_clicks_4 > 0:
        children = get_music_children(name_4, city_4)
        return children, True
    else:
        return no_update, False

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
    html.Div(id="stats"),
    dmc.Space(h=20),
    dmc.Card([dcc.Graph(style={"width": "100%"}, id="map-fig")], className="map-card"),
    dmc.Modal(
        id="restaurant-description",
        size="lg",
        ),
    dmc.Modal(
        id="for-the-way-modal",
        size="lg",
        zIndex=2000,
        ),
    dcc.Store(id="click-data"),
])
