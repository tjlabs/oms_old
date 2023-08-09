from typing import List
import math
from models import models

def calc_coord_diff(whole_coordinates: list) -> list[float]:
    diff_dist: List[float] = [0.0]
    for idx in range(len(whole_coordinates)-1):
        x1, y1 = float(whole_coordinates[idx].x), float(whole_coordinates[idx].y)
        x2, y2 = float(whole_coordinates[idx+1].x), float(whole_coordinates[idx+1].y)

        diff_dist.append(math.dist((x2, y2), (x1, y1)))
    return diff_dist

def calc_err_frequency(diff_dist: list[float]) -> models.OneUserPositionErrTable:
    if len(diff_dist) == 0:
        return models.OneUserPositionErrTable()
    
    th_50, _ = calc_threshold_err_ratio(diff_dist, 50)
    th_30, _ = calc_threshold_err_ratio(diff_dist, 30)
    th_10, total = calc_threshold_err_ratio(diff_dist, 10)

    perthreshold = models.OneUserPositionErrTable(
        threshold_10=th_10-th_30,
        threshold_30=th_30-th_50,
        threshold_50=th_50,
        user_data_cnt=total
    )

    return perthreshold

def calc_threshold_err_ratio(diff_dist: list[float], threshold: float) -> tuple[float, float]:
    # ** LD에서 통계를 구하는 기준이 현재 total : 변화량이 0이 아닌 애들만 count된 것 
    # 그러니까 수집된 총 데이터 개수랑 다른 것임
    total, cnt = 0.0, 0.0
    for idx, dist in enumerate(diff_dist):
        if diff_dist[idx] == 0 and idx == 0:
            total += 1
            continue
        if dist == 0:
            continue
        if dist >= threshold:
            cnt += 1
        total += 1
    return (cnt/total) * 100, total

def calc_oneday_position_correction(oneday_whole_user_datas: list[models.OneUserPositionErrTable]) -> models.OneUserPositionErrTable:
    oneday_whole_user_dists: list[float] = []
    for one_user_track in oneday_whole_user_datas:
        oneday_whole_user_dists += one_user_track.user_dist_diff
    oneday_position_err_data = calc_err_frequency(oneday_whole_user_dists)
    return oneday_position_err_data
        
    