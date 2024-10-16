from dash_iconify import DashIconify


DATA_PATH = "data/michelin_by_Jerry_Ng.csv"

def get_icon(icon):
    return DashIconify(icon=icon, height=16)