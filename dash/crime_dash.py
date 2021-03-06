from datetime import date
import pandas as pd
from dash import no_update
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
import dash_table
import plotly.graph_objs as go
from flask import request
from plotly.graph_objs import Layout
import dash_daq as daq
from functools import reduce
from sklearn import preprocessing
import numpy as np
from NLP.POS.pos import analyse_victim

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)


# top banner
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("GR.C.A"),
                    html.H6("Greek Crime Analytics"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="I Like Trees", n_clicks=0
                    ),
                    html.Img(id="logo", src=app.get_asset_url("agroknow-logo.png")),
                ],
            ),
        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


def my_crime_table():
    article_summary, victim_gender, criminal_status = analyse_victim()

    layout = Layout(
        plot_bgcolor='rgba(49, 75, 86, 1)',
        paper_bgcolor='rgba(22, 26, 40, 1)',
    )

    fig = go.Figure(
        layout=layout,
        data=[
            go.Table(
                cells=dict(
                    values=article_summary,
                    line_color='darkslategray',
                    fill=dict(color=['white']),
                    align=['left', 'center'],
                    font_size=12,
                    height=30)
            )])

    return fig


app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),  # this is the top top part
        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=50,  # start at batch 50
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="news_table",
                    children=[
                        generate_section_banner("News"),
                        dcc.Graph(figure=my_crime_table())
                    ]),
            ]),
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
