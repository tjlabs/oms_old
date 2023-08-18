from datetime import timedelta
import numpy as np
from models import models
from collections import defaultdict

def avg_on_minute(whole_calc_times: tuple, interval: int):
    first_time, unit_data = None, []
    total_calc_time, cnt = timedelta(), 0
    quantile_stats = models.LocationTrackingTime()
    min_log_calc_time = [timedelta]*(1440//interval)

    for idx, calc_time in enumerate(whole_calc_times):
        if first_time == None:
            first_time = calc_time[0]
            unit_data.append(calc_time[1])
            total_calc_time += calc_time[1]
            cnt += 1
            continue

        if abs(first_time.minute - calc_time[0].minute) >= interval or idx == len(whole_calc_times)-1:
            average_timedelta = total_calc_time // cnt
            if first_time.minute not in min_log_calc_time:
                min_log_calc_time[first_time.minute] = average_timedelta.microseconds/1000
            total_calc_time, cnt = timedelta(), 0
            first_time = calc_time[0]
            quantile_stats.quantile_50th.append(np.percentile(unit_data, 50).microseconds/1000)
            quantile_stats.quantile_90th.append(np.percentile(unit_data, 90).microseconds/1000)
            quantile_stats.quantile_95th.append(np.percentile(unit_data, 95).microseconds/1000)

        unit_data.append(calc_time[1])
        total_calc_time += calc_time[1]
        cnt += 1

    quantile_stats.min_avg_ltt = min_log_calc_time
    return quantile_stats

def avg_day(whole_calc_times: tuple):
    total_calc_time, cnt = timedelta(), 0
    for calc_time in whole_calc_times:
        total_calc_time += calc_time[1]
        cnt += 1
    if cnt == 0 :
        return 0.0
    return (total_calc_time / cnt).microseconds/1000

