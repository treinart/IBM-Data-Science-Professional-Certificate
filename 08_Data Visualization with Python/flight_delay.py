# Open this in your browser:
# http://127.0.0.1:8050/

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

airline_data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv",
    encoding="ISO-8859-1",
    dtype={
        "Div1Airport": str,
        "Div1TailNum": str,
        "Div2Airport": str,
        "Div2TailNum": str,
    },
)

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            "Flight Delay Time Statistics",
            style={"textAlign": "center", "color": "#503D36", "font-size": 30},
        ),
        html.Div(
            [
                "Input Year: ",
                dcc.Input(
                    id="input-year",
                    value="2010",
                    type="number",
                    style={"height": "35px", "font-size": 30},
                ),
            ],
            style={"font-size": 30},
        ),
        html.Br(),
        html.Br(),
        html.Div(
            [
                html.Div(dcc.Graph(id="carrier-plot")),
                html.Div(dcc.Graph(id="weather-plot")),
            ],
            style={"display": "flex"},
        ),
        html.Div(
            [
                html.Div(dcc.Graph(id="nas-plot")),
                html.Div(dcc.Graph(id="security-plot")),
            ],
            style={"display": "flex"},
        ),
        html.Div(dcc.Graph(id="late-plot"), style={"width": "65%"}),
    ]
)


def compute_info(airline_data, entered_year):
    df = airline_data[airline_data["Year"] == int(entered_year)]

    avg_car = df.groupby(["Month", "Reporting_Airline"])["CarrierDelay"].mean().reset_index()
    avg_weather = df.groupby(["Month", "Reporting_Airline"])["WeatherDelay"].mean().reset_index()
    avg_nas = df.groupby(["Month", "Reporting_Airline"])["NASDelay"].mean().reset_index()
    avg_sec = df.groupby(["Month", "Reporting_Airline"])["SecurityDelay"].mean().reset_index()
    avg_late = df.groupby(["Month", "Reporting_Airline"])["LateAircraftDelay"].mean().reset_index()

    return avg_car, avg_weather, avg_nas, avg_sec, avg_late


@app.callback(
    [
        Output("carrier-plot", "figure"),
        Output("weather-plot", "figure"),
        Output("nas-plot", "figure"),
        Output("security-plot", "figure"),
        Output("late-plot", "figure"),
    ],
    Input("input-year", "value"),
)
def get_graph(entered_year):
    avg_car, avg_weather, avg_nas, avg_sec, avg_late = compute_info(
        airline_data, entered_year
    )

    carrier_fig = px.line(
        avg_car,
        x="Month",
        y="CarrierDelay",
        color="Reporting_Airline",
        title="Average carrier delay time (minutes) by airline",
    )
    weather_fig = px.line(
        avg_weather,
        x="Month",
        y="WeatherDelay",
        color="Reporting_Airline",
        title="Average weather delay time (minutes) by airline",
    )
    nas_fig = px.line(
        avg_nas,
        x="Month",
        y="NASDelay",
        color="Reporting_Airline",
        title="Average NAS delay time (minutes) by airline",
    )
    sec_fig = px.line(
        avg_sec,
        x="Month",
        y="SecurityDelay",
        color="Reporting_Airline",
        title="Average security delay time (minutes) by airline",
    )
    late_fig = px.line(
        avg_late,
        x="Month",
        y="LateAircraftDelay",
        color="Reporting_Airline",
        title="Average late aircraft delay time (minutes) by airline",
    )

    return [carrier_fig, weather_fig, nas_fig, sec_fig, late_fig]


if __name__ == "__main__":
    app.run()