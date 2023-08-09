from modules.manage_db.where_db import postgres, place_info, position_err_dist, first_fix
from modules.manage_db.stats_db import statsdb
import numpy as np

db_conn = postgres.DBConnection()
stats_DB_conn = statsdb.StatsDBConnection()

def request_performance_indicators():
    return stats_DB_conn.get_tables()
    
def request_place_info() -> dict:
    place = place_info.PlaceInfo(db_conn)
    return place.get_place_info()

# ** DBConn을 넘겨받지 않고도 그냥 전역변수로도 사용이 가능한 이유에 대해 생각해보기
def request_yesterday_whole_users(start_time: str, end_time: str):
    user_ids = db_conn.select_user_ids(6, start_time, end_time)
    total_count = db_conn.count_mobile_results(6, start_time, end_time)
    return user_ids, total_count

def check_yesterday_stats(table_name: str, start_time: str):
    exists = stats_DB_conn.check_yesterday_stats_exists(table_name, start_time)
    return exists

def update_postition_err_dist(user_ids: list, start_time: str, end_time: str, sector_id: str) -> None:
    one_day_trajectory = position_err_dist.get_positiong_error_distance(db_conn, user_ids, int(sector_id), start_time, end_time)
    stats_DB_conn.insert_position_err_stats(one_day_trajectory)
    return

def position_err_dist_stats(end_date: str) -> np.ndarray:
    position_err_stats = stats_DB_conn.get_position_err_dist_stats(end_date)
    return np.array(position_err_stats)

def TTFF_stats(end_date: str) -> tuple:
    time_to_first_fix_stats = stats_DB_conn.get_TTFF(end_date)
    return time_to_first_fix_stats

    
def update_time_to_first_fix(user_ids: list[str], start_time: str, end_time: str, sector_id: str) -> None:
    stabilization_info = first_fix.get_phase_one_to_four_time(db_conn, user_ids, start_time, end_time, int(sector_id))
    stats_DB_conn.insert_TTFF_stats(stabilization_info)
    return

    
if __name__ == '__main__':
    0