import streamlit as st
import json, pytz
import requests
from datetime import datetime
from modules.plot import plot_charts
from utils import data_requests, use_dict

def set_page_title():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                       layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")
    st.divider()

@st.cache_data
def load_performance_tables():
    if 'performance' not in st.session_state:
        try:
            request_result = data_requests.request_performance_indicators()
            st.session_state['performance'] = request_result
        except requests.exceptions.HTTPError as e:
            print("Error occurred:", e)

def set_performance_sidebar():
    if 'performance' in st.session_state:
        with st.sidebar:
            st.sidebar.multiselect(
                "Please select the performance metrics you would like to see.",
                st.session_state['performance']
            )

@st.cache_data
def get_place_datas():
    if 'place_info' not in st.session_state:
        try:
            request_result = data_requests.request_place_info()
            st.session_state['place_info'] = request_result
        except requests.exceptions.HTTPError as e:
            print("Error occurred:", e)

@st.cache_data
def extract_sectors():
    if 'place_info' in st.session_state:
        sector = {}
        for key, value in st.session_state['place_info'].items():
            sector[key] = value[0][0]
        
        if 'sectors' not in st.session_state:
            st.session_state['sectors'] = sector

def set_place_selection():
    st.header("Place Information")

    command, col1, col2, col3 = st.columns([1,2,2,2])
    sector_key = 1
    with command:
        st.write("Select Place you want to Search")

    with col1:
        sector_key = select_sector()
        if sector_key == '':
            st.selectbox('No sector', ())

    with col2:
        building_idx = select_building(sector_key)
        if building_idx == -1:
            st.selectbox('No building', ())

    with col3:
        level_name = select_level(sector_key, building_idx)
        if level_name == "":
            st.selectbox('No level', ())

def select_sector() -> str:
    if 'sectors' in st.session_state:
        sector = st.selectbox('Select sector', st.session_state['sectors'].values())
        sector_key = use_dict.find_key(st.session_state['sectors'], sector)
        return sector_key
    return ''
    
def select_building(sector_key: str) -> int:
    if 'place_info' in st.session_state:
        if len(st.session_state['place_info'][sector_key]) > 1:
            building_list = st.session_state['place_info'][sector_key][1]
            building_name = st.selectbox('Select building', sorted(building_list))
            building_idx = building_list.index(building_name)
        return building_idx
    return -1

def select_level(sector_key: str, building_idx: int) -> str:
    if 'place_info' in st.session_state:
        if len(st.session_state['place_info'][sector_key]) > 2:
            levels_list = st.session_state['place_info'][sector_key][2]
            each_level = use_dict.divide_levels(levels_list)
            level_name = st.selectbox('Select level', sorted(each_level[building_idx], key=use_dict.custom_sort_key))
        return level_name
    return ""


@st.cache_data
def get_current_time_and_json(): 
    with st.columns(1)[0]:
        st.header("Current Time")

        user_time_str = "2023-07-08 03:49:41.695820"

        # 문자열을 datetime 객체로 변환
        seoul_timezone = pytz.timezone('Asia/Seoul')
        user_time = datetime.strptime(user_time_str, '%Y-%m-%d %H:%M:%S.%f')
        user_time = seoul_timezone.localize(user_time)

        # 시간을 문자열로 변환
        user_time_str_formatted = user_time.isoformat()
        # current_time_str = datetime.now(tz=pytz.timezone('Asia/Seoul')).isoformat()
        # datetime_obj = datetime.strptime(current_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        # formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M')
        st.markdown(f"<span style='font-size: 40px;'>{user_time_str_formatted}</span>", unsafe_allow_html=True)
       
        current_time_json = json.dumps(user_time_str_formatted)

        if 'yesterday_date' not in st.session_state:
            st.session_state['yesterday_date'] = current_time_json

    return current_time_json, user_time_str_formatted

@st.cache_data
def get_yesterday_userinfos(current_time_json):
    if 'yesterday_date' in st.session_state:
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
        
# @st.cache_data
# # *** 요기에 모든 성능 지표 전날 거 업데이트 되게 위치해야 함 
# def save_yesterday_data(current_time_json):
#     if 'users' in st.session_state:
#         data = {'start_time': current_time_json, 'user_id': st.session_state['users'], 'device_model': st.session_state['devices']}
#         status_code = data_requests.request_updated_postition_err_dist(data)
#         if status_code == 200:
#             st.success('Updated until yesterday stats')

def load_webpage(current_time_json, current_time_str):
    perf_1, _, _, _, _ = st.columns([1,1,1,1,1])
    loc_diff, first_fix = st.columns([1, 1])
   
    # with perf_1:
    #     data = {'sector_id': 6, 'start_time': starttime_json_data, 'end_time': endtime_json_data}
    #     userID = requests.get("http://localhost:8502/api", data=json.dumps(data))
    #     st.session_state['yesterday_date']

    # chart_data, loaded_data = None, None
    # with loc_diff:
    #     data = {'end_time': current_time_json}
    #     daily_datas = data_requests.request_whole_performance_stats(data)
    #     if daily_datas != None:    
    #         loaded_data = [0]*30
    #         for idx, daily_data in enumerate(daily_datas):
    #             loaded_data[idx] = daily_data["total_data"]
    #         # chart_data, loaded_data = plot_charts.plot_stacked_bar_chart(daily_datas)
    #         plt = plot_charts.plot_cumulative_bar_chart(daily_datas, loaded_data)
    #         st.pyplot(plt)

    with first_fix:
        if 'users' in st.session_state:
            data = {'start_time': current_time_str, 'user_id': st.session_state['users'], 'device_model': st.session_state['devices']}
            # 'end_time'으로 현재 시간 넘겨주는 경우 바꿔주기
            ttff = data_requests.request_time_to_first_fix(data)



if __name__ == '__main__' :
    # set_page_title()
    # load_performance_tables()
    # set_performance_sidebar()
    # get_place_datas()
    # extract_sectors()
    # set_place_selection()
    current_time_json, current_time_str = get_current_time_and_json()
    print(current_time_json, current_time_str )
    get_yesterday_userinfos(current_time_json)
    # save_yesterday_data(current_time_json)
    load_webpage(current_time_json, current_time_str)