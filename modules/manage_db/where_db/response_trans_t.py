from datetime import timedelta
from datetime import datetime

def avg_on_minute(whole_calc_times: tuple, interval: int):
    prev_time = datetime.now()
    total_calc_time = timedelta()
    unit_data = []
    cnt = 0
    min_log_calc_time = [timedelta()]*24*(60//interval)
    interval_str: str = ""

    total_seconds = set_interval(interval)
    for idx, calc_time in enumerate(whole_calc_times):
        if idx == 0:
            interval_str = set_compare_element(total_seconds, calc_time)
            total_calc_time += calc_time[1]
            prev_time = calc_time[0]
            continue

        if interval_str == 'hour':
            if prev_time.hour != calc_time[0].hour or idx == len(whole_calc_times)-1:
                # 95,90분위수 저장
                average_timedelta = total_calc_time // cnt
                min_log_calc_time[prev_time.hour] = average_timedelta
                total_calc_time = timedelta()
                cnt = 0
        elif interval_str == 'minute':
            if prev_time.minute != calc_time[0].minute:
                average_timedelta = total_calc_time // cnt
                min_log_calc_time[calc_time[0].hour*60 + calc_time[0].minute] = average_timedelta
                total_calc_time = timedelta()
                cnt = 0
        elif idx == len(whole_calc_times)-1:
            min_log_calc_time.append(total_calc_time // cnt)

        unit_data.append(calc_time[0])
        prev_time = calc_time[0]
        total_calc_time += calc_time[1]
        cnt += 1

    return min_log_calc_time

def set_interval(interval: int) -> float:
    time_interval = timedelta(minutes=interval)
    return time_interval.total_seconds()

def set_compare_element(total_seconds: float, calc_time: tuple) -> str:
    if total_seconds == 3600:
        return 'hour'
    elif total_seconds == 60:
        return 'minute'
    else:
        return 'day'

