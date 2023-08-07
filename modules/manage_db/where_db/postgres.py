from utils import config
import psycopg2, os
from psycopg2 import pool

class DBConnection:
    def __init__(self):
        self.connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=30,
            host=config.WHEREDB_CONFIG['dbHost'],
            dbname=config.WHEREDB_CONFIG['dbName'],
            user=config.WHEREDB_CONFIG['dbUser'],
            password=config.WHEREDB_CONFIG['dbPassword'],
            port=config.WHEREDB_CONFIG['dbPort']
        )

    def get_db_connection(self):
        return self.connection_pool.getconn()

    def put_db_connection(self, conn):
        self.connection_pool.putconn(conn)

    def select_userids_and_device_models(self, sector_id, start_time, end_time):
        SELECT_QUERY = """SELECT DISTINCT mr.user_id, u.device_model FROM mobile_results AS mr
                INNER JOIN users AS u ON u.id = mr.user_id
                INNER JOIN levels AS l ON l.short_name = mr.level_name
                INNER JOIN buildings AS b ON b.id = l.building_id
                INNER JOIN sectors AS s ON s.id = b.sector_id
                WHERE mr.sector_id = %s AND mr.mobile_time >= %s AND mr.mobile_time < %s"""
        
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY, (sector_id, start_time, end_time, ))
                records = cur.fetchall()
        except Exception as error:
            raise Exception (f"error while selecting user ids and device models : {error}")
        finally:
            self.put_db_connection(conn)

        user_ids, device_models = [], []

        for record in records:
            user_ids.append(record[0])
            device_models.append(record[1])

        return user_ids, device_models
    
    def count_mobile_results(self, sector_id, start_time, end_time):
        SELECT_QUERY = """SELECT COUNT(*)
                        FROM mobile_results
                        WHERE sector_id = %s
                        AND mobile_time >= %s AND mobile_time <= %s
                        """
        conn = self.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY, (sector_id, start_time, end_time, ))
                total_count = cur.fetchone()[0]
        except Exception as error:
            raise Exception (f"error while counting datas : {error}")
        finally:
            self.put_db_connection(conn)

        return total_count
    




                




    





