#taxi-app

import streamlit as st

from func import *

def main():
    st.set_page_config(layout='wide')
    if 'pickup' not in st.session_state:
        st.session_state.pickup = None

    if 'dropoff' not in st.session_state:
        st.session_state.dropoff =None
        
    st.title('NYC taxi fare prediction',)
    taxi_zones = gpd.read_file("/home/user/Desktop/wheres-my-taxi/wheres-my-taxi/2019_data/geo_export_4323a1fa-9e81-4f79-bb4c-9011fa40138e.shp")
    col1, col2, col3 =  st.columns([2,1,2])
    with col2:
        try:
            st.session_state.pickup = get_geolocation()['coords']
            if get_locatinID(st.session_state.pickup,taxi_zones) == -1:
                
                st.warning('You are not in New York')
        except:
            st.warning('Auto location Failed')
    with col1:
        if get_locatinID(st.session_state.pickup,taxi_zones) != -1:
            PUmap,PU_mark = plot_map(st.session_state.pickup)
            PUaddr = st.text_input("Enter Pickup Address from New york only")
            st.session_state.pickup = get_coordinates_from_address(PUaddr)
            if get_locatinID(st.session_state.pickup,taxi_zones) != -1:
                PUmap,PU_mark = plot_map(st.session_state.pickup)
                PU_mark.add_to(PUmap)
                folium_static(PUmap,width=725)
            else:
                st.warning('Enter Pickup addess from NEW york only')
        else:
            st.write('Since you are not in NYC, we are choosing random location from NYC')
            st.session_state.pickup = generate_random_location(taxi_zones,5)
            PUmap,PU_mark = plot_map(st.session_state.pickup)
            PU_mark.add_to(PUmap)
            #folium_static(PUmap,width=725)
    with col3:
        st.write('Generate Random Dropoff(FOR TESTING)')
        st.session_state.dropoff = generate_random_location(taxi_zones,np.random.randint(210))
        plot_map(st.session_state.dropoff)

        
#inputs
    with col2:
        st.session_state.pass_count = st.number_input('Enter number of passengers', min_value=1)
        st.session_state.RCID = st.radio('Select your RateCodeID', options=[1,2,3,4,5,6])
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

        #st.write(st.session_state)
       
        z = predict(pass_count, distance, RCID, PUL, DOL, time, hour, weekday)


if __name__ == "__main__":
    main()