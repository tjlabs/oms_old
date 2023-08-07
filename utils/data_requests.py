from tkinter import S
import requests, json
import streamlit as st
from modules.manage_db.where_db import postgres, place_info, position_err_dist, first_fix
from modules.manage_db.stats_db import statsdb
from models import models
import numpy as np

DBConn = postgres.DBConnection()
StatsDBConn = statsdb.StatsDBConnection()

def request_performance_indicators():
    return StatsDBConn.get_tables()
    
def request_place_info() -> dict:
    place = place_info.PlaceInfo(DBConn)
    return place.get_place_info()

# ** DBConn을 넘겨받지 않고도 그냥 전역변수로도 사용이 가능한 이유에 대해 생각해보기
def request_yesterday_whole_users(start_time: str, end_time: str):
    user_ids, device_models = DBConn.select_userids_and_device_models(6, start_time, end_time)
    total_count = DBConn.count_mobile_results(6, start_time, end_time)
    return user_ids, device_models, total_count

def check_yesterday_stats(table_name: str, start_time: str):
    exists = StatsDBConn.check_yesterday_stats_exists(table_name, start_time)
    return exists

def update_postition_err_dist(data: dict, start_time: str, end_time: str) -> None:
    indicator = position_err_dist.PositioningErrorDistance(DBConn, data['sector_id'], start_time, end_time, data['user_id'], data['device_model'])
    one_day_trajectory = indicator.get_positiong_error_distance()
    StatsDBConn.insert_position_err_stats(one_day_trajectory)
    return

def position_err_dist_stats(end_date: str) -> np.ndarray:
    position_err_stats = StatsDBConn.get_position_err_dist_stats(end_date)
    return np.array(position_err_stats)

def TTFF_stats(end_date: str) -> tuple:
    time_to_first_fix_stats = StatsDBConn.get_TTFF(end_date)
    return time_to_first_fix_stats

    
def update_time_to_first_fix(data: dict, start_time: str, end_time: str) -> None:
    indicator = first_fix.TimeToFirstFix(DBConn, data['sector_id'], start_time, end_time, data['user_id'])
    stabilization_info = indicator.get_phase_one_to_four_time()
    StatsDBConn.insert_TTFF_stats(stabilization_info)
    return

    
if __name__ == '__main__':
    0