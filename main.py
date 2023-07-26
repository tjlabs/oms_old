import streamlit as st
import json, pytz
import requests
from datetime import datetime
from modules.plot import plot_charts

def set_page_title():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                       layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")
    st.divider()

def set_performance_sidebar():
    response_data = requests.get("http://localhost:8502/load-performance-indicators", data=json.dumps(None))
    if response_data.status_code == 200:
        performances = response_data.json()["indicators"]
        with st.sidebar:
            st.sidebar.multiselect(
                "Please select the performance metrics you would like to see.",
                performances
            )

@st.cache_data(experimental_allow_widgets=True)
def place_info_container():

    st.header("Select Place Information")

    command, col1, col2, col3, _ = st.columns([2,2,2,2,2])
    sector_key , building_key, level_key = -1, -1, -1
    with command:
        st.write("Select Place you want to Search")

    get_place_datas()

    if 'place_info' in st.session_state:
        places = list(st.session_state['place_info'].values())
        print(places)

    # with col1:
    #     if 'sectors' in st.session_state:
    #         sector = st.selectbox('Select sector', st.session_state['sectors'])
    #         sector_key = st.session_state['sectors'].index(sector)
    #     else:
    #         st.selectbox('Select sector', ())

    # with col2:
    #     if 'buildings' in st.session_state and sector_key != -1:
    #         building = st.selectbox('Select building', st.session_state['buildings'][sector_key])
    #         # building_key = building_list.index(building)
    #     else:
    #         st.selectbox('Select building')

    # with col3:
    #     if 'levels' in st.session_state and sector_key != -1:
    #         level = st.selectbox('Select level', st.session_state['levels'][sector_key])
    #         # level_key = level_list.index(level)
    #     else:
    #         st.selectbox('Select level')

def get_place_datas():
    response_data = requests.get("http://localhost:8502/place-info")
    if response_data.status_code == 200:
        data = response_data.json()

        place_info = data["placeInfo"]

        # sector_list, building_list, level_list = [], [], []
        # for i in range(1, len(place_info)+1):
        #     print(place_info[str(i)])
        #     print()
        #     sector_list.append(place_info[str(i)][0])
        #     if len(place_info[str(i)]) > 1:
        #         building_list.append(place_info[str(i)][1])
        #     else:
        #         building_list.append(['None'])

        #     if len(place_info[str(i)]) > 2:
        #         level_list.append(place_info[str(i)][2])
        #     else:
        #         level_list.append(['None'])

        if 'place_info' not in st.session_state:
            st.session_state['place_info'] = place_info

        # if 'buildings' not in st.session_state:
        #     st.session_state['buildings'] = building_list
        # if 'levels' not in st.session_state:
        #     st.session_state['levels'] = level_list


@st.cache_data
def get_current_time_and_json(): 
    with st.columns(1)[0]:
        st.header("Current Time")
        current_time_str = datetime.now(tz=pytz.timezone('Asia/Seoul')).isoformat()
        datetime_obj = datetime.strptime(current_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M')
        st.markdown(f"<span style='font-size: 40px;'>{formatted_time}</span>", unsafe_allow_html=True)

        current_time_json = json.dumps(current_time_str)

        if 'yesterday_date' not in st.session_state:
            st.session_state['yesterday_date'] = current_time_json

    return current_time_json

@st.cache_data
def get_yesterday_userinfos(current_time_json):
    if st.session_state['yesterday_date'] == current_time_json:
        response_data = requests.get("http://localhost:8502/get-yesterday-users", data=json.dumps({'start_time': current_time_json}))
    
        if response_data.status_code == 200:
            st.success('Loaded yesterday\'s whole users')
            data = response_data.json()
            
            if 'users' not in st.session_state:
                st.session_state['users'] = data["users"]
            if 'devices' not in st.session_state:
                st.session_state['devices'] = data["devices"]
            if 'total_data_count' not in st.session_state:
                st.session_state['total_data_count'] = data["totalDataCount"]
        
@st.cache_data
def save_yesterday_data(current_time_json):
    if 'users' in st.session_state:
        data = {'start_time': current_time_json, 'user_id': st.session_state['users'], 'device_model': st.session_state['devices']}
        response_data = requests.get("http://localhost:8502/save-yesterday", data=json.dumps(data))

        if response_data.status_code == 200:
            st.success('Updated until yesterday stats')

def load_webpage(current_time_json):
    perf_1, _, _, _, _ = st.columns([1,1,1,1,1])
    placeholder = st.empty()
    bar_chart, line_chart = st.columns([4, 4])
   
    # with perf_1:
    #     data = {'sector_id': 6, 'start_time': starttime_json_data, 'end_time': endtime_json_data}
    #     userID = requests.get("http://localhost:8502/api", data=json.dumps(data))
    #     st.session_state['yesterday_date']


    with placeholder.container():
        chart_data, loaded_data = None, None
        with bar_chart:
            response_data = requests.get("http://localhost:8502/performance-statistics", data=json.dumps({'end_time': current_time_json}))
            if response_data.status_code == 200:
                daily_datas = response_data.json()["dailyStatus"]
                if daily_datas != None:    
                    chart_data, loaded_data = plot_charts.plot_stacked_bar_chart(daily_datas)

        with line_chart:
            if daily_datas != None and not chart_data.empty and not loaded_data.empty:
                plot_charts.plot_line_chart(chart_data, loaded_data)
        st.markdown("### Detailed Data View")

if __name__ == '__main__' :
    set_page_title()
    set_performance_sidebar()
    place_info_container()
    current_time_json = get_current_time_and_json()
    get_yesterday_userinfos(current_time_json)
    save_yesterday_data(current_time_json)
    load_webpage(current_time_json)