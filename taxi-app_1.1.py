#taxi-app

import streamlit as st
import streamlit.components.v1 as components
from func import *

def main():
    if 'pickup' not in st.session_state:
        st.session_state.pickup = None

    if 'dropoff' not in st.session_state:
        st.session_state.dropoff =None
        
    st.title('NYC taxi fare prediction')
    taxi_zones = gpd.read_file("/home/user/Desktop/wheres-my-taxi/wheres-my-taxi/2019_data/geo_export_4323a1fa-9e81-4f79-bb4c-9011fa40138e.shp")

    try:
        st.session_state.pickup = get_geolocation()['coords']
        if get_locatinID(pickup,taxi_zones) == -1:
            
            st.warning('You are not in New York')
    except:
        st.warning('Auto location Failed')

    if get_locatinID(st.session_state.pickup,taxi_zones) != -1:
            PUmap,PU_mark = plot_map(st.session_state.pickup)
    else:
        PUaddr = st.text_input("Enter Pickup Address from New york only")
        st.session_state.pickup = get_coordinates_from_address(PUaddr)
        if get_locatinID(st.session_state.pickup,taxi_zones) != -1:
            PUmap,PU_mark = plot_map(st.session_state.pickup)
            PU_mark.add_to(PUmap)
            folium_static(PUmap,width=725)
        else:
            st.warning('Enter Pickup addess from NEW york only')
            st.write('Since you are not in NYC, we are choosing random location from NYC')
            st.session_state.pickup = generate_random_location(taxi_zones,5)
            PUmap,PU_mark = plot_map(st.session_state.pickup)
            PU_mark.add_to(PUmap)
            #folium_static(PUmap,width=725)

    st.write('Generate Random Dropoff(FOR TESTING)')
    st.session_state.dropoff = generate_random_location(taxi_zones,np.random.randint(210))
    plot_map(st.session_state.dropoff)

    
#inputs
    st.session_state.pass_count = st.number_input('Enter number of passengers', min_value=1)
    st.session_state.RCID = st.radio('Select your RateCodeID', options=[1,2,3,4,5,6])
    hour = int(datetime.now().hour)
    weekday = datetime.now().weekday()
    st.session_state.distance,st.session_state.time = distance_matrix(pickup=st.session_state.pickup,dropoff=st.session_state.dropoff)
    st.session_state.PUL = get_locatinID(st.session_state.pickup,taxi_zones)
    #st.session_state.DOL = get_locatinID(st.session_state.dropoff,taxi_zones)
    st.session_state.DOL = np.random.randint(low=1,high=263)
    # Extract feature values from session state
    pass_count = st.session_state.pass_count
    RCID = st.session_state.RCID
    hour = int(datetime.now().hour)
    weekday = datetime.now().weekday()
    distance =st.session_state.distance
    time = st.session_state.time
    PUL = st.session_state.PUL
    DOL = st.session_state.DOL


    st.write([pass_count,distance,RCID,PUL,DOL,time,hour,weekday])


    if st.button('Predict Fare'):
        # Load the model
        pickle_in = open('taxi_RF.pkl', 'rb')
        regressor = pickle.load(pickle_in)

        st.write([pass_count, distance, RCID, PUL, DOL, time, hour, weekday])

        
        # Predict fare
        for i in range(263):
            pred = regressor.predict([[pass_count, distance, RCID, PUL, i, time, hour, weekday]])
            st.success(f'Your fare for the trip will be {pred}')



    

if __name__ == "__main__":
    main()