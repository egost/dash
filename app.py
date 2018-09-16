import time
import os


import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import create_engine


external_stylesheets = [
        'https://fonts.googleapis.com/css?family=Raleway:400,300,600',
]

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)
server = app.server

yellow = '#FEBE10'


# Prep Input Data

DATABASE_USER = os.environ.get("DB_USER", '')
DATABASE_PASSWORD = os.environ.get("DB_PASSWORD", '')
DATABASE_URL = os.environ.get("DB_URL", '')
DATABASE_NAME = os.environ.get("DB_NAME", '')

host = "mysql://{}:{}@{}/{}".format(DATABASE_USER,DATABASE_PASSWORD,DATABASE_URL,DATABASE_NAME)
engine = create_engine(host)

df = pd.read_sql('rides', con=engine)
df['date']  = pd.to_datetime(df['date'])

# Useful Variables
dates = df['date'].map(pd.Timestamp.date).unique()

colors = {
            '2017-04-14': {'name':'Spring', 'rgb':'rgba(70, 144, 36, 1)'},
            '2017-07-29': {'name':'Summer', 'rgb':'rgba(247, 23, 53, 1)'},
            '2017-10-12': {'name':'Autumn',  'rgb':'rgba(230, 194, 41, 1)'},
            '2017-12-21': {'name':'Winter', 'rgb':'rgba(35, 110, 142, 1)'},
        }

season_dates = list(colors.keys())


# App Elements
name_dropdown = dcc.Dropdown(
    id='ride-name',
    options=[{'label':name, 'value':name} for name in df.ride_name.unique()],
    value=df.ride_name[0],
    )

date_slider = dcc.RangeSlider(
    id='date-slider',
    marks={i: '{}'.format(dates[i]) for i in range(0, len(dates))},
    min=0,
    max=len(dates),
    value=[0, len(dates)]
    )

date_checklist = dcc.Checklist(
    id='date-checklist',
    options=[{'label':date, 'value':date} for date in dates],
    values=[dates[0]],
    # labelStyle={'margin-right': '100px'}
    # className='checklist'
    )

seasons_checklist = dcc.Checklist(
    id='seasons-checklist',
    options=[{'label':date, 'value':date} for date in season_dates],
    values=[season_dates[0], season_dates[1]],
    # labelStyle={'margin-right': '100px'}
    # className='checklist'
    )

app.layout = html.Div([
    html.H3('Ride Daily Throughput'),
    html.Div([
        html.Div([
            name_dropdown,
            seasons_checklist,
            ], className='two columns'),
        html.Div([
            dcc.Graph(id='seasons-daily-ride-throughput'),
            ], className='ten columns'),
        ], className='row'),
    ], className='main-div')


def date_range(df, begin, end):
    """Returns a list of valid dates from begin to end"""
    return df[(df.date > pd.Timestamp(begin)) & (df.date <= pd.Timestamp(end))]


def day_data(df, day):
    """Returns a dataframe that only contains the information for a single day"""
    search = df.date.map(pd.Timestamp.date)
    date = pd.Timestamp.date(pd.Timestamp(day))
    data = df[search == date].rename(columns={'date':'time'})
    data['time'] = data['time'].dt.strftime("%-I %p")
    return data


@app.callback(
    dash.dependencies.Output('seasons-daily-ride-throughput', 'figure'),
    [
        dash.dependencies.Input('ride-name', 'value'),
        dash.dependencies.Input('seasons-checklist', 'values')
    ])
def seasons_daily_ride_throughput(ride_name, date_checklist):
    ride_data = df[df.ride_name == ride_name]
    traces = []
    for date in date_checklist:
        day = day_data(ride_data, date)
        traces.append(go.Scatter(
            x=day['time'],
            y=day['throughput'],
            # text=data['throughput'],
            mode='lines+markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'black'},
                'color':colors[date]['rgb'],
            },
            name=colors[date]['name']
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Time', 'color':yellow},
            yaxis={'title': 'Throughput', 'color':yellow},
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend= dict(font=dict(
                            color=yellow
                            )
                ),
            # grid={'color':'black'},
            hovermode='closest',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0.5)',
        )
    }

# @app.callback(
#     dash.dependencies.Output('daily-ride-throughput', 'figure'),
#     [
#         dash.dependencies.Input('ride-name', 'value'),
#         dash.dependencies.Input('date-checklist', 'values')
#     ])
# def daily_ride_throughput_all_dates(ride_name, date_checklist):
#     ride_data = df[df.ride_name == ride_name]
#     traces = []
#     for date in date_checklist:
#         day = day_data(ride_data, date)
#         traces.append(go.Scatter(
#             x=day['time'],
#             y=day['throughput'],
#             # text=data['throughput'],
#             mode='lines+markers',
#             opacity=0.6,
#             marker={
#                 'size': 15,
#                 'line': {'width': 0.5, 'color': 'black'}
#             },
#             name=date
#         ))

#     return {
#         'data': traces,
#         'layout': go.Layout(
#             xaxis={'title': 'Time'},
#             yaxis={'title': 'Throughput'},
#             # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             # legend={'x': 0, 'y': 1},
#             hovermode='closest'
#         )
#     }


if __name__ == '__main__':
    app.run_server(debug=False)
