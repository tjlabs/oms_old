from utils import config
from psycopg2 import pool

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
    