# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id="site-dropdown",
                                    options=[
                                        {"label": "All Sites", "value": "ALL"}
                                    ] + [
                                        {"label": site, "value": site}
                                        for site in spacex_df["Launch Site"].unique()
                                    ],
                                    value="ALL",
                                    placeholder="Select a Launch Site here",
                                    searchable=True,
                                    clearable=False
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id="payload-slider",
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={
                                        0: "0",
                                        2000: "2000",
                                        4000: "4000",
                                        6000: "6000",
                                        8000: "8000",
                                        10000: "10000"
                                    },
                                    value=[min_payload, max_payload]
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):

    if entered_site == "ALL":
        success_counts = (
            spacex_df.groupby("Launch Site", as_index=False)["class"]
            .sum()
        )

        fig = px.pie(
            success_counts,
            values="class",
            names="Launch Site",
            title="Successful Launches by Site"
        )

    else:
        filtered_df = spacex_df[
            spacex_df["Launch Site"] == entered_site
        ]

        outcome_counts = (
            filtered_df["class"]
            .value_counts()
            .reindex([0, 1], fill_value=0)
            .rename_axis("class")
            .reset_index(name="Count")
        )

        outcome_counts["Outcome"] = outcome_counts["class"].map(
            {0: "Unsuccessful", 1: "Successful"}
        )

        fig = px.pie(
            outcome_counts,
            values="Count",
            names="Outcome",
            title=f"Launch Outcomes for {entered_site}",
            color="Outcome",
            color_discrete_map={
                "Unsuccessful": "red",
                "Successful": "green"
            }
        )

    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value")
    ]
)
def get_scatter_chart(entered_site, payload_range):

    # Read the slider's lower and upper values
    low_payload, high_payload = payload_range

    # Apply the payload filter for every site selection
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low_payload)
        & (spacex_df["Payload Mass (kg)"] <= high_payload)
    ]

    if entered_site == "ALL":
        chart_title = "Payload and Landing Outcome for All Sites"

    else:
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]

        chart_title = (
            f"Payload and Landing Outcome for {entered_site}"
        )

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        title=chart_title,
        labels={
            "Payload Mass (kg)": "Payload Mass (kg)",
            "class": "Landing Outcome",
            "Booster Version Category": "Booster Version"
        }
    )

    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=["Unsuccessful (0)", "Successful (1)"],
        range=[-0.2, 1.2]
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
