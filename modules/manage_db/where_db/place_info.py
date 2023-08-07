class PlaceInfo:
    def __init__(self, DBConn) -> None:
        self.place_info = {}
        self.conn = DBConn

    def get_place_info(self) -> dict:
        self.get_sectors()
        self.get_buildings()
        self.get_levels()
        return self.place_info

    def get_sectors(self) -> None:
        SELECT_QUERY = """SELECT id, name FROM sectors
                        ORDER BY id"""
        conn = self.conn.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY)
                tuple_sectors = cur.fetchall()
        except Exception as error:
            raise Exception (f"select parameter Error : {error}")
        finally:
            self.conn.put_db_connection(conn)

        for tuple_sector in tuple_sectors:
            self.place_info[tuple_sector[0]] = [tuple_sector[1]]

    def get_buildings(self) -> None:
        SELECT_QUERY = """SELECT b.sector_id, b.name FROM buildings AS b
                        INNER JOIN sectors AS s
                        ON s.id = b.sector_id
                        ORDER BY s.id"""
        
        conn = self.conn.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY)
                buildings_order_by_sector_id = cur.fetchall()
        except Exception as error:
            raise Exception (f"select parameter Error : {error}")
        finally:
            self.conn.put_db_connection(conn)

        buildings = []
        prev_sector_id = 0
        for idx, tuple_building in enumerate(buildings_order_by_sector_id):
            if idx == 0:
                prev_sector_id = tuple_building[0]
                buildings.append(tuple_building[1])
                continue

            if tuple_building[0] == prev_sector_id:
                buildings.append(tuple_building[1])
            else:
                self.place_info[prev_sector_id].append(buildings)
                buildings = []
                buildings.append(tuple_building[1])

            prev_sector_id = tuple_building[0]
    
    def get_levels(self) -> None:
        SELECT_QUERY = """SELECT b.sector_id, b.id, l.short_name FROM levels AS l
                        INNER JOIN buildings AS b ON b.id = l.building_id
                        INNER JOIN sectors AS s ON s.id = b.sector_id
                        ORDER BY s.id, b.id"""
        
        conn = self.conn.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_QUERY)
                levels_order_by_sector_id = cur.fetchall()
        except Exception as error:
            raise Exception (f"select parameter Error : {error}")
        finally:
            self.conn.put_db_connection(conn)

        levels = []
        prev_sector_id, prev_building_id = 0, 0
        for idx, tuple_level in enumerate(levels_order_by_sector_id):
            if idx == 0:
                prev_sector_id, prev_building_id = tuple_level[0], tuple_level[1]
                levels.append(tuple_level[2])
                continue

            if tuple_level[0] == prev_sector_id:
                if tuple_level[1] == prev_building_id:
                    levels.append(tuple_level[2])
                else:
                    levels.append("")
            else:
                self.place_info[prev_sector_id].append(levels)
                levels = []
                levels.append(tuple_level[2])

            prev_sector_id = tuple_level[0]
            prev_building_id = tuple_level[1]
