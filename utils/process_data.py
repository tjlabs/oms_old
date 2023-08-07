from datetime import datetime, timedelta
import numpy as np

def find_key(dict: dict, target: str) -> str:
    for key, value in dict.items():
        if value == target:
            return key
    return ""

def custom_sort_key(item):
    if item[0] == 'B':
        return (-1, item)
    else:
        return (1, item) 
    
def divide_levels(levels_list: list) -> list:
    result_list, temp_list = [], []
    for level in levels_list:
        if level != "":
            temp_list.append(level)
        else:
            if temp_list:
                result_list.append(temp_list)
                temp_list = []
    if temp_list:
        result_list.append(temp_list)
    return result_list

def change_time_format_to_postgresdb(current_utc: str) -> tuple[str, str]:

    if int(current_utc[11:13]) < 15:
        current_utc = current_utc[:8] + str(int(current_utc[9:10])-1).zfill(2) + ' 15:00:00'

    else:
        current_utc = current_utc[:11] + '15:00:00'

    end_time = current_utc

    modified_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S') - timedelta(days=1)
    start_time = modified_dt.strftime('%Y-%m-%d %H:%M:%S')
    return start_time, end_time

def convert_date_format(dates: list) -> list:
        formatted_dates = np.vectorize(lambda x: x.strftime("%m-%d"))(dates)
        converted_dates = [date_str for date_str in formatted_dates]
        return converted_dates

