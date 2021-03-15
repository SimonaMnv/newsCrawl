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
from spacy.lang.lex_attrs import lower
from NLP.POS.pos import analyse_victim
from elasticsearchapp.query_results import get_n_raw_data

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}]
)

global UNIQUE_TERMS
global END_DATE

UNIQUE_TERMS = ['ΔΟΛΟΦΟΝΙΑ', 'ΝΑΡΚΩΤΙΚΑ', 'ΤΡΟΜΟΚΡΑΤΙΚΗ ΕΠΙΘΕΣΗ', 'ΛΗΣΤΕΙΑ', 'ΣΕΞΟΥΑΛΙΚΟ ΕΓΚΛΗΜΑ']


def generated_data(start_date, end_date, crime_type):
    # load data
    data = get_n_raw_data(crime_type, 10)

    for datum in data:
        refactored_date = datum['Date'].split("T")
        datum['Date'] = refactored_date[0]

    df = pd.DataFrame(data=data)
    df.to_csv('data/' + crime_type + '.csv', index=False)

    return df


# top banner
def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.Button(
                        id="learn-more-button", children="Greek Crime Analytics", n_clicks=0
                    ),
                ],
            ),
        ],
    )


def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)


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
        html.Div(id='choices', children=[
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2012, 1, 1),
                max_date_allowed=date.today(),
                initial_visible_month=date.today(),
                display_format='Y-MM-DD',
                start_date=date(2012, 1, 1),
                end_date=date.today()
            ),
        ]),
        # popup modal
        dcc.Loading(
            id="loading-2",
            type="default",
            children=[
                html.Div(
                    id="modal-div",
                    children=[
                        dbc.Modal(
                            children=[
                                dbc.ModalFooter(
                                    dbc.Button("Close", id="close", className="ml-auto")
                                ),
                            ],
                            id="modal"
                        ),
                    ]),
            ]),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="news_table",
                    children=[
                        html.Div(
                            id="selector",
                            children=[
                                # drop down menu
                                generate_section_banner("Filter by Crime Type"),
                                dcc.Loading(
                                    id="loading-1",
                                    type="default",
                                    children=[
                                        dcc.Dropdown(
                                            id='crime_type_dd',
                                            options=[],
                                            clearable=False,
                                        ),
                                    ]),
                            ]),
                        dcc.Loading(
                            id="loading-data",
                            type="cube",
                            children=[
                                html.Div(
                                    id="fdk-part",
                                    children=[
                                        html.Button('Apply Filters', id='btn-submit', n_clicks=0,
                                                    style=dict(width='100%')),
                                        generate_section_banner("Results"),
                                        dash_table.DataTable(
                                            id='crime_table',
                                            page_size=10,
                                            fixed_rows={'headers': True},
                                            style_table={'overflowY': 'scroll'},
                                            style_header={
                                                'backgroundColor': '#314b56',
                                                'color': 'white',
                                                'fontWeight': 'bold'
                                            },
                                            style_as_list_view=True,
                                            style_cell={
                                                'backgroundColor': '#1e2130',
                                                'color': 'white',
                                                'textAlign': 'left',
                                                'padding': '15px',
                                                'font-family': 'sans-serif',
                                                'minWidth': '180px', 'width': '180px',
                                                'maxWidth': '300px',
                                                'overflow': 'hidden',
                                                'textOverflow': 'ellipsis',
                                            },
                                            style_data_conditional=(),
                                            css=[{
                                                'selector': '.dash-table-tooltip',
                                                'rule': 'background-color: black; font-family: sans-serif;'
                                            }],
                                            tooltip_delay=0,
                                            tooltip_duration=None,
                                        ),
                                    ]),
                            ]),
                    ]),
            ]),
    ]
)


@app.callback(
    [
        Output('crime_table', 'data'),
        Output('crime_table', 'columns'),
        Output('crime_table', 'style_data_conditional')
    ],
    [
        Input("crime_type_dd", "value"),
        Input('btn-submit', 'n_clicks'),
    ],
)
def update_values_and_charts(crime_type, btn):
    # apply on each click
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    victims = []
    c_status = []
    acts = []
    ages = []
    dates = []

    if 'btn-submit' in changed_id:
        crime_merged_table = generated_data(None, None, crime_type)

        for type, body, title in zip(crime_merged_table['Type'], crime_merged_table['Body'], crime_merged_table['Title']):
            context = title + " " + body
            if crime_type == 'ΔΟΛΟΦΟΝΙΑ':   # elastic top verb similarity mixed with POS analysis and NER analysis
                columns = ['Date', 'Title', 'Body', 'Type', 'Victim', 'Criminal Status', 'Acts', 'Ages', 'Crime Date']

                article_summary, victim_gender, criminal_status, act, age, date = analyse_victim(context, crime_type)
                victims.append(victim_gender)
                c_status.append(criminal_status)
                acts.append([str(x)+" " for x in act])
                ages.append([str(x)+" " for x in age])
                dates.append([str(x)+" " for x in date])

        crime_merged_table['Victim'] = victims
        crime_merged_table['Criminal Status'] = c_status
        crime_merged_table['Acts'] = acts
        crime_merged_table['Ages'] = ages
        crime_merged_table['Crime Date'] = dates

        if len(crime_merged_table) == 0:
            return no_update, no_update, no_update

        data_table = crime_merged_table.to_dict("records")

        return data_table, [{"name": i, "id": i} for i in columns], (
            [
                {
                    "if": {"state": "selected"},  # 'active' | 'selected'
                    "backgroundColor": "rgba(0, 116, 217, 0.3)",
                    "border": "1px solid blue",
                }
            ]
        )

    else:
        return [], [], []


@app.callback(
    [
        Output("modal", "is_open"),
        Output('modal', 'children'),
    ],
    [
        Input("crime_table", "active_cell"),  # open button
        Input("close", "n_clicks"),  # close button
        Input("crime_table", "data"),
    ],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, crime_table, is_open):
    if not crime_table:
        return no_update, no_update

    if n1 is not None:
        if (n1 and n1['column_id'] == 'Title') or n2:
            return not is_open, (
                       dbc.ModalHeader("Full Title of Article"),
                       dbc.ModalBody(children=[
                               html.Label(html.A(crime_table[n1['row']]['Title']))]
                               ),
                       dbc.ModalFooter(
                           dbc.Button("Close", id="close", className="ml-auto")
                       ),
                   )
        elif (n1 and n1['column_id'] == 'Body') or n2:
            return not is_open, (
                dbc.ModalHeader("Full Body of Article"),
                dbc.ModalBody(children=[
                    html.Label(html.A(crime_table[n1['row']]['Body']))]
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            )
        else:
            return is_open, no_update
    else:
        return no_update, no_update


@app.callback([
    Output("crime_type_dd", "options"),
    Output("crime_type_dd", "value"),
],
    [
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date')
    ])
def generate_initial_date_terms(start_date, end_date):
    global END_DATE
    END_DATE = end_date

    return [{'value': x, 'label': x}
            for x in UNIQUE_TERMS], UNIQUE_TERMS[0]


if __name__ == '__main__':
    app.run_server(debug=True)
