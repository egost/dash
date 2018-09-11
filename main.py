import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go


app = dash.Dash()


# Prep Input Data

def silly_names(df):
    """Replaces copyrighted names with fake names"""

    def random_names():
        """Concatenates a list of names."""

        animals = list(pd.read_fwf('resources/animals.txt').values)
        adjectives = list(pd.read_fwf('resources/adjectives.txt').values)
        names = []
        for i in range(0, len(animals)):
            names.append(str(adjectives[i][0] + ' ' + animals[i][0]))
        return names

    silly_names = random_names()
    for original, silly in zip(df['ride_name'].unique(), random_names()):
        df['ride_name'] = df['ride_name'].replace(original, silly)

    return df


df = pd.read_csv('resources/dataframe.csv')
df['date']  = pd.to_datetime(df['date'])
df = silly_names(df)


# Useful Variables
dates = df['date'].map(pd.Timestamp.date).unique()
times = [str(time) for time in df.date.map(pd.Timestamp.time)]


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
    )

app.layout = html.Div([
    dcc.Graph(id='daily-ride-throughput'),
    name_dropdown,
    html.Div([
        date_checklist,
        ]
        )
])


def date_range(df, begin, end):
    """Returns a list of valid dates from begin to end"""
    return df[(df.date > pd.Timestamp(begin)) & (df.date <= pd.Timestamp(end))]


def day_data(df, day):
    """Returns a dataframe that only contains the information for a single day"""
    search = df.date.map(pd.Timestamp.date)
    date = pd.Timestamp.date(pd.Timestamp(day))
    data = df[search == date].rename(columns={'date':'time'})
    data['time'] = data['time'].map(pd.Timestamp.time)
    return data


@app.callback(
    dash.dependencies.Output('daily-ride-throughput', 'figure'),
    [
        dash.dependencies.Input('ride-name', 'value'),
        dash.dependencies.Input('date-checklist', 'values')
    ])
def update_figure(ride_name, date_checklist):
    ride_data = df[df.ride_name == ride_name]
    traces = []
    for date in date_checklist:
        day = day_data(ride_data, date)
        traces.append(go.Scatter(
            x=day['time'],
            y=day['throughput'],
            # text=data['throughput'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'black'}
            },
            name=date
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Time'},
            yaxis={'title': 'Throughput'},
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            # legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
