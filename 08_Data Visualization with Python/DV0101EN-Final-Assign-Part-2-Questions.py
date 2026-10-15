import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


# Load the automobile-sales dataset supplied for the final assignment.
DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"
)
data = pd.read_csv(DATA_URL)
data["Year"] = data["Year"].astype(int)

year_list = list(range(1980, 2024))

app = dash.Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"


def graph_cell(figure):
    """Place one graph in one half of a dashboard row."""
    return html.Div(
        dcc.Graph(figure=figure),
        style={"width": "50%", "minWidth": 0},
    )


def graph_row(left_figure, right_figure):
    """Create one row containing two dashboard graphs."""
    return html.Div(
        [graph_cell(left_figure), graph_cell(right_figure)],
        className="chart-item",
        style={"display": "flex", "width": "100%"},
    )


app.layout = html.Div(
    [
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={
                "textAlign": "center",
                "color": "#503D36",
                "fontSize": 24,
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select Statistics:"),
                        dcc.Dropdown(
                            id="dropdown-statistics",
                            options=[
                                {
                                    "label": "Yearly Statistics",
                                    "value": "Yearly Statistics",
                                },
                                {
                                    "label": "Recession Period Statistics",
                                    "value": "Recession Period Statistics",
                                },
                            ],
                            placeholder="Select a report type",
                            value="Select Statistics",
                        ),
                    ],
                    style={"width": "48%"},
                ),
                html.Div(
                    [
                        html.Label("Select Year:"),
                        dcc.Dropdown(
                            id="select-year",
                            options=[
                                {"label": year, "value": year} for year in year_list
                            ],
                            placeholder="Select a year",
                            value="Select-year",
                            disabled=True,
                        ),
                    ],
                    style={"width": "48%"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "marginBottom": "20px",
            },
        ),
        html.Div(
            id="output-container",
            className="chart-grid",
            style={"display": "flex", "flexDirection": "column", "width": "100%"},
        ),
    ]
)


@app.callback(
    Output(component_id="select-year", component_property="disabled"),
    Input(component_id="dropdown-statistics", component_property="value"),
)
def update_input_container(selected_statistics):
    """Enable the year selector only for the yearly report."""
    return selected_statistics != "Yearly Statistics"


@app.callback(
    Output(component_id="output-container", component_property="children"),
    [
        Input(component_id="dropdown-statistics", component_property="value"),
        Input(component_id="select-year", component_property="value"),
    ],
)
def update_output_container(selected_statistics, input_year):
    """Create the four graphs requested for the selected report."""
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        yearly_rec = (
            recession_data.groupby("Year", as_index=False)["Automobile_Sales"].mean()
        )
        recession_chart_1 = px.line(
            yearly_rec,
            x="Year",
            y="Automobile_Sales",
            title="Average Automobile Sales Fluctuation Over Recession Period",
        )

        vehicle_sales = (
            recession_data.groupby("Vehicle_Type", as_index=False)[
                "Automobile_Sales"
            ].mean()
        )
        recession_chart_2 = px.bar(
            vehicle_sales,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title="Average Number of Vehicles Sold by Vehicle Type During Recession",
        )

        advertising = (
            recession_data.groupby("Vehicle_Type", as_index=False)[
                "Advertising_Expenditure"
            ].sum()
        )
        recession_chart_3 = px.pie(
            advertising,
            names="Vehicle_Type",
            values="Advertising_Expenditure",
            title="Total Advertising Expenditure by Vehicle Type During Recession",
        )

        unemployment_sales = (
            recession_data.groupby(
                ["unemployment_rate", "Vehicle_Type"], as_index=False
            )["Automobile_Sales"].mean()
        )
        recession_chart_4 = px.bar(
            unemployment_sales,
            x="unemployment_rate",
            y="Automobile_Sales",
            color="Vehicle_Type",
            title="Effect of Unemployment Rate on Vehicle Type and Sales",
            labels={"unemployment_rate": "Unemployment Rate"},
        )

        return [
            graph_row(recession_chart_1, recession_chart_2),
            graph_row(recession_chart_3, recession_chart_4),
        ]

    if selected_statistics == "Yearly Statistics" and input_year in year_list:
        yearly_data = data[data["Year"] == input_year]

        yearly_sales = data.groupby("Year", as_index=False)["Automobile_Sales"].mean()
        yearly_chart_1 = px.line(
            yearly_sales,
            x="Year",
            y="Automobile_Sales",
            title="Yearly Average Automobile Sales",
        )

        monthly_sales = yearly_data.groupby("Month", as_index=False)[
            "Automobile_Sales"
        ].sum()
        yearly_chart_2 = px.line(
            monthly_sales,
            x="Month",
            y="Automobile_Sales",
            title=f"Total Monthly Automobile Sales in {input_year}",
        )

        vehicle_sales = yearly_data.groupby("Vehicle_Type", as_index=False)[
            "Automobile_Sales"
        ].mean()
        yearly_chart_3 = px.bar(
            vehicle_sales,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title=f"Average Vehicles Sold by Vehicle Type in {input_year}",
        )

        advertising = yearly_data.groupby("Vehicle_Type", as_index=False)[
            "Advertising_Expenditure"
        ].sum()
        yearly_chart_4 = px.pie(
            advertising,
            names="Vehicle_Type",
            values="Advertising_Expenditure",
            title=f"Total Advertising Expenditure by Vehicle Type in {input_year}",
        )

        return [
            graph_row(yearly_chart_1, yearly_chart_2),
            graph_row(yearly_chart_3, yearly_chart_4),
        ]

    return []


if __name__ == "__main__":
    app.run(debug=True)
