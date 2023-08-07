from models import models
from modules.calculation import calculate

class PositioningErrorDistance:
    def __init__(self, DBConn, sector_id, start_time, end_time, user_ids, device_models) -> None:
        self.conn = DBConn # ** 뒤에 콤마를 붙이면 튜플로 저장이 됩니다~
        self.sector_id = sector_id
        self.start_time = start_time
        self.end_time = end_time
        self.user_ids = user_ids
        self.device_models = device_models
        self.whole_coords = []
        
    def get_positiong_error_distance(self) -> models.PositionTrajectory:
        oneday_whole_user_datas: list[models.OneUserPositionErrTable] = []
        # ** 이 수치도 지금 1명의 user가 단 1번의 test를 시행했다는 가정에 의해 검출된 통계. 
        # 만약 동일 id를 가진 user가 2회 이상 시스템을 사용했을 때에 대한 분류가 필요
        for idx, user_id in enumerate(self.user_ids):
            self.get_user_whole_coords(self.sector_id, user_id, self.start_time, self.end_time, )
            diff_dist = calculate.calc_coord_diff(self.whole_coords)
            threshold_err_ratio: models.OneUserPositionErrTable = calculate.calc_err_frequency(diff_dist)
            threshold_err_ratio.user_dist_diff = diff_dist

            oneday_whole_user_datas.append(threshold_err_ratio)

        oneday_position_err_data = calculate.calc_oneday_position_correction(oneday_whole_user_datas)
        one_day_trajectory = models.PositionTrajectory(
            sector_id=self.sector_id,
            calc_date=self.start_time,
            one_day_stat=oneday_position_err_data
        )

        return one_day_trajectory

    def get_user_whole_coords(self, sector_id, user_id, start_time, end_time):
        SELECT_DEVICE_COORDS = """SELECT mr.x, mr.y FROM mobile_results AS mr
                                INNER JOIN levels AS l ON l.short_name = mr.level_name
                                INNER JOIN buildings AS b ON b.id = l.building_id
                                INNER JOIN sectors AS s ON s.id = b.sector_id
                                WHERE s.id = %s AND mr.user_id = %s
                                AND mobile_time >= %s AND mobile_time < %s
                                ORDER BY mr.mobile_time"""
        
        conn = self.conn.get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(SELECT_DEVICE_COORDS, (sector_id, user_id, start_time, end_time, ))
                db_whole_coords = cur.fetchall()
        except Exception as error:
            raise Exception (f"error while reading tables: {error}")
        finally:
            self.conn.put_db_connection(conn)

        for coord in db_whole_coords:
            self.whole_coords.append(models.Coordinates(x= coord[0], y=coord[1]))


        return

