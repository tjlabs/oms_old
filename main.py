import streamlit as st
from datetime import datetime, timedelta
from utils import process_data
from modules.manage_db.stats_db import statsdb, get_stats
from modules.manage_db.where_db import basic_setting, postgresDBModule, position_err_dist, first_fix
from models import models
from modules.plot import plot_charts
import numpy as np
from zoneinfo import ZoneInfo

db_conn = postgresDBModule.DBConnection()
stats_DB_conn = statsdb.StatsDBConnection()

def set_page_title() -> None:
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                    layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")

@st.cache_data
def get_place_datas() -> dict:
    return basic_setting.get_place_info(db_conn)

@st.cache_data
def extract_sectors(place_info: dict) -> dict:
    sector = {}
    for key, value in place_info.items():
        sector[key] = value[0]
    return sector

def set_place_selection(place_info: dict, sector:dict) -> str:
    with st.container():
        st.write("Place Information")

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
        
    st.divider()
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
def get_current_time_and_json() -> tuple[datetime, datetime]: 
    utc_time = datetime.utcnow()
    today_date = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    start_time, end_time = process_data.change_time_format_to_postgresdb(utc_time)
    return start_time, end_time
        
@st.cache_data
def save_until_yesterday_data(end_time: datetime, sector_key: str):
    start_time = end_time - timedelta(days=1)
    users = basic_setting.select_user_ids(db_conn, 6, start_time, end_time)

    one_day_whole_test_sets = []

    for user in users:
        user_whole_testsets = basic_setting.get_whole_request_output_data(db_conn, user, start_time, end_time)
        one_day_whole_test_sets.append(user_whole_testsets)

    is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'location_difference', end_time)
    if is_updated == False:
        one_day_trajectory = position_err_dist.get_positiong_error_distance(db_conn, one_day_whole_test_sets, 6, end_time)
        get_stats.insert_position_err_stats(stats_DB_conn, one_day_trajectory)
        
    is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'time_to_first_fix', end_time)
    if is_updated == False:
        time_to_first_fix = first_fix.calculate_time_to_first_fix(db_conn, one_day_whole_test_sets)

        get_stats.insert_TTFF_stats(stats_DB_conn, time_to_first_fix)
        st.success('Updated until yesterday stats')

def load_webpage(utc_time: datetime):
    ped, ttff = st.columns([1]), st.columns([1])

    with ped[0]:
        daily_ped_datas = get_stats.get_position_err_dist_stats(stats_DB_conn, utc_time)
        _, day = st.columns([4, 2])
        dates = day.radio('', ('7days', '14days', '30days'), key='LD', horizontal=True)
        if len(daily_ped_datas) == 30  and dates != None:
            date = int(dates[:-4])
            daily_ped_datas = np.array(daily_ped_datas)[:date]
            plot_charts.plot_position_loc_stats(daily_ped_datas)

    with ttff[0]:
        daily_tf_datas = None        
        daily_tf_datas = get_stats.get_TTFF(stats_DB_conn, utc_time)
        _, day = st.columns([4, 2])
        dates = day.radio('', ('7days', '14days', '30days'), key='TTFF', horizontal=True)
        if len(daily_tf_datas) == 11 and dates != None:
            date = int(dates[:-4])
            daily_tf_datas = daily_tf_datas[:date]
            plot_charts.scatter_avg_ttff(daily_tf_datas)

if __name__ == '__main__' :
    set_page_title()
    place_info = get_place_datas()
    sector = extract_sectors(place_info)
    sector_key = set_place_selection(place_info, sector)
    start_time, end_time = get_current_time_and_json()
    # save_until_yesterday_data(end_time, sector_key)
    load_webpage(end_time)
