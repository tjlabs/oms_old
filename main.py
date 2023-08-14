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
    total_count = basic_setting.count_mobile_results(db_conn, 6, start_time, end_time)

    one_day_whole_test_sets = []

    for user in users:
        user_whole_testsets = basic_setting.query_one_day_data(db_conn, user, start_time, end_time)
        one_day_whole_test_sets.append(user_whole_testsets)

    is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'location_difference', end_time)
    if is_updated == False:
        one_day_trajectory = position_err_dist.get_positiong_error_distance(db_conn, one_day_whole_test_sets, 6, end_time)
        get_stats.insert_position_err_stats(stats_DB_conn, one_day_trajectory)
        
    is_updated = get_stats.check_yesterday_stats_exists(stats_DB_conn, 'time_to_first_fix', end_time)
    if is_updated == False:

        daily_ttff, daily_cnt = first_fix.calculate_time_to_first_fix(db_conn, one_day_whole_test_sets, 24)
        hour_ttff, daily_cnt = first_fix.calculate_time_to_first_fix(db_conn, one_day_whole_test_sets, 1)

        stabilization_info = models.TimeToFirstFix(
            sector_id=6,
            calc_date=start_time,
            avg_stabilization_time=daily_ttff/daily_cnt,
            hour_unit_ttff=first_fix.average_hour_unit_data(hour_ttff, daily_cnt),
            user_count=daily_cnt
        )

        get_stats.insert_TTFF_stats(stats_DB_conn, stabilization_info)
        st.success('Updated until yesterday stats')

def load_webpage(utc_time: datetime):
    ped, ttff = st.columns([1]), st.columns([1])

    with ped[0]:
        daily_ped_datas = get_stats.get_position_err_dist_stats(stats_DB_conn, utc_time)
        _, day = st.columns([4, 2])
        dates = day.radio('', ('7days', '14days', '30days'), key='LD', horizontal=True)
        if len(daily_ped_datas) == 11  and dates != None:
            date = int(dates[:-4])
            daily_ped_datas = np.array(daily_ped_datas)[:11]
            plot_charts.plot_position_loc_stats(daily_ped_datas)

    with ttff[0]:
        daily_tf_datas = None        
        daily_tf_datas = get_stats.get_TTFF(stats_DB_conn, utc_time)
        _, day = st.columns([4, 2])
        dates = day.radio('', ('7days', '14days', '30days'), key='TTFF', horizontal=True)
        if len(daily_tf_datas) == 8 and dates != None:
            date = int(dates[:-4])
            daily_tf_datas = daily_tf_datas[:8]
            plot_charts.ttff_line_chart(daily_tf_datas)




def get_ttff(user_id, start_time, end_time):
    unit_ttff, unit_cnt = 0.0, 0.0
    exists = first_fix.check_phase_four_exists(db_conn, user_id, start_time, end_time)
    if not exists:
        return "X"
    test_sets = basic_setting.query_one_day_data(db_conn, user_id, start_time, end_time)
    phase_one_time = test_sets.test_sets[0].start_time
    phase_four_time = first_fix.get_phase_four_time(db_conn, start_time, end_time, user_id)
    return first_fix.calculate_ttff(phase_one_time, phase_four_time)

if __name__ == '__main__' :
    # set_page_title()
    # place_info = get_place_datas()
    # sector = extract_sectors(place_info)
    # sector_key = set_place_selection(place_info, sector)
    # start_time, end_time = get_current_time_and_json()
    # # save_until_yesterday_data(end_time, sector_key)
    # load_webpage(end_time)

    android_devices = ["s20u", "s20", "s22", "a53"]
    ios_devices = ["iPhone13Pro", "iPhone12Pro", "iPhone12mini", "iPhoneX"]
    android_timestamps = [
        (datetime(2023, 8, 14, 11, 26, tzinfo=ZoneInfo('Asia/Seoul')),datetime(2023, 8, 14, 11, 48, tzinfo=ZoneInfo('Asia/Seoul'))),
        (datetime(2023, 8, 14, 11, 47, tzinfo=ZoneInfo('Asia/Seoul')),datetime(2023, 8, 14, 11, 50, tzinfo=ZoneInfo('Asia/Seoul'))),
        (datetime(2023, 8, 14, 11, 50, tzinfo=ZoneInfo('Asia/Seoul')),datetime(2023, 8, 14, 11, 52, tzinfo=ZoneInfo('Asia/Seoul'))),
    ]
    ios_timestamps = [
        (datetime(2023, 8, 14, 10, 30, tzinfo=ZoneInfo('Asia/Seoul')),datetime(2023, 8, 14, 10, 50, tzinfo=ZoneInfo('Asia/Seoul'))),
        (datetime(2023, 8, 14, 10, 51, tzinfo=ZoneInfo('Asia/Seoul')),datetime(2023, 8, 14, 10, 53, 10, tzinfo=ZoneInfo('Asia/Seoul'))),
        (datetime(2023, 8, 14, 10, 53, 10, tzinfo=ZoneInfo('Asia/Seoul')),datetime(2023, 8, 14, 10, 58, tzinfo=ZoneInfo('Asia/Seoul'))),
    ]
    for android_device in android_devices:
        for i in range(3):
            res = get_ttff(android_device, android_timestamps[i][0], android_timestamps[i][1])
            print(f"{android_device} in test {i}: {res}")
    for ios_device in ios_devices:
        for i in range(3):
            res = get_ttff(ios_device, ios_timestamps[i][0], ios_timestamps[i][1])
            print(f"{ios_device} in test {i}: {res}")    

    


    # desired_hour = 2  # 시
    # desired_minute = 0  # 분
    # desired_second = 0  # 초

    # # 현재 날짜와 시간을 가져옵니다.
    # current_time = datetime.now()

    # # 원하는 시간을 설정합니다.
    # start_time = current_time.replace(hour=desired_hour, minute=desired_minute, second=desired_second)


    # desired_hour = 3  # 시
    # desired_minute = 0  # 분
    # desired_second = 0  # 초

    # # 현재 날짜와 시간을 가져옵니다.
    # current_time = datetime.now()

    # # 원하는 시간을 설정합니다.
    # end_time = current_time.replace(hour=desired_hour, minute=desired_minute, second=desired_second)

    # users = basic_setting.select_user_ids(db_conn, 6, start_time, end_time)


    # one_day_whole_test_sets = []

    # for user in users:
    #     if user != 's20u':
    #         continue
    #     total_count = basic_setting.count_mobile_results(db_conn, 6, user, start_time, end_time)
        # user_whole_testsets = basic_setting.query_one_day_data(db_conn, user, start_time, end_time)
        # one_day_whole_test_sets.append(user_whole_testsets)




    # del one_day_whole_test_sets[6].test_sets[0]
    

        # daily_ttff, daily_cnt = first_fix.calculate_time_to_first_fix(db_conn, one_day_whole_test_sets, user, 24)
        # hour_ttff, daily_cnt = first_fix.calculate_time_to_first_fix(db_conn, one_day_whole_test_sets, user, 1)

        # stabilization_info = models.TimeToFirstFix(
        #     sector_id=6,
        #     calc_date=start_time,
        #     avg_stabilization_time=daily_ttff/daily_cnt,
        #     hour_unit_ttff=first_fix.average_hour_unit_data(hour_ttff, daily_cnt),
        #     user_count=daily_cnt
        # )

    # get_stats.insert_TTFF_stats(stats_DB_conn, stabilization_info)




