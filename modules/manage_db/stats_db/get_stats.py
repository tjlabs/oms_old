from modules.manage_db.stats_db.statsdb import StatsDBConnection
from datetime import datetime
from models import models

def get_tables(stats_DB_conn: StatsDBConnection) -> list:
    SELECT_QUERY = """SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'"""
    
    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY)
            tuple_tables = cur.fetchall()
    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        stats_DB_conn.put_stats_connection(conn)

    table_list = []

    for tuple_table in tuple_tables:
        table_list.append(tuple_table[0])

    return table_list

def delete_row(stats_DB_conn: StatsDBConnection, id: int):
    DELETE_QUERY =  """DELETE FROM location_tracking_time WHERE id = %s"""

    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(DELETE_QUERY, (id,))
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        conn.commit()
        stats_DB_conn.put_stats_connection(conn)

def update_row(stats_DB_conn: StatsDBConnection, date: models.PositionTrajectory, id: int):
    UPDATE_QUERY =  """UPDATE test_location_difference
                    SET calc_data_num = %s, threshold_010 = %s, threshold_030 = %s, threshold_050 = %s
                    WHERE id = %s"""

    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(UPDATE_QUERY, (date.one_day_stat.user_data_cnt, date.one_day_stat.threshold_10, date.one_day_stat.threshold_30, date.one_day_stat.threshold_50, id,))
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        conn.commit()
        stats_DB_conn.put_stats_connection(conn)


def check_yesterday_stats_exists(stats_DB_conn: StatsDBConnection, table_name: str, end_time: datetime) -> bool:
    EXIST_QUERY = """SELECT EXISTS (SELECT calc_date
                    FROM {}
                    WHERE calc_date=%s
                    ) AS exists_flag"""
    
    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(EXIST_QUERY.format(table_name), (end_time,))
            exists = cur.fetchone()[0]
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        stats_DB_conn.put_stats_connection(conn)

    return exists

def insert_position_err_stats(stats_DB_conn: StatsDBConnection, one_day_trajectory: models.PositionTrajectory):
    INSERT_QUERY = """INSERT INTO location_difference (sector_id, calc_date, calc_data_num,
                    threshold_10, threshold_30, threshold_50) VALUES (%s, %s, %s, %s, %s, %s) """

    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(INSERT_QUERY, (one_day_trajectory.sector_id, one_day_trajectory.calc_date,
                                        one_day_trajectory.one_day_data_cnt, one_day_trajectory.one_day_stat.threshold_10,
                                        one_day_trajectory.one_day_stat.threshold_30, one_day_trajectory.one_day_stat.threshold_50, ))
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        conn.commit()
        stats_DB_conn.put_stats_connection(conn)

    return 

def get_position_err_dist_stats(stats_DB_conn: StatsDBConnection, calc_date: datetime) -> tuple:
    SELECT_QUERY = """ SELECT calc_date, calc_data_num, threshold_10, threshold_30, threshold_50
                        FROM location_difference
                        WHERE calc_date < %s
                        ORDER BY calc_date DESC
                        LIMIT 30"""
                    
    conn = stats_DB_conn.get_stats_connection()
    result_list = []

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (calc_date, ))
            daily_stats = cur.fetchall()
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        stats_DB_conn.put_stats_connection(conn)

    for stat in daily_stats:
        result_list.append(stat)

    return daily_stats

def get_ttff(stats_DB_conn: StatsDBConnection, calc_date: datetime) -> tuple:
    SELECT_QUERY = """ SELECT calc_date, daily_avg_ttff, hour_unit_ttff, users_count
                        FROM time_to_first_fix
                        WHERE calc_date < %s
                        ORDER BY calc_date DESC
                        LIMIT 30"""
    
    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (calc_date, ))
            daily_stats = cur.fetchall()
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        stats_DB_conn.put_stats_connection(conn)

    return daily_stats

def get_ltt(stats_DB_conn, calc_date: datetime):
    SELECT_QUERY = """ SELECT calc_date, avg_loc_track_time, quantile_50th, quantile_90th, quantile_95th
                        FROM location_tracking_time
                        WHERE calc_date < %s
                        ORDER BY calc_date DESC
                        LIMIT 30"""
    
    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (calc_date, ))
            daily_ltt_stats = cur.fetchall()
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        stats_DB_conn.put_stats_connection(conn)

    return daily_ltt_stats

def insert_ttff_stats(stats_DB_conn: StatsDBConnection, stabilization_info: models.TimeToFirstFix):
    INSERT_QUERY = """INSERT INTO time_to_first_fix (sector_id, calc_date, daily_avg_ttff,
                    hour_unit_ttff, users_count) VALUES (%s, %s, %s, %s, %s) """

    conn = stats_DB_conn.get_stats_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(INSERT_QUERY, (stabilization_info.sector_id, stabilization_info.calc_date,
                                        stabilization_info.avg_stabilization_time, stabilization_info.hour_unit_ttff, 
                                        stabilization_info.user_count, ))
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        conn.commit()
        stats_DB_conn.put_stats_connection(conn)

    return 

def insert_loc_track_time_stats(stats_DB_conn: StatsDBConnection, quantile_stats: models.LocationTrackingTime):
    INSERT_QUERY = """INSERT INTO location_tracking_time (calc_date, avg_loc_track_time, quantile_50th, quantile_90th, quantile_95th)
                    VALUES (%s, %s, %s, %s, %s) """
    conn = stats_DB_conn.get_stats_connection()
                                       
    try:
        with conn.cursor() as cur:
            cur.execute(INSERT_QUERY, (quantile_stats.calc_date, quantile_stats.avg_loc_track_time, quantile_stats.quantile_50th, quantile_stats.quantile_90th, quantile_stats.quantile_95th,))
    except Exception as error:
        raise Exception (f"error while checking tables: {error}")
    finally:
        conn.commit()
        stats_DB_conn.put_stats_connection(conn)

    return 