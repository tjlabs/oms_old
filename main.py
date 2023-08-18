import streamlit as st
from datetime import datetime, timedelta
from utils import process_data
from modules.manage_db.stats_db import statsdb, get_stats
from modules.manage_db.where_db import basic_setting, postgresDBModule, position_err_dist, first_fix, response_trans_t
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
    current_time_seoul = datetime.now(ZoneInfo('Asia/Seoul'))
    current_time_seoul_zeroed = current_time_seoul.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = current_time_seoul_zeroed - timedelta(days=1)
    return current_time_seoul_zeroed, yesterday
        
@st.cache_data
def save_until_yesterday_data(end_time: datetime, sector_key: str):
    start_time = end_time - timedelta(days=1)
    users = basic_setting.select_user_ids(db_conn, 6, start_time, end_time)

    one_day_whole_test_sets = []
    for user in users:
        total_mobile_results = basic_setting.get_whole_request_data(db_conn, user, start_time, end_time)
        if total_mobile_results == []:
            pass
        one_user_testsets = basic_setting.divide_test_sets(list(total_mobile_results), user)
        one_day_whole_test_sets.append(one_user_testsets)

    # is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'location_difference', end_time)
    # if is_updated == False:
    # one_day_trajectory = position_err_dist.get_positiong_error_distance(db_conn, one_day_whole_test_sets, start_time)
    # get_stats.insert_position_err_stats(stats_DB_conn, one_day_trajectory)
        
    # is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'time_to_first_fix', end_time)
    # if is_updated == False:
    time_to_first_fix = first_fix.calculate_time_to_first_fix(db_conn, one_day_whole_test_sets, start_time)
    time_to_first_fix.calc_date = start_time

    get_stats.insert_ttff_stats(stats_DB_conn, time_to_first_fix)

    # is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'location_tracking_time', end_time)
    # if is_updated == False:
    #     whole_calc_times = basic_setting.get_whole_calc_time(db_conn, start_time, end_time)
    #     quantile_stats = response_trans_t.avg_on_minute(whole_calc_times, 1)
    #     day_log_calc_time = response_trans_t.avg_day(whole_calc_times)
    #     quantile_stats.avg_loc_track_time = day_log_calc_time
    #     quantile_stats.calc_date = start_time

    #     get_stats.insert_loc_track_time_stats(stats_DB_conn, quantile_stats)
    #     st.success('Updated until yesterday stats')

def load_webpage(utc_time: datetime):
    ped, ttff, ltt = st.columns([1]), st.columns([1]), st.columns([1])

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
        daily_tf_datas = get_stats.get_ttff(stats_DB_conn, utc_time)
        _, day = st.columns([4, 2])
        dates = day.radio('', ('7days', '14days', '30days'), key='TTFF', horizontal=True)
        if len(daily_tf_datas) == 30 and dates != None:
            date = int(dates[:-4])
            daily_tf_datas = daily_tf_datas[:date]
            plot_charts.scatter_avg_ttff(daily_tf_datas)

    with ltt[0]:
        daily_ltt_datas = None
        daily_ltt_datas = get_stats.get_ltt(stats_DB_conn, utc_time)
        _, day = st.columns([4, 2])
        dates = day.radio('', ('1days', '7days', '14days', '30days'), key='LTT', horizontal=True)
        if len(daily_ltt_datas) == 30 and dates != None:
            date = int(dates[:-4])
            daily_ltt_datas = daily_ltt_datas[:date]
            if date == 1:
                plot_charts.one_day_ltt(daily_ltt_datas)
            else:
                plot_charts.scatter_avg_ltt(daily_ltt_datas)

if __name__ == '__main__' :
    # set_page_title()
    # place_info = get_place_datas()
    # sector = extract_sectors(place_info)
    # sector_key = set_place_selection(place_info, sector)
    # start_time, end_time = get_current_time_and_json()
    current_time_seoul = datetime.now(ZoneInfo('Asia/Seoul'))
    for i in range(17, 32):
        current_time_seoul_zeroed = current_time_seoul.replace(month= 8, day = i, hour=0, minute=0, second=0, microsecond=0)
        save_until_yesterday_data(current_time_seoul_zeroed, 0)
    # load_webpage(end_time)




    


    
