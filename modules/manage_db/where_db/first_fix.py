from datetime import datetime
from models import models
from modules.manage_db.where_db import postgresDBModule

def calculate_time_to_first_fix(db_conn: postgresDBModule.DBConnection, one_day_whole_test_sets: list, start_time: datetime) -> models.TimeToFirstFix:
    unit_ttff, unit_cnt = [0.0]*24, [0.0]*24
    total_ttff, cnt = 0, 0

    if len(one_day_whole_test_sets) == 0:
        return models.TimeToFirstFix()

    for one_user in one_day_whole_test_sets:
        for one_test in one_user.test_sets:
            exists = check_phase_four_exists(db_conn, one_user.user_id, one_test.start_time, one_test.end_time)
            if not exists:
                continue

            phase_four_time = get_phase_four_time(db_conn, one_test.start_time, one_test.end_time, one_user.user_id)
            ttff = calculate_ttff(one_test.start_time, phase_four_time)

            total_ttff += ttff
            cnt += 1

            unit_ttff[one_test.start_time.hour] += ttff
            unit_cnt[one_test.start_time.hour] += 1

    if total_ttff == 0:
        return models.TimeToFirstFix()

    stabilization_info = models.TimeToFirstFix(
        sector_id=6,
        avg_stabilization_time=total_ttff/cnt,
        hour_unit_ttff=average_hour_unit_data(unit_ttff, unit_cnt),
        user_count=cnt
    )

    return stabilization_info

def calculate_ttff(phase_one_time: datetime, phase_four_time: datetime) -> int:
    if phase_four_time is None:
        return 0
    return (phase_four_time -  phase_one_time).seconds

def average_hour_unit_data(hour_unit_ttff: list[float], hour_unit_cnt: list[float]) -> list[float]:
    for idx in range(len(hour_unit_ttff)):
        if hour_unit_cnt[idx] == 0:
            continue
        hour_unit_ttff[idx] = round(hour_unit_ttff[idx] / hour_unit_cnt[idx], 3)
    return hour_unit_ttff

def check_phase_four_exists(db_conn: postgresDBModule.DBConnection, user: str, start_time: datetime, end_time: datetime) -> bool:

    EXISTS_QUERY = """SELECT EXISTS
                    (SELECT 1
                        FROM request_outputs
                        WHERE mobile_time >= %s
                        AND mobile_time <= %s
                        AND user_id = %s
                        AND phase = 4
                    ) AS exists_flag"""
    
    conn = db_conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(EXISTS_QUERY, (start_time, end_time, user, ))
            exists = cur.fetchone()[0]

    except Exception as error:
        db_conn.put_db_connection(conn)
        raise 
    finally:
        db_conn.put_db_connection(conn)

    return exists

def get_phase_four_time(db_conn: postgresDBModule.DBConnection, phase_one_time: datetime, end_time: datetime, user: str) -> datetime:
    SELECT_QUERY = """SELECT mobile_time FROM request_outputs
                    WHERE mobile_time >= %s
                    AND mobile_time <= %s
                    AND user_id = %s
                    AND phase = 4
                    ORDER BY mobile_time
                    LIMIT 1"""
    
    conn = db_conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (phase_one_time, end_time, user, ))
            phase_four_time = cur.fetchone()[0]

    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        db_conn.put_db_connection(conn)

    return phase_four_time