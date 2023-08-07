from utils import config
from psycopg2 import pool
from models import models

class StatsDBConnection:
    def __init__(self):
        self.connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=30,
            host=config.PERFORCHKDB_CONFIG['dbHost'],
            dbname=config.PERFORCHKDB_CONFIG['dbName'],
            user=config.PERFORCHKDB_CONFIG['dbUser'],
            password=config.PERFORCHKDB_CONFIG['dbPassword'],
            port=config.PERFORCHKDB_CONFIG['dbPort']
        )

    def get_stats_connection(self):
        return self.connection_pool.getconn()

    def put_stats_connection(self, conn):
        self.connection_pool.putconn(conn)

    def get_tables(self) -> list:
        SELECT_QUERY = """SELECT table_name FROM information_schema.tables
                        WHERE table_schema = 'public'"""
        
        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY)
                tuple_tables = cur.fetchall()
        except Exception as error:
            raise Exception (f"error while reading tables: {error}")
        finally:
            self.put_stats_connection(conn)

        table_list = []

        for tuple_table in tuple_tables:
            table_list.append(tuple_table[0])

        return table_list
    
    def delete_row(self, id):
        DELETE_QUERY =  """DELETE FROM time_to_first_fix WHERE id = %s"""

        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(DELETE_QUERY, (id,))
        except Exception as error:
            raise Exception (f"error while checking tables: {error}")
        finally:
            conn.commit()
            self.put_stats_connection(conn)

    
    def check_yesterday_stats_exists(self, table_name: str, start_time: str) -> bool:
        EXIST_QUERY = """SELECT EXISTS (SELECT calc_date
                        FROM {}
                        WHERE calc_date=%s
                        ) AS exists_flag"""
        
        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(EXIST_QUERY.format(table_name), (start_time,))
                exists = cur.fetchone()[0]
        except Exception as error:
            raise Exception (f"error while checking tables: {error}")
        finally:
            self.put_stats_connection(conn)

        return exists
    
    def insert_position_err_stats(self, one_day_trajectory: models.PositionTrajectory):
        INSERT_QUERY = """INSERT INTO location_difference (sector_id, calc_date, calc_data_num,
                        threshold_10, threshold_30, threshold_50) VALUES (%s, %s, %s, %s, %s, %s) """

        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(INSERT_QUERY, (one_day_trajectory.sector_id, one_day_trajectory.calc_date,
                                           one_day_trajectory.one_day_stat.user_data_cnt, one_day_trajectory.one_day_stat.threshold_10,
                                            one_day_trajectory.one_day_stat.threshold_30, one_day_trajectory.one_day_stat.threshold_50, ))
        except Exception as error:
            raise Exception (f"error while checking tables: {error}")
        finally:
            conn.commit()
            self.put_stats_connection(conn)

        return 
    
    def get_position_err_dist_stats(self, calc_date) -> tuple:
        SELECT_QUERY = """ SELECT calc_date, calc_data_num, threshold_10, threshold_30, threshold_50
                            FROM location_difference
                            WHERE calc_date < %s
                            ORDER BY calc_date DESC
                            LIMIT 30"""
        
        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY, (calc_date, ))
                daily_stats = cur.fetchall()
        except Exception as error:
            raise Exception (f"error while checking tables: {error}")
        finally:
            self.put_stats_connection(conn)

        return daily_stats
    
    def get_TTFF(self, calc_date: str) -> tuple:
        SELECT_QUERY = """ SELECT calc_date, daily_avg_ttff, hour_unit_ttff, users_count
                            FROM time_to_first_fix
                            WHERE calc_date < %s
                            ORDER BY calc_date DESC
                            LIMIT 30"""
        
        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY, (calc_date, ))
                daily_stats = cur.fetchall()
        except Exception as error:
            raise Exception (f"error while checking tables: {error}")
        finally:
            self.put_stats_connection(conn)

        return daily_stats
    
    def insert_TTFF_stats(self, stabilization_info: models.TimeToFirstFix):
        INSERT_QUERY = """INSERT INTO time_to_first_fix (sector_id, calc_date, daily_avg_ttff,
                        hour_unit_ttff, users_count) VALUES (%s, %s, %s, %s, %s) """

        conn = self.get_stats_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(INSERT_QUERY, (stabilization_info.sector_id, stabilization_info.calc_date,
                                           stabilization_info.avg_stabilization_time, stabilization_info.hour_unit_TTFF,
                                            stabilization_info.user_count, ))
        except Exception as error:
            raise Exception (f"error while checking tables: {error}")
        finally:
            conn.commit()
            self.put_stats_connection(conn)

        return 

if __name__ == '__main__':
    print('statsdb.py')
        
