from models import models
from modules.calculation import calculate
from modules.manage_db.where_db import postgresDBModule
from datetime import datetime
    
def get_positiong_error_distance(db_conn: postgresDBModule.DBConnection, one_day_whole_test_sets: list, start_time: datetime) -> models.PositionTrajectory:
    oneday_whole_user_datas: list[models.OneUserPositionErrTable] = []
    one_day_whole_data_cnt = 0

    for test in one_day_whole_test_sets:
        for set in test.test_sets:
            whole_coords = get_user_whole_coords(db_conn, 6, test.user_id, set.start_time, set.end_time)
            filtered_testsets = filter_indoor(whole_coords)
            for filtered_testset in filtered_testsets:
                diff_dist = calculate.calc_coord_diff(filtered_testset)

                threshold_err_ratio: models.OneUserPositionErrTable = calculate.calc_err_frequency(diff_dist[2:])
                threshold_err_ratio.user_dist_diff = diff_dist[2:]

                oneday_whole_user_datas.append(threshold_err_ratio)
                one_day_whole_data_cnt += threshold_err_ratio.user_data_cnt

    oneday_position_err_data = calculate.calc_oneday_position_correction(oneday_whole_user_datas)
    one_day_trajectory = models.PositionTrajectory(
        sector_id=6,
        calc_date=start_time,
        one_day_stat=oneday_position_err_data,
        one_day_data_cnt=one_day_whole_data_cnt
    )

    return one_day_trajectory

def filter_indoor(whole_coords: list[models.CoordinatesWithIsindoor]) -> list:
    filtered_testsets = []
    one_test = []
    get_start = False
    for idx, coord in enumerate(whole_coords):
        if coord.is_indoor == False and get_start == True:
            filtered_testsets.append(one_test)
            one_test = []
            get_start = False
            continue
        if coord.is_indoor == False:
            continue
        one_test.append(coord)
        get_start = True

        if idx == len(whole_coords)-1 and get_start == True:
            filtered_testsets.append(one_test)

    return filtered_testsets


def get_user_whole_coords(db_conn: postgresDBModule.DBConnection, sector_id: int, user_id: str, start_time: datetime, end_time: datetime) -> list:
    SELECT_DEVICE_COORDS = """SELECT mr.x, mr.y, mr.is_indoor, mr.mobile_time FROM mobile_results AS mr
                            WHERE mr.sector_id = %s AND mr.user_id = %s
                            AND mobile_time >= %s AND mobile_time <= %s
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
        whole_coords.append(models.CoordinatesWithIsindoor(x= coord[0], y=coord[1], is_indoor=coord[2], mobile_time=coord[3]))

    return whole_coords

