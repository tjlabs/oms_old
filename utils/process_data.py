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

def change_time_format_to_postgresdb(utc_time: datetime) -> tuple[datetime, datetime]:

    if utc_time.hour < 15:
        utc_time -= timedelta(days=1)
        end_time = utc_time.replace(hour=15, minute=0, second=0)

    else:
        end_time = utc_time.replace(hour=15, minute=0, second=0)

    start_time = end_time - timedelta(days=1)
    return start_time, end_time

def convert_date_format(dates: np.ndarray) -> list:
        formatted_dates = np.vectorize(lambda x: x.strftime("%m-%d"))(dates)
        converted_dates = [date_str for date_str in formatted_dates]
        return converted_dates

