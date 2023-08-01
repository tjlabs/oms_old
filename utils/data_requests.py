import requests, json

def request_performance_indicators() -> any:
    response_data = requests.get("http://localhost:8502/load-performance-indicators")
    if response_data.status_code == 200:
        return response_data.json()["indicators"]
    else:
        return response_data.raise_for_status()
    
def request_place_info() -> any:
    response_data = requests.get("http://localhost:8502/place-info")
    if response_data.status_code == 200:
        return response_data.json()["placeInfo"]
    else:
        return response_data.raise_for_status()
    
def request_updated_postition_err_dist(data: dict) -> int:
    response_data = requests.get("http://localhost:8502/update-positioning-err-distance", data=json.dumps(data))
    return response_data.status_code

def request_whole_performance_stats(data: dict) -> any:
    response_data = requests.get("http://localhost:8502/whole-performance-statistics", data=json.dumps(data))
    if response_data.status_code == 200:
        return response_data.json()["dailyStatus"]
    else:
        return response_data.raise_for_status()
    
def request_time_to_first_fix(data: dict) -> any:
    response_data = requests.get("http://localhost:8502/time-to-first-fix", data=json.dumps(data))
    print('k1', data, response_data.status_code )
    if response_data.status_code == 200:
        return response_data.json()["TTFF"]
    else:
        return response_data.raise_for_status()