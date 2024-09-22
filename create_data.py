import pandas as pd
import random
import datetime as dt
import folium
import geopy.distance

class path:
    data = r'C:\Users\lara_\Documents\scripts\flights\data.csv'
    map = r'C:\Users\lara_\Documents\scripts\flights\flight_routes_map.html'

df = pd.DataFrame(index=range(0,30000))

airlines = [
    'American Airlines',
    'Delta Air Lines'
]

df['airline'] = [random.choice(airlines) for _ in range(len(df))]
df

places = [
    ['MTY',25.67507, -100.31847],
    ['CDMX',19.42847, -99.12766],
    ['PUEBLA',19.03793, -98.20346],
    ['CANCUN',21.17429, -86.84656],
    ['SLP',22.14982, -100.97916],
]

def set_random_place(row):
    return random.choice(places)
def set_random_destination(row):
    return random.choice([place for place in places if place[0] != row['origin']])

df[['origin', 'origin_lat', 'origin_long']] = df.apply(set_random_place, axis=1, result_type='expand')
df[['destination', 'destination_lat', 'destination_long']] = df.apply(set_random_destination, axis=1, result_type='expand')
df

def generate_random_datetime(row):
    start_date = dt.datetime(2023,1,1)
    end_date = dt.datetime(2024,1,1)
    time_diff = end_date - start_date
    random_seconds = random.randint(0, int(time_diff.total_seconds()/60))
    return start_date + dt.timedelta(minutes=random_seconds)
def generate_arrive_date(row):
    distance = geopy.distance.geodesic((row['origin_lat'], row['origin_long']), (row['destination_lat'], row['destination_long'])).km
    speed = 860 #km/h
    time = distance / speed
    time = round(time,2 )
    return time, distance, row['departure_date'] + dt.timedelta(hours=time)

df['departure_date'] = df.apply(generate_random_datetime, axis=1, result_type='expand')
df[['flight_time','flight_distance','arrive_date']] = df.apply(generate_arrive_date, axis=1, result_type='expand')
df

def generate_price(row):
    unit_price = 0.15 # in dolar, per km
    random_variation = 10
    price = row['flight_distance'] * unit_price
    price = price + random.randint(-random_variation,random_variation)
    return round(price,2)
df['price'] = df.apply(generate_price, axis=1, result_type='expand')
df

df.to_csv(path.data,index=False)

# map
m = folium.Map(location=(25.67507, -100.31847))

def generate_routes(row):
    # Marcador para el origen
    folium.Marker(
        location=[row['origin_lat'], row['origin_long']],
        tooltip="Origin",
        popup="Origin Location",
        icon=folium.Icon(icon="cloud"),
    ).add_to(m)

    # Marcador para el destino
    folium.Marker(
        location=[row['destination_lat'], row['destination_long']],
        tooltip="Destination",
        popup="Destination Location",
        icon=folium.Icon(icon="cloud"),
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



##### routes