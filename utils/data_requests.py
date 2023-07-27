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