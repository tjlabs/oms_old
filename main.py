from ast import Tuple
import select
import streamlit as st
import time, json, pytz
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from datetime import date, datetime

def set_page_title():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                       layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")
    st.divider()

def set_performance_sidebar():
    response_data = requests.get("http://localhost:8502/load-tables", data=json.dumps(None))
    if response_data.status_code == 200:
        performances = response_data.json()["tables"]
        with st.sidebar:
            st.sidebar.multiselect(
                "Please select the performance metrics you would like to see.",
                performances
            )

def place_info_container():
    with st.container():
        st.header("Selected Place Information")

        current_time, sector, building, level, subcol1, subcol2, subcol3, subcol4 = st.columns([1,1,1,1,1,1,1])
        response_data = requests.get("http://localhost:8502/place-info", data=json.dumps(None))

def show_current_time() : 
    select_time_period = st.columns(1)
    with select_time_period[0]:
        st.header("Current Time")
        current_time_str = datetime.now(tz=pytz.timezone('Asia/Seoul')).isoformat()
        datetime_obj = datetime.strptime(current_time_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M')
        st.markdown(f"<span style='font-size: 40px;'>{formatted_time}</span>", unsafe_allow_html=True)

def get_current_time():
    current_time = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    current_time_json_data = json.dumps(current_time.isoformat())

    if 'yesterday_date' not in st.session_state:
        st.session_state['yesterday_date'] = current_time_json_data

    return current_time_json_data

def get_yesterday_userinfos(current_time_json_data):
    data = {'start_time': current_time_json_data}
    response_data = requests.get("http://localhost:8502/get-yesterday-user", data=json.dumps(data))
    
    if response_data.status_code == 200:
        st.success('Loaded yesterday\'s whole users')
        data = response_data.json()
        
        if 'users' not in st.session_state:
            st.session_state['users'] = data["users"]
        if 'devicemodels' not in st.session_state:
            st.session_state['devicemodels'] = data["devices"]
        if 'total_count' not in st.session_state:
            st.session_state['total_count'] = response_data.json()["totalDataCount"]


def save_yesterday_data(current_time_json_data):
    data = {'start_time': current_time_json_data, 'user_id': st.session_state['users'], 'device_model': st.session_state['devicemodels']}
    response_data = requests.get("http://localhost:8502/save-yesterday", data=json.dumps(data))
    
    if response_data.status_code == 200:
        st.success('Updated until yesterday stats')

def load_webpage(current_time_json_data):
    perf_1, _, _, _, _ = st.columns([1,1,1,1,1])
    placeholder = st.empty()
    chart, line_chart = st.columns([4, 4])
   
    # with perf_1:
    #     data = {'sector_id': 6, 'start_time': starttime_json_data, 'end_time': endtime_json_data}
    #     userID = requests.get("http://localhost:8502/api", data=json.dumps(data))
    #     st.session_state['yesterday_date']


    with placeholder.container():
        chart_data, loaded_data = None, None
        dates = [0]*30
        with chart:
            print("sss", current_time_json_data)
            data = {'end_time': current_time_json_data}
            response_data = requests.get("http://localhost:8502/performance-statistics", data=json.dumps(data))
            if response_data.status_code == 200:
                data = response_data.json()
                daily_datas = data["dailyStatus"]    

                chart_data = np.zeros((30, 4))
                loaded_data = [0]*30
                for idx, daily_data in enumerate(daily_datas):
                    dates[idx] = daily_data["calc_date"][2:10]
                    chart_data[idx][3] = daily_data["threshold_50"]
                    chart_data[idx][2] = daily_data["threshold_30"]
                    chart_data[idx][1] = daily_data["threshold_10"]
                    chart_data[idx][0] = 100.0 - (daily_data["threshold_10"] + daily_data["threshold_30"] + daily_data["threshold_50"])
                    loaded_data[idx] = daily_data["total_data"]

                chart_columns = ["threshold_10", "threshold_30", "threshold_50", "threshold_over_50"]

                chart_data = pd.DataFrame(chart_data, columns=chart_columns, index=dates)
                loaded_data = pd.DataFrame({
                                            'Date' : dates,
                                            'Count': loaded_data
                                            })

                st.bar_chart(data=chart_data, x=None, y=None, width=0, height=500, use_container_width=True)

        with line_chart:
            tab1, tab2 = st.tabs(["Line Chart", "Loaded Data Histogram"])
            with tab1:
                st.header("Line Chart")
                if chart_data != None:
                    st.line_chart(data=chart_data, x=None, y=None, width=0, height=500, use_container_width=True)
            with tab2:
                st.header("Loaded Data Histogram")
                if loaded_data != None:
                    fig = px.histogram(data_frame=loaded_data, x='Date', y='Count', nbins=30, text_auto=True)
                    st.write(fig)

        st.markdown("### Detailed Data View")


if __name__ == '__main__' :
    set_page_title()
    set_performance_sidebar()
    # place_info_container
    show_current_time()
    current_time_json_data = get_current_time()
    get_yesterday_userinfos(current_time_json_data)
    save_yesterday_data(current_time_json_data)
    load_webpage(current_time_json_data)