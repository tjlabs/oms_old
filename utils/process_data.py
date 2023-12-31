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

def convert_date_format(dates: np.ndarray) -> list:
        formatted_dates = np.vectorize(lambda x: x.strftime("%m-%d"))(dates)
        converted_dates = [date_str for date_str in formatted_dates]
        return converted_dates

