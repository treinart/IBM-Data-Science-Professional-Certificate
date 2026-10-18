"""Interactive SpaceX launch dashboard for the IBM capstone lab.

Run from any directory with:
    python spacex-dash-app.py

The application loads ``spacex_launch_dash.csv`` from this script's folder,
so it does not depend on the terminal's current working directory.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html


APP_TITLE: Final[str] = "SpaceX Launch Dashboard"
ALL_SITES: Final[str] = "ALL"
DATA_PATH: Final[Path] = Path(__file__).with_name("spacex_launch_dash.csv")
REQUIRED_COLUMNS: Final[set[str]] = {
    "Launch Site",
    "class",
    "Payload Mass (kg)",
    "Booster Version Category",
}
OUTCOME_LABELS: Final[dict[int, str]] = {0: "Failure", 1: "Success"}
OUTCOME_COLORS: Final[dict[str, str]] = {
    "Failure": "#c0392b",
    "Success": "#1f8f4e",
}


def load_launch_data(data_path: Path) -> pd.DataFrame:
    """Load and validate the course dataset used by the dashboard."""
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Course dataset not found: {data_path}. "
            "Save spacex_launch_dash.csv in the same folder as this script."
        )

    dataframe = pd.read_csv(data_path)
    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(
            "The CSV is missing required column(s): "
            + ", ".join(sorted(missing_columns))
        )

    if dataframe.loc[:, list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("The CSV contains missing values in required dashboard columns.")

    dataframe = dataframe.copy()
    dataframe["class"] = pd.to_numeric(dataframe["class"], errors="raise").astype(int)
    dataframe["Payload Mass (kg)"] = pd.to_numeric(
        dataframe["Payload Mass (kg)"], errors="raise"
    )

    invalid_outcomes = set(dataframe["class"].unique()).difference(OUTCOME_LABELS)
    if invalid_outcomes:
        raise ValueError(
            "The class column must contain only 0 (failure) and 1 (success). "
            f"Found: {sorted(invalid_outcomes)}"
        )

    return dataframe


spacex_df = load_launch_data(DATA_PATH)
launch_sites = sorted(spacex_df["Launch Site"].unique())
booster_categories = sorted(spacex_df["Booster Version Category"].unique())


def filter_launches(entered_site: str | None, payload_range: list[float] | tuple[float, float]) -> pd.DataFrame:
    """Return launches that match the selected site and inclusive payload range."""
    lower_payload, upper_payload = sorted(float(value) for value in payload_range)
    filtered = spacex_df.loc[
        spacex_df["Payload Mass (kg)"].between(lower_payload, upper_payload, inclusive="both")
    ]

    if entered_site and entered_site != ALL_SITES:
        filtered = filtered.loc[filtered["Launch Site"] == entered_site]

    return filtered.copy()


def style_figure(figure, title: str):
    """Apply a consistent, readable visual style to all course charts."""
    figure.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        margin={"l": 50, "r": 30, "t": 70, "b": 50},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return figure


def build_all_sites_pie() -> object:
    """Build the required success-launch pie chart when all sites are selected."""
    successes_by_site = (
        spacex_df.groupby("Launch Site", as_index=False)["class"]
        .sum()
        .rename(columns={"class": "Successful Launches"})
    )
    figure = px.pie(
        successes_by_site,
        values="Successful Launches",
        names="Launch Site",
        title="Total Successful Launches by Site",
        color="Launch Site",
    )
    figure.update_layout(legend_title_text="Launch Site")
    return style_figure(figure, "Total Successful Launches by Site")


def build_selected_site_pie(entered_site: str) -> object:
    """Build the required success-versus-failure pie chart for one launch site."""
    selected_site_data = spacex_df.loc[spacex_df["Launch Site"] == entered_site]
    outcomes = (
        selected_site_data["class"]
        .map(OUTCOME_LABELS)
        .value_counts()
        .reindex(["Success", "Failure"], fill_value=0)
        .rename_axis("Outcome")
        .reset_index(name="Launches")
    )
    figure = px.pie(
        outcomes,
        values="Launches",
        names="Outcome",
        title=f"Launch Outcomes for {entered_site}",
        color="Outcome",
        color_discrete_map=OUTCOME_COLORS,
    )
    figure.update_layout(legend_title_text="Launch Outcome")
    return style_figure(figure, f"Launch Outcomes for {entered_site}")


app = Dash(__name__, title=APP_TITLE)
server = app.server

app.layout = html.Main(
    [
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "marginBottom": "0.25rem"},
        ),
        html.P(
            "Explore launch outcomes by launch site, payload mass, and booster category.",
            style={"textAlign": "center", "color": "#4a5568", "marginTop": "0"},
        ),
        html.Section(
            [
                html.Label("Launch site", htmlFor="site-dropdown"),
                dcc.Dropdown(
                    id="site-dropdown",
                    options=[{"label": "All Sites", "value": ALL_SITES}]
                    + [{"label": site, "value": site} for site in launch_sites],
                    value=ALL_SITES,
                    placeholder="Select a launch site",
                    searchable=True,
                    clearable=False,
                ),
            ],
            style={"maxWidth": "900px", "margin": "1.5rem auto"},
        ),
        dcc.Graph(id="success-pie-chart"),
        html.Section(
            [
                html.Label("Payload mass range (kg)", htmlFor="payload-slider"),
                dcc.RangeSlider(
                    id="payload-slider",
                    min=0,
                    max=10000,
                    step=1000,
                    value=[0, 10000],
                    marks={value: f"{value:,}" for value in range(0, 10001, 1000)},
                    allowCross=False,
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ],
            style={"maxWidth": "900px", "margin": "2rem auto 1rem"},
        ),
        dcc.Graph(id="success-payload-scatter-chart"),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "1.5rem",
        "fontFamily": "Arial, sans-serif",
    },
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def update_pie_chart(entered_site: str | None):
    """Render success totals by site or outcomes for the selected site."""
    if entered_site in (None, ALL_SITES):
        return build_all_sites_pie()
    return build_selected_site_pie(entered_site)


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
    Input(component_id="payload-slider", component_property="value"),
)
def update_scatter_chart(
    entered_site: str | None, payload_range: list[float] | tuple[float, float]
):
    """Render the required payload, outcome, and booster-category scatter chart."""
    filtered_data = filter_launches(entered_site, payload_range)
    site_label = "All Sites" if entered_site in (None, ALL_SITES) else entered_site

    figure = px.scatter(
        filtered_data,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        category_orders={"Booster Version Category": booster_categories},
        hover_data={"Launch Site": True, "Booster Version": True, "class": False},
        labels={
            "Payload Mass (kg)": "Payload Mass (kg)",
            "class": "Launch Outcome",
            "Booster Version Category": "Booster Version Category",
        },
        title=f"Payload Mass and Launch Outcome for {site_label}",
    )
    figure.update_yaxes(
        tickmode="array",
        tickvals=[0, 1],
        ticktext=["Failure", "Success"],
        range=[-0.15, 1.15],
    )
    figure.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    figure.update_traces(marker={"size": 10, "opacity": 0.8})
    return style_figure(figure, f"Payload Mass and Launch Outcome for {site_label}")


def main() -> None:
    """Run the Dash development server for the course lab."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug)


if __name__ == "__main__":
    main()
