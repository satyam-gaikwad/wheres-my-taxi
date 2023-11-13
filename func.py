#func
from logging import raiseExceptions
from streamlit_js_eval import get_geolocation
from streamlit_folium import folium_static
import requests
import folium


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
        raise ValueError("Error: No coordinates found.")
        

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
    folium_static(map,width=725)
    return map,mark

def get_location():
    loc = get_geolocation()
    return loc

def distance_matrix(pickup,dropoff):
    url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}".format(pickup['longitude'],pickup['latitude'],dropoff['longitude'],dropoff['latitude'])
    r = requests.get(url)
    result = r.json()
    return result['routes'][0]['distance'],result['routes'][0]['duration']