from models import models
from modules.calculation import calculate
from modules.manage_db.where_db import postgresDBModule
from datetime import datetime, timedelta
    
def get_positiong_error_distance(db_conn: postgresDBModule.DBConnection, user_ids: list, sector_id: int, end_time: datetime) -> models.PositionTrajectory:
    oneday_whole_user_datas: list[models.OneUserPositionErrTable] = []
    start_time = end_time - timedelta(days=1)

    for _, user_id in enumerate(user_ids):
        whole_coords = get_user_whole_coords(db_conn, sector_id, user_id, start_time, end_time, )
        diff_dist = calculate.calc_coord_diff(whole_coords)
        threshold_err_ratio: models.OneUserPositionErrTable = calculate.calc_err_frequency(diff_dist)
        threshold_err_ratio.user_dist_diff = diff_dist

        oneday_whole_user_datas.append(threshold_err_ratio)

    oneday_position_err_data = calculate.calc_oneday_position_correction(oneday_whole_user_datas)
    one_day_trajectory = models.PositionTrajectory(
        sector_id=sector_id,
        calc_date=start_time,
        one_day_stat=oneday_position_err_data
    )

    return one_day_trajectory

def get_user_whole_coords(db_conn: postgresDBModule.DBConnection, sector_id: int, user_id: str, start_time: datetime, end_time: datetime) -> list:
    SELECT_DEVICE_COORDS = """SELECT mr.x, mr.y FROM mobile_results AS mr
                            INNER JOIN levels AS l ON l.short_name = mr.level_name
                            INNER JOIN buildings AS b ON b.id = l.building_id
                            INNER JOIN sectors AS s ON s.id = b.sector_id
                            WHERE s.id = %s AND mr.user_id = %s
                            AND mobile_time >= %s AND mobile_time < %s
                            ORDER BY mr.mobile_time"""
    
    whole_coords = []
    conn = db_conn.get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_DEVICE_COORDS, (sector_id, user_id, start_time, end_time, ))
            db_whole_coords = cur.fetchall()
    except Exception as error:
        raise Exception (f"error while reading tables: {error}")
    finally:
        db_conn.put_db_connection(conn)

    for coord in db_whole_coords:
        whole_coords.append(models.Coordinates(x= coord[0], y=coord[1]))

    return whole_coords

