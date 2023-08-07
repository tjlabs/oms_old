import streamlit as st
from datetime import datetime, timedelta
from utils import data_requests, process_data
import pandas as pd
import numpy as np

def set_page_title():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                       layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")
    st.divider()

@st.cache_data
def load_performance_tables():
    if 'performance' not in st.session_state:
        table_list = data_requests.request_performance_indicators()
        st.session_state['performance'] = table_list

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
        place_info = data_requests.request_place_info()
        st.session_state['place_info'] = place_info

@st.cache_data
def extract_sectors():
    if 'place_info' in st.session_state:
        sector = {}
        for key, value in st.session_state['place_info'].items():
            sector[key] = value[0]
        
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
        if 'sector_id' not in st.session_state and sector_key != '':
            st.session_state['sector_id'] = sector_key

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
        sector_key = process_data.find_key(st.session_state['sectors'], sector) # type: ignore
        return sector_key
    return ''
    
def select_building(sector_key: str) -> int:
    building_idx = 0
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
            each_level = process_data.divide_levels(levels_list)
            level_name = st.selectbox('Select level', sorted(each_level[building_idx], key=process_data.custom_sort_key))
        return level_name # type: ignore
    return ""


@st.cache_data
def get_current_time_and_json() -> None: 
    with st.columns(1)[0]:
        st.header("Current Time")
        korea_timezone = timedelta(hours=9)
        utc_time = datetime.utcnow()
        korea_time = utc_time + korea_timezone
        formatted_utc_time = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    formatted_korea_time = korea_time.strftime('%Y-%m-%d %H:%M:%S')
    st.markdown(f"<span style='font-size: 40px;'>{formatted_korea_time}</span>", unsafe_allow_html=True)

    if 'yesterday_date' not in st.session_state:
        st.session_state['yesterday_date'] = formatted_utc_time


@st.cache_data
def get_yesterday_userinfos() -> str:
    if 'yesterday_date' in st.session_state:
        start_time, end_time = process_data.change_time_format_to_postgresdb(st.session_state['yesterday_date'])
        if 'start_time' not in st.session_state and 'end_time' not in st.session_state:
            st.session_state['start_time'] = start_time
            st.session_state['end_time'] = end_time
            
        users, devices, total_count = data_requests.request_yesterday_whole_users(start_time, end_time)

        if users != None:
            st.success('Loaded yesterday\'s whole users')
            
            if 'users' not in st.session_state:
                st.session_state['users'] = users
            if 'devices' not in st.session_state:
                st.session_state['devices'] = devices
            if 'total_data_count' not in st.session_state:
                st.session_state['total_data_count'] = total_count

            return end_time
    return ""
        
@st.cache_data
def save_until_yesterday_data():
    if 'start_time' in st.session_state and 'end_time' in st.session_state:
        if 'users' in st.session_state and 'sector_id' in st.session_state:
            data = {'user_id': st.session_state['users'], 'device_model': st.session_state['devices'], 'sector_id': st.session_state['sector_id']}
            is_updated = data_requests.check_yesterday_stats('location_difference', st.session_state['end_time'])
            if is_updated == False:
                data_requests.update_postition_err_dist(data, st.session_state['start_time'], st.session_state['end_time'])
            
            is_updated = data_requests.check_yesterday_stats('time_to_first_fix', st.session_state['end_time'])    
            if is_updated == False:
                data_requests.update_time_to_first_fix(data, st.session_state['start_time'], st.session_state['end_time'])
   
                st.success('Updated until yesterday stats')

def load_webpage(end_time: str):
    pos_err_diff = st.columns(1)
    
    pp2 = st.columns(1)

    first_fix = st.columns(1)

    chart_data, loaded_data = None, None
    with pos_err_diff[0]:
        daily_ped_datas = None
        if 'end_time' in st.session_state:
        # if end_time != None:
            daily_ped_datas = data_requests.position_err_dist_stats(end_time)
            if len(daily_ped_datas) == 30:
                print('aaaaaaaaaaa')
                # data = {
                #     'Category': ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
                #     'Value 1': [30, 50, 70, 30],
                #     'Value 2': [20, 20, 20, 30],
                #     'Value 3': [20, 20, 0, 0],
                #     'Value 4': [0, 0, 0, 0]
                # }
                # df = pd.DataFrame(data)

                # # DataFrame을 바 차트로 시각화
                # st.subheader("바 차트")
                # st.bar_chart(df.set_index('Category'), use_container_width=True)

            # --------------------------------------------------------------

                dates = daily_ped_datas[:, 0]
                data_cnts = daily_ped_datas[:, 1]
                max_cnt = max(data_cnts)
                bar_heights = [(100*cnt)/max_cnt for cnt in data_cnts]
                print(daily_ped_datas)

                th_10 = []
                for idx, ratio in enumerate(bar_heights):
                    print('1',daily_ped_datas[idx][2:])
                    daily_ped_datas[idx][2:] *= ratio
                    print('2',daily_ped_datas[idx][2:])
                    print('3', ratio-daily_ped_datas[idx][2]-daily_ped_datas[idx][3]-daily_ped_datas[idx][4])
                    th_10.append(ratio-daily_ped_datas[idx][2]-daily_ped_datas[idx][3]-daily_ped_datas[idx][4])

                formatted_dates = np.vectorize(lambda x: x.strftime("%m-%d"))(dates)
                converted_dates = [date_str for date_str in formatted_dates]

                ped_data_frame = pd.DataFrame({
                    'dates': converted_dates,
                    'threshold_10': th_10,
                    'threshold_30': list(daily_ped_datas[:, 2]),
                    'threshold_50': list(daily_ped_datas[:, 3]),
                    'threshold_100': list(daily_ped_datas[:, 4]),
                }) # , columns=['threshold 10', 'threshold 30', 'threshold 50', 'threshold_100'])

                # ped_data_frame['data ratio'] = bar_heights
                st.bar_chart(ped_data_frame.set_index('dates'), height=100, use_container_width=True) #  y=['threshold_10', 'threshold_30', 'threshold_50', 'threshold_100'],


    # with first_fix[0]:
    #     0
        # daily_tf_datas = data_requests.TTFF_stats(st.session_state['end_time'])
        # if 'users' in st.session_state:
        # data = {'start_time': current_utc_for_parsing, 'user_id': st.session_state['users'], 'device_model': st.session_state['devices']}
        # 'end_time'으로 현재 시간 넘겨주는 경우 바꿔주기


if __name__ == '__main__' :
    set_page_title()
    load_performance_tables()
    set_performance_sidebar()
    get_place_datas()
    extract_sectors()
    set_place_selection()
    get_current_time_and_json()

    end_time = get_yesterday_userinfos()
    # save_until_yesterday_data(formatted_utc_time, users, devices)
    load_webpage(end_time)

