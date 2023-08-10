from modules.manage_db.where_db import basic_setting, position_err_dist, first_fix, postgresDBModule
from modules.manage_db.stats_db import statsdb

db_conn = postgresDBModule.DBConnection()
stats_DB_conn = statsdb.StatsDBConnection()

def request_yesterday_whole_users(start_time: str, end_time: str):
    user_ids = basic_setting.select_user_ids(db_conn, 6, start_time, end_time)
    total_count = basic_setting.count_mobile_results(db_conn, 6, start_time, end_time)
    return user_ids, total_count

def update_postition_err_dist(user_ids: list, start_time: str, end_time: str, sector_id: str) -> None:
    one_day_trajectory = position_err_dist.get_positiong_error_distance(db_conn, user_ids, int(sector_id), start_time, end_time)
    stats_DB_conn.insert_position_err_stats(one_day_trajectory)
    return

def update_time_to_first_fix(user_ids: list[str], start_time: str, end_time: str, sector_id: str) -> None:
    stabilization_info = first_fix.get_phase_one_to_four_time(db_conn, user_ids, start_time, end_time, int(sector_id))
    stats_DB_conn.insert_TTFF_stats(stabilization_info)
    return
