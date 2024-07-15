#taxi-app

import streamlit as st
import streamlit.components.v1 as components
from func import *

def main():
    st.title('NYC taxi fare prediction')
    try:
        pickup = get_geolocation()['coords']
        #st.write(pickup)
    except:
        st.write('Auto location Failed')

    if pickup:
            PUmap,PU_mark = plot_map(pickup)
    else:
        PUaddr = st.text_input("Enter Pickup Address")
        pickup = get_coordinates_from_address(PUaddr)
        if pickup:
            PUmap,PU_mark = plot_map(pickup)
            PU_mark.add_to(PUmap)
            folium_static(PUmap,width=725)
    
    if st.button('Choose Location from Map'):
        PU_mark.options['draggable'] = True
        folium_static(PUmap)



    address = st.text_input("Enter Drop off locaation.")

    if address:
        dropoff = get_coordinates_from_address(address)
        #st.write(dropoff)
        DOmap,DO_mark = plot_map(dropoff)

    distance,time = distance_matrix(pickup=pickup,dropoff=dropoff)
    st.write(distance,time) 
    
    pass_count = st.number_input('Enter number of passengers', min_value=1)

    RCID = st.radio('Select your RateCodeID', options=[1,2,3,4,5,6])

    hour = int(datetime.now().hour)
    weekday = datetime.now().weekday()

    taxi_zones = gpd.read_file("/home/user/Desktop/wheres-my-taxi/wheres-my-taxi/2019_data/geo_export_4323a1fa-9e81-4f79-bb4c-9011fa40138e.shp")
    PUL = get_locatinID(pickup,taxi_zones)
    DOL = get_locatinID(dropoff,taxi_zones)

    pickle_in = open('taxi_RF.pkl','rb')
    regressor = pickle.load(pickle_in)
    st.write([pass_count,distance,RCID,PUL,DOL,time,hour,weekday])
    #@st.cache()

    if st.button('Predict Fare'):
    #def prediction(PUL,DOL,distance,time,pass_count,RCID,hour,weekday):
        pred = regressor.predict([[pass_count,distance,RCID,PUL,DOL,time,hour,weekday]])
        st.success(f'Your fare for the trip will be {pred}')
    


    

if __name__ == "__main__":
    main()