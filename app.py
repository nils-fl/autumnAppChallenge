import dash_mantine_components as dmc
import pandas as pd
from dash import _dash_renderer
from dash_extensions.enrich import (DashProxy, Input, Output, Serverside,
                                    ServersideOutputTransform, dcc, html,
                                    page_container)

from modules.country_map import *
from modules.helpers import *

_dash_renderer._set_react_version("18.2.0")

app = DashProxy(
    __name__,
    update_title="Autumn App Challenge",
    use_pages=True,
    external_stylesheets=dmc.styles.ALL,
    transforms=[ServersideOutputTransform()]
    )

app.config.suppress_callback_exceptions = True
server = app.server

def get_nav_content():
    return [
        dmc.Image(
            src="https://upload.wikimedia.org/wikipedia/commons/a/ad/MichelinStar.svg",
            className="brand-icon",
        ),
        dmc.NavLink(
            href="/",
            leftSection=get_icon("mdi:map"),
            label="Map",
        ),
        dmc.NavLink(
            href="/analytics_countries",
            leftSection=get_icon("mdi:analytics"),
            label="Countries",
        ),
        dmc.NavLink(
            href="/analytics_cuisines",
            leftSection=get_icon("mdi:analytics"),
            label="Cuisines",
        ),
    ]

def size_mapping(award):
    if award == '3 Stars':
        return 25
    elif award == '2 Stars':
        return 20
    elif award == '1 Star':
        return 15
    elif award == 'Bib Gourmand':
        return 7
    else:
        return 5


def get_stars(award):
    if award == '3 Stars':
        return 3
    elif award == '2 Stars':
        return 2
    elif award == '1 Star':
        return 1
    else:
        return 0


@app.callback(
    Output("data-store", "data"),
    Input("url", "search"),
    )
def display_page(url):
    df = pd.read_csv(DATA_PATH)
    df['award_size'] = df['Award'].apply(size_mapping)
    df["country"] = df.Location.apply(lambda x: x.split(",")[-1].strip())
    df["country"] = df.country.map(country_name_map)
    df["city"] = df.Location.apply(lambda x: x.split(",")[0].strip())
    df["stars"] = df.Award.apply(lambda x: get_stars(x))
    df["country_codes"] = df.country.map(country_code_map)
    df["population"] = df.country_codes.map(country_population_map)
    df.Price = df.Price.astype(str).apply(lambda x: len(x) if x != "nan" else 0)
    return Serverside(df)


app.layout = dmc.MantineProvider(
    id="m2d-mantine-provider",
    forceColorScheme="light",
    children=[
        dcc.Location(id="url", refresh="callback-nav"),
        dmc.AppShell(
            children=[
                dmc.AppShellNavbar(get_nav_content(), zIndex=2000, w="12em", className="nav-left"),
                dmc.AppShellMain(children=page_container),
                dcc.Store(id="data-store"),
            ]
        ),
    ])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8071, debug=False, use_reloader=True)
