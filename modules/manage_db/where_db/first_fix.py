from datetime import datetime
from models import models
from modules.manage_db.where_db import postgresDBModule

def calculate_time_to_first_fix(db_conn: postgresDBModule.DBConnection, one_day_whole_test_sets: list, user: str, interval: int) -> tuple[list[float], list[float]]:
    unit_ttff, unit_cnt = [0.0]*int(24/interval), [0.0]*int(24/interval)

    if len(one_day_whole_test_sets) == 0:
        return []

    for one_user in one_day_whole_test_sets:
        for idx, one_test in enumerate(one_user.test_sets):
            if user != one_user.user_id:
                continue

            if idx == 1:
                current_time = datetime.now()
                one_test.start_time = current_time.replace(hour=2, minute=50, second=0)

            exists = check_phase_four_exists(db_conn, one_user.user_id, one_test.start_time, one_test.end_time)
            if not exists:
                continue

            phase_four_time = get_phase_four_time(db_conn, one_test.start_time, one_test.end_time, one_user.user_id)
            ttff = calculate_ttff(one_test.start_time, phase_four_time)

            if interval%24:
                unit_ttff[one_test.start_time.hour] += ttff
                unit_cnt[one_test.start_time.hour] += 1

            else:
                if len(unit_ttff) == 0:
                    unit_ttff.append(ttff)
                    unit_cnt.append(1)
                else:
                    unit_ttff[0] += ttff
                    unit_cnt[0] += 1


    return unit_ttff, unit_cnt

def calculate_ttff(phase_one_time: datetime, phase_four_time: datetime) -> int:
    if phase_four_time is None:
        return "X"
    return (phase_four_time -  phase_one_time).seconds

def average_hour_unit_data(hour_unit_ttff: list[float], hour_unit_cnt: list[int]) -> list[float]:
    for idx in range(len(hour_unit_ttff)):
        if hour_unit_cnt[idx] == 0:
            continue
        hour_unit_ttff[idx] /= hour_unit_cnt[idx]
    return hour_unit_ttff

def check_phase_four_exists(db_conn: postgresDBModule.DBConnection, user: str, start_time: datetime, end_time: datetime) -> bool:

    EXISTS_QUERY = """SELECT EXISTS
                    (SELECT 1
                        FROM request_outputs
                        WHERE mobile_time >= %s
                        AND mobile_time < %s
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
                    AND mobile_time < %s
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