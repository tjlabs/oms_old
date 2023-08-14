from modules.manage_db.where_db import postgresDBModule
from datetime import datetime
from models import models

def get_place_info(db_conn: postgresDBModule.DBConnection) -> dict:
    place_info = get_sectors(db_conn)
    place_info = get_buildings(place_info, db_conn)
    place_info = get_levels(place_info, db_conn)
    return place_info

def get_sectors(db_conn) -> dict:
    place_info = {}
    SELECT_QUERY = """SELECT id, name FROM sectors
                    ORDER BY id"""
    conn = db_conn.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY)
            tuple_sectors = cur.fetchall()
    except Exception as error:
        raise Exception (f"select parameter Error : {error}")
    finally:
        db_conn.put_db_connection(conn)

    for tuple_sector in tuple_sectors:
        place_info[tuple_sector[0]] = [tuple_sector[1]]

    return place_info

def get_buildings(place_info: dict, db_conn: postgresDBModule.DBConnection) -> dict:
    SELECT_QUERY = """SELECT b.sector_id, b.name FROM buildings AS b
                    INNER JOIN sectors AS s
                    ON s.id = b.sector_id
                    ORDER BY s.id"""
    
    conn = db_conn.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY)
            buildings_order_by_sector_id = cur.fetchall()
    except Exception as error:
        raise Exception (f"select parameter Error : {error}")
    finally:
        db_conn.put_db_connection(conn)

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
            place_info[prev_sector_id].append(buildings)
            buildings = []
            buildings.append(tuple_building[1])

        prev_sector_id = tuple_building[0]

    return place_info

def get_levels(place_info: dict, db_conn: postgresDBModule.DBConnection) -> dict:
    SELECT_QUERY = """SELECT b.sector_id, b.id, l.short_name FROM levels AS l
                    INNER JOIN buildings AS b ON b.id = l.building_id
                    INNER JOIN sectors AS s ON s.id = b.sector_id
                    ORDER BY s.id, b.id"""
    
    conn = db_conn.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY)
            levels_order_by_sector_id = cur.fetchall()
    except Exception as error:
        raise Exception (f"select parameter Error : {error}")
    finally:
        db_conn.put_db_connection(conn)

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
            place_info[prev_sector_id].append(levels)
            levels = []
            levels.append(tuple_level[2])

        prev_sector_id = tuple_level[0]
        prev_building_id = tuple_level[1]

    return place_info

def select_user_ids(db_conn: postgresDBModule.DBConnection, sector_id, start_time, end_time) -> list:
    SELECT_QUERY = """SELECT DISTINCT mr.user_id FROM mobile_results AS mr
            WHERE mr.sector_id = %s AND mr.mobile_time >= %s AND mr.mobile_time < %s"""
    
    conn = db_conn.get_db_connection()
    try:
        records = db_conn.executeAll(SELECT_QUERY, (sector_id, start_time, end_time, ))
    except Exception as error:
        raise Exception (f"error while selecting user ids and device models : {error}")
    finally:
        db_conn.put_db_connection(conn)

    user_ids = []

    for record in records:
        user_ids.append(record[0])

    return user_ids

def count_mobile_results(db_conn: postgresDBModule.DBConnection, sector_id, user, start_time, end_time):
    SELECT_QUERY = """SELECT COUNT(*)
                    FROM request_outputs
                    WHERE user_id = %s
                    AND mobile_time >= %s AND mobile_time < %s
                    """
    conn = db_conn.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_QUERY, (user, start_time, end_time, ))
            total_count = cur.fetchone()[0]
    except Exception as error:
        raise Exception (f"error while counting datas : {error}")
    finally:
        db_conn.put_db_connection(conn)

    return total_count

# sector_id 연계해서 언젠간 작성해야 함
def query_one_day_data(db_conn: postgresDBModule.DBConnection, user: str, start_time: datetime, end_time: datetime) -> models.OneuserWholeTestSets:
    SELECT_QUERY = """SELECT mobile_time, index, building_name
                    FROM request_outputs
                    WHERE mobile_time >= %s AND mobile_time < %s
                    AND user_id = %s
                    ORDER BY mobile_time
                    """
    conn = db_conn.get_db_connection()
    try:
        total_mobile_results = db_conn.executeAll(SELECT_QUERY, (start_time, end_time, user, ))
    except Exception as error:
        raise Exception (f"error while counting datas : {error}")
    finally:
        db_conn.put_db_connection(conn)

    if len(total_mobile_results) == 0:
        return  models.OneuserWholeTestSets()
    
    user_whole_testsets = divide_test_sets(list(total_mobile_results), user)

    return user_whole_testsets

def divide_test_sets(total_mobile_results: list, user: str) -> models.OneuserWholeTestSets:
    prev_db_idx: int = total_mobile_results[0][1]
    prev_db_building: str = ""
    user_whole_testsets = models.OneuserWholeTestSets(
        user_id = user
    )
    test = models.TestSet(
        start_time=total_mobile_results[0][0]
    )
    retest = False
    for idx, data in enumerate(total_mobile_results):
        if prev_db_building != "" and data[2] == "" or idx == 0:
            end = data[0]
        if prev_db_building == "" and data[2] != "":
            test = models.TestSet(
                start_time=data[0],
                end_time= end
            )
            user_whole_testsets.test_sets.append(test)
            prev_db_building = str(data[2])

        if int(data[1]) < prev_db_idx:
            test.end_time = total_mobile_results[idx-1][0]
            user_whole_testsets.test_sets.append(test)
            test = models.TestSet(
                    start_time=data[0]
            )
            prev_db_idx = int(data[1])
            prev_db_building = str(data[2])
            retest = True
            continue

        prev_db_idx = int(data[1])
        prev_db_building = str(data[2])

    if retest == False or idx == len(total_mobile_results)-1:
        test.end_time = total_mobile_results[-1][0]
        user_whole_testsets.test_sets.append(test)

    return user_whole_testsets
