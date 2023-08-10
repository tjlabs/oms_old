import streamlit as st
from datetime import datetime, timedelta
from utils import data_requests, process_data
from modules.manage_db.stats_db import statsdb
from modules.manage_db.where_db import basic_setting, postgresDBModule
from modules.plot import plot_charts
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt

db_conn = postgresDBModule.DBConnection()
stats_DB_conn = statsdb.StatsDBConnection()

def set_page_title():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                       layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")
    st.divider()

@st.cache_data
def load_performance_tables() -> list:
    return stats_DB_conn.get_tables()

def set_performance_sidebar(table_list: list) -> None:
    with st.sidebar:
        st.sidebar.multiselect(
            "Please select the performance metrics you would like to see.",
            table_list
        )

@st.cache_data
def get_place_datas() -> dict:
    place = basic_setting.PlaceInfo(db_conn)
    return place.get_place_info()

@st.cache_data
def extract_sectors(place_info: dict) -> dict:
    sector = {}
    for key, value in place_info.items():
        sector[key] = value[0]
    return sector

def set_place_selection(place_info: dict, sector:dict) -> str:
    st.header("Place Information")

    command, col1, col2, col3 = st.columns([1,2,2,2])
    sector_key = 1
    with command:
        st.write("Select Place you want to Search")

    with col1:
        sector_key = select_sector(sector)
        if sector_key == '':
            st.selectbox('No sector', ())

    with col2:
        building_idx = select_building(sector_key, place_info)
        if building_idx == -1:
            st.selectbox('No building', ())

    with col3:
        level_name = select_level(sector_key, building_idx, place_info)
        if level_name == "":
            st.selectbox('No level', ())

    return sector_key

def select_sector(sectors: dict) -> str:
    sector = st.selectbox('Select sector', sectors.values())
    if sector != None:
        sector_key = process_data.find_key(sectors, sector)
        return sector_key
    return ""
    
def select_building(sector_key: str, place_info: dict) -> int:
    building_idx = 0
    if len(place_info[sector_key]) > 1:
        building_list = place_info[sector_key][1]
        building_name = st.selectbox('Select building', sorted(building_list))
        building_idx = building_list.index(building_name)
        return building_idx
    return -1

def select_level(sector_key: str, building_idx: int, place_info) -> str:
    if len(place_info[sector_key]) > 2:
        levels_list = place_info[sector_key][2]
        each_level = process_data.divide_levels(levels_list)
        level_name = st.selectbox('Select level', sorted(each_level[building_idx], key=process_data.custom_sort_key))
        return level_name # type: ignore
    return ""

@st.cache_data
def get_current_time_and_json() -> tuple[str, str]: 
    with st.columns(1)[0]:
        st.header("Current Time")
        korea_timezone = timedelta(hours=9)
        utc_time = datetime.utcnow()
        korea_time = utc_time + korea_timezone
        today_date = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    formatted_korea_time = korea_time.strftime('%Y-%m-%d %H:%M:%S')
    st.markdown(f"<span style='font-size: 40px;'>{formatted_korea_time}</span>", unsafe_allow_html=True)
    start_time, end_time = process_data.change_time_format_to_postgresdb(today_date)
    return start_time, end_time
        
@st.cache_data
def save_until_yesterday_data(start_time: str, end_time: str, sector_key: str):
    users, total_count = data_requests.request_yesterday_whole_users(start_time, end_time)

    is_updated = stats_DB_conn.check_yesterday_stats_exists('location_difference', end_time)
    if is_updated == False:
        data_requests.update_postition_err_dist(users, start_time, end_time, sector_key)
    
    is_updated = stats_DB_conn.check_yesterday_stats_exists('time_to_first_fix', end_time)
    if is_updated == False:
        data_requests.update_time_to_first_fix(users, start_time, end_time, sector_key)
        st.success('Updated until yesterday stats')

def load_webpage(end_time: str):
    ped, ttff = st.columns([4,2])

    with ped:
        st.subheader('Position Err Distance Data Chart')
        tab1, tab2 = st.tabs(["One Site", "With Line Chart"])
        daily_ped_datas = None
        daily_ped_datas = np.array(stats_DB_conn.get_position_err_dist_stats(end_time))

        if len(daily_ped_datas) == 30:
            with tab1:
                plot_charts.plot_position_loc_stats(daily_ped_datas)

            with tab2:
                plot_charts.plot_pos_err_one_site(daily_ped_datas, height=500)


    with ttff:
        st.subheader('Time To First Fix Data Chart')
        daily_tf_datas = None        
        daily_tf_datas = stats_DB_conn.get_TTFF(end_time)

        if len(daily_tf_datas) == 30:
            plot_charts.ttff_line_chart(daily_tf_datas)


if __name__ == '__main__' :
    set_page_title()
    table_list = load_performance_tables()
    set_performance_sidebar(table_list)
    place_info = get_place_datas()
    sector = extract_sectors(place_info)
    sector_key = set_place_selection(place_info, sector)
    start_time, end_time = get_current_time_and_json()

    # save_until_yesterday_data(start_time, end_time, sector_key)
    load_webpage(end_time)

