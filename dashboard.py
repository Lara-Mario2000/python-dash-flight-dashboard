from dash import Dash, html, dcc, dash_table, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import folium
import datetime as dt
import numpy as np

class path:
    data = r'C:\Users\lara_\Documents\scripts\flights\data.csv'
    map = r'C:\Users\lara_\Documents\scripts\flights\flight_routes_week_map.html'

def get_data():
    df = pd.read_csv(path.data)
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    df["arrive_date"] = pd.to_datetime(df["arrive_date"])
    return df

def get_filter_df(df, airline, origin, destination, date, min_hour, max_hour):
    df_filtered = df[df['airline'].isin(airline)] if airline not in [[], None] else df
    df_filtered = df_filtered[df_filtered['origin'].isin(origin)] if origin not in [[], None] else df_filtered
    df_filtered = df_filtered[df_filtered['destination'].isin(destination)] if destination not in [[], None] else df_filtered
    df_filtered = df_filtered[df_filtered['arrive_date'].dt.date==date]
    df_filtered = df_filtered[(df_filtered['arrive_date'].dt.hour<=max_hour) & (df_filtered['arrive_date'].dt.hour>=min_hour)]
    return df_filtered

def generate_map(df):
    lat = df['destination_lat'].mean() if not df.empty else 21.536989891304348
    long = df['destination_long'].mean() if not df.empty else -96.94262173913046
    m = folium.Map(location=(lat,long), zoom_start=5)
    
    #map
    def generate_routes(row):
        # Marcador para el origen
        folium.Marker(
            location=[row['origin_lat'], row['origin_long']],
            tooltip="Origin",
            popup="Origin Location",
            icon=folium.Icon(icon="plane"),
        ).add_to(m)

        # Marcador para el destino
        folium.Marker(
            location=[row['destination_lat'], row['destination_long']],
            tooltip="Destination",
            popup="Destination Location",
            icon=folium.Icon(icon="plane"),
        ).add_to(m)

        # Añadir una línea entre el origen y destino
        folium.PolyLine(
            locations=[(row['origin_lat'], row['origin_long']), 
                    (row['destination_lat'], row['destination_long'])],
            color='blue'
        ).add_to(m)

    # Aplicar la función a cada fila del DataFrame
    df.apply(generate_routes, axis=1)

    # Guardar el mapa con todos los puntos y líneas al final
    m.save(path.map)

df = get_data()


### Dash
external_scripts = [
    {
        'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
        'integrity': 'sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
external_stylesheets = [
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH',
        'crossorigin': 'anonymous'
    },
]


app = Dash(
    __name__,
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets
)


app.layout = [
    html.Div([
        html.H1(
            "Flight Routes Map", 
            className='header'
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P(
                            children='Airline',
                            className='h6'
                        ),
                        dcc.Checklist(
                            id='airline-checklist',
                            options=df['airline'].unique().tolist()
                        ),
                        html.P(
                            children='Flight Origin',
                            className='h6'
                        ),
                        dcc.Checklist(
                            id='origin-checklist',
                            options=df['origin'].unique().tolist()
                        ),
                        html.P(
                            children='Flight Destination',
                            className='h6'
                        ),
                        dcc.Checklist(
                            id='destination-checklist',
                            options=df['destination'].unique().tolist()
                        ),
                        html.P(
                            children='Day',
                            className='h6'
                        ),
                        dcc.Slider(
                            id='arriveDate-slider',
                            min=0, 
                            max = df['arrive_date'].dt.date.nunique()-1, 
                            step = 1,
                            value = 0,
                            marks=None,
                            included=False
                        ),
                        html.P(
                            id='output-container-slider', 
                            className='h6'
                        ),
                        html.P(
                            children='Time',
                            className='h6'
                        ),
                        dcc.RangeSlider(
                            id='arriveHour-range-slider',
                            min=0, 
                            max = 24, 
                            value = [0,24]
                        )
                    ],
                    className='mt-3 ms-3',
                    style={'overflow-x': 'auto'}
                ),
                html.Iframe(
                    id="map",
                    srcDoc=open(path.map, 'r').read(),
                    className='map'
                )
            ],
            className='split-container'
        ),
        html.Div([
            dash_table.DataTable(
                id='datatable-interactivity',
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                ],
                data=df.to_dict('records'),
                #editable=True,
                #filter_action="native",
                sort_action="native",
                sort_mode="multi",
                #column_selectable="single",
                #row_selectable="multi",
                #row_deletable=True,
                #selected_columns=[],
                #selected_rows=[],
                page_action="native",
                page_current= 0,
                page_size= 10,
                style_cell={'fontSize':'1rem', 'font-family':'Roboto'}
            ),
            html.Div(
                id='datatable-interactivity-container'
            )
        ], className='mt-3 dash-data-table'
        )
    ])
]

unique_dates = df['arrive_date'].dt.date.unique()
unique_dates = np.sort(unique_dates)

@callback(
    Output('output-container-slider', 'children'),
    Input('arriveDate-slider', 'value'))
def update_output(value):
    return f"{unique_dates[value]}"

@callback(
    Output('datatable-interactivity', 'data'),
    Output('map', 'srcDoc'),
    Input('airline-checklist', 'value'),
    Input('origin-checklist', 'value'),
    Input('destination-checklist', 'value'),
    Input('arriveDate-slider', 'value'),
    Input('arriveHour-range-slider', 'value'),
    State('map', 'srcDoc'))
def update_map(airline, origin, destination, date, hour, current_src):
    date = unique_dates[date]
    min_hour = hour[0]
    max_hour = hour[1]
    df_filter = get_filter_df(df, airline, origin, destination, date, min_hour, max_hour)
    generate_map(df_filter)
    return df_filter.to_dict('records'), open(path.map, 'r').read()

if __name__ == '__main__':
    app.run(debug=True)