from audioop import avg
from datetime import datetime, timedelta
from models import models

class TimeToFirstFix:
    def __init__(self, DBConn, sector_id, start_time, end_time, users) -> None:
        self.conn = DBConn
        self.start_time = start_time
        self.end_time = end_time
        self.sector_id = sector_id
        self.users = users
        self.total_time: int = 0

    def get_phase_one_to_four_time(self) -> models.TimeToFirstFix:
        hourUnitTTFF: list[int] = [0]*24
        hourUnitCount: list[int] = [0]*24
        not_count = 0

        if len(self.users) == 0:
            return models.TimeToFirstFix(
                calc_date=self.start_time,
            )
        for user in self.users:
            if user == '20230622-0000000000970' or user == '20230622-0000000000978':
                continue
            phase_one_time = self.get_phase_one_time(user)
            exists = self.check_phase_four_exists(user)
            if not exists:
                not_count += 1
                continue
            phase_four_time, phase_four_idx = self.get_phase_four_time(phase_one_time, user)

            TTFF = (phase_four_time -  phase_one_time).seconds

            if TTFF > 480 :
                TTFF = self.update_ttff_length_over_480(phase_four_time, phase_one_time, user, phase_four_idx)
                if TTFF > 480 : 
                    not_count += 1
                    continue

            self.total_time += TTFF

            hourUnitTTFF[phase_one_time.hour] += TTFF
            hourUnitCount[phase_one_time.hour] += 1

        stabilization_info = models.TimeToFirstFix(
            sector_id=self.sector_id,
            calc_date=self.start_time,
            avg_stabilization_time=self.total_time/len(self.users),
            hour_unit_TTFF=self.average_daily_datas(hourUnitCount, hourUnitTTFF),
            user_count=len(self.users)-not_count
        )
        return stabilization_info
    
    def average_daily_datas(self, hourUnitCount, hourUnitTTFF):
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