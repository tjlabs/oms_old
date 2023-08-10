from audioop import avg
from datetime import datetime, timedelta
from models import models
from modules.manage_db.where_db import postgresDBModule

def get_phase_one_to_four_time(db_conn: postgresDBModule.DBConnection, user_ids: list[str], start_time: str, end_time: str, sector_id: int) -> models.TimeToFirstFix:
    hourUnitTTFF: list[int] = [0]*24
    hourUnitCount: list[int] = [0]*24
    not_count, total_time = 0, 0

    if len(user_ids) == 0:
        return models.TimeToFirstFix(
            calc_date=start_time,
        )
    for user in user_ids:
        phase_one_time = get_phase_one_time_in_rq_inpt(db_conn, user, start_time, end_time, sector_id)
        # exists = self.check_phase_four_exists(user)
        # if not exists:
        #     not_count += 1
        #     continue
        phase_four_time = get_phase_four_time_in_rq_out(db_conn, phase_one_time, user, end_time)
        if phase_four_time == datetime(1, 1, 1, 0, 0, 0):
                not_count += 1
                continue

        TTFF = (phase_four_time -  phase_one_time).seconds

        # if TTFF > 480 :
        #     TTFF = self.update_ttff_length_over_480(phase_four_time, phase_one_time, user, phase_four_idx)
        #     if TTFF > 480 : 
        #         not_count += 1
        #         continue

        total_time += TTFF

        hourUnitTTFF[phase_one_time.hour] += TTFF
        hourUnitCount[phase_one_time.hour] += 1

    stabilization_info = models.TimeToFirstFix(
        sector_id=sector_id,
        calc_date=start_time,
        avg_stabilization_time=total_time/(len(user_ids)-not_count),
        hour_unit_TTFF=average_daily_datas(hourUnitCount, hourUnitTTFF),
        user_count=len(user_ids)-not_count
    )
    return stabilization_info

def average_daily_datas(hourUnitCount: list[int], hourUnitTTFF: list[int]):
    for idx in range(24):
        if hourUnitCount[idx] != 0:
            hourUnitTTFF[idx] //= hourUnitCount[idx]
    return hourUnitTTFF


def update_ttff_length_over_480(self, phase_four_time, phase_one_time, user, phase_four_idx):
    phase_one_time = self.reload_phase_one_time(phase_four_time, phase_one_time + timedelta(minutes=7), user, phase_four_idx)
    TTFF = (phase_four_time -  phase_one_time).seconds
    return TTFF

def get_phase_one_time(self, user) -> datetime:
    SELECT_QUERY = """SELECT mobile_time FROM mobile_results
                    WHERE mobile_time >= %s
                    AND mobile_time < %s
                    AND user_id = %s
                    AND sector_id = %s
                    ORDER BY mobile_time, index
                    LIMIT 1"""
    
    conn = self.conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (self.start_time, self.end_time, user, self.sector_id, ))
            phase_one_time = cur.fetchone()[0]
    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        self.conn.put_db_connection(conn)

    return phase_one_time  

def get_phase_one_time_in_rq_inpt(db_conn: postgresDBModule.DBConnection, user: str, start_time: str, end_time: str, sector_id: int) -> datetime:
    SELECT_QUERY = """SELECT mobile_time FROM request_inputs
                    WHERE mobile_time >= %s
                    AND mobile_time < %s
                    AND user_id = %s
                    AND sector_id = %s
                    AND phase = 0
                    ORDER BY mobile_time
                    LIMIT 1"""
    
    conn = db_conn.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (start_time, end_time, user, sector_id, ))
            phase_one_time = cur.fetchone()[0]
    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        db_conn.put_db_connection(conn)

    return phase_one_time


def check_phase_four_exists(self, user) -> bool:

    EXISTS_QUERY = """SELECT EXISTS
                    (SELECT 1
                        FROM mobile_results
                        WHERE mobile_time >= %s
                        AND mobile_time < %s
                        AND user_id = %s
                        AND sector_id = %s
                        AND phase = 4
                    ) AS exists_flag"""
    
    conn = self.conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(EXISTS_QUERY, (self.start_time, self.end_time, user, self.sector_id, ))
            exists = cur.fetchone()[0]

    except Exception as error:
        self.conn.put_db_connection(conn)
        raise 
    finally:
        self.conn.put_db_connection(conn)

    return exists

def reload_phase_one_time(self, phase_four_time, least_phase_one_time, user, phase_four_idx):
    SELECT_QUERY = """SELECT mobile_time FROM mobile_results
            WHERE mobile_time < %s
            AND mobile_time > %s
            AND user_id = %s
            AND sector_id = %s
            AND index < %s
            ORDER BY mobile_time, index 
            LIMIT 1"""
    
    conn = self.conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (phase_four_time, least_phase_one_time, user, self.sector_id, phase_four_idx, ))
            phase_one_time = cur.fetchone()[0]
    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        self.conn.put_db_connection(conn)

    return phase_one_time

def get_phase_four_time(self, phase_one_time: datetime, user) -> tuple[datetime, int]:
    SELECT_QUERY = """SELECT mobile_time, index FROM mobile_results
                    WHERE mobile_time >= %s
                    AND mobile_time < %s
                    AND mobile_time < %s
                    AND user_id = %s
                    AND sector_id = %s
                    AND phase = 4
                    ORDER BY mobile_time, index
                    LIMIT 1"""
    
    conn = self.conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (phase_one_time.strftime('%Y-%m-%d %H:%M:%S'), self.end_time, phase_one_time + timedelta(hours=8), user, self.sector_id, ))
            result = cur.fetchone()
            phase_four_time = result[0]
            phase_four_idx = result[1]

    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        self.conn.put_db_connection(conn)

    return phase_four_time, phase_four_idx

def get_phase_four_time_in_rq_out(db_conn: postgresDBModule.DBConnection, phase_one_time: datetime, user: str, end_time: str) -> datetime:
    SELECT_QUERY = """SELECT mobile_time FROM request_outputs
                    WHERE mobile_time >= %s
                    AND mobile_time < %s
                    AND mobile_time < %s
                    AND user_id = %s
                    AND phase = 4
                    ORDER BY mobile_time, index
                    LIMIT 1"""
    
    conn = db_conn.get_db_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (phase_one_time.strftime('%Y-%m-%d %H:%M:%S'), end_time, phase_one_time + timedelta(hours=8), user, ))
            if cur.fetchone() == None:
                return datetime(1, 1, 1, 0, 0, 0)
            phase_four_time = cur.fetchone()[0]

    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        db_conn.put_db_connection(conn)

    return phase_four_time