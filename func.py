#func
from types import NoneType
import streamlit as st 
from streamlit_js_eval import get_geolocation
from streamlit_folium import folium_static
import requests
import folium
from datetime import datetime
import pickle
import numpy as np
import geopandas as gpd
from shapely.geometry import Point




def get_coordinates_from_address(address):
    url = 'https://geocode.maps.co/search'
    params = {
        'q': address,
        'format': 'json',
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data:
        return {'latitude' : float(data[0]['lat']),
                'longitude': float(data[0]['lon'])}
        
    else:
        return {'latitude' : 0,
                'longitude': 0}
        #raise ValueError("Error: No coordinates found.")
        

def plot_map(location):
    map = folium.Map(location=[location['latitude'],location['longitude']],
                    zoom_start=12,
                    KEY='PUmap')
    mark = folium.Marker(
                    location=[location['latitude'],location['longitude']],
                    popup='You are here',
                    tooltip='Your Location',
                    draggable=False,
                    key='get_loc_mark')
            
    mark.add_to(map)
    folium_static(map,width=650)
    return map,mark

def get_location():
    loc = get_geolocation()
    return loc

def distance_matrix(pickup,dropoff):
    url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(pickup['longitude'],pickup['latitude'],dropoff['longitude'],dropoff['latitude'])
    r = requests.get(url)
    result = r.json()
    return result['routes'][0]['distance'],result['routes'][0]['duration']


def get_locatinID(coords,zone_list):
    if coords!=None:
        point = Point(coords['longitude'], coords['latitude'])
        matching_zone = zone_list[zone_list.geometry.contains(point)]
        if not matching_zone.empty:
            LocationID = matching_zone.iloc[0]['objectid']
            return LocationID
        else:
            return -1
    else:
        return -1


def generate_random_location(shapefile_path, polygon_id):
    # Step 1: Read the shapefile
    gdf = shapefile_path
    # Step 2: Get the specific polygon by ID
    selected_polygon = gdf[gdf['objectid'] == polygon_id].geometry.values[0]

    # Step 3: Get the bounding box of the selected polygon
    bounding_box = selected_polygon.bounds

    # Step 4: Generate random coordinates within the bounding box
    min_x, min_y, max_x, max_y = bounding_box
    random_point = Point(np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y))

    # Step 5: Check if the point is within the selected polygon
    if selected_polygon.contains(random_point):
        location = {'longitude':random_point.x,
                    'latitude': random_point.y}
        # Step 6: Return longitude and latitude
        return location
    else:
        # Retry if not within the polygon
        return generate_random_location(shapefile_path, polygon_id)
    
def predict(pass_count, distance, RCID, PUL, DOL, time, hour, weekday):
       # Load the model
       pickle_in = open('taxi_RF.pkl', 'rb')
       regressor = pickle.load(pickle_in)
       pred = regressor.predict([[pass_count, distance, RCID, PUL, DOL, time, hour, weekday]])
       st.success(f'Your fare for the trip will be {pred}') 