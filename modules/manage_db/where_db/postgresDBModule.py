from utils import config
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
        self.cursor = self.connection_pool.getconn().cursor()

    def get_db_connection(self):
        return self.connection_pool.getconn()

    def put_db_connection(self, conn):
        self.connection_pool.putconn(conn)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row
    
    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        rows = self.cursor.fetchall()
        return rows
    
    def commit(self):
        self.cursor.commit()
    




                




    





