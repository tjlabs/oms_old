import streamlit as st
import time, json, pytz
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import altair as alt

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

        time_zone, sector, building, level, subcol1, subcol2, subcol3, subcol4 = st.columns([1,1,1,1,1,1,1])
        response_data = requests.get("http://localhost:8502/place-info", data=json.dumps(None))

def save_yesterday_data():
    korea_timezone = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(tz=korea_timezone)
    current_time_str = current_time.isoformat()
    current_time_json_data = json.dumps(current_time_str)
    data = {'start_time': current_time_json_data}
    response_data = requests.get("http://localhost:8502/save-yesterday", data=json.dumps(data))
    
    if response_data.status_code == 200:
        st.success('Updated until yesterday stats')


def showFirstPage():
    row4 = st.columns(1)
    part1, _ = st.columns([4, 3])
    placeholder = st.empty()
    chart, line_chart = st.columns([4, 4])
    endtime_json_data = None 
    with row4[0]:
        st.markdown("<h3 style='text-align: right; color: black;'>Data retrieval period</h3>", unsafe_allow_html=True)
        time_zone, subcol1, subcol2, subcol3, subcol4 = st.columns([4,1,1,1,1])

        with time_zone:
            korea_timezone = pytz.timezone('Asia/Seoul')
            current_time = datetime.now(tz=korea_timezone)
            current_time_str = current_time.isoformat()

            st.header("Current Time")
            time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

            datetime_obj = datetime.strptime(current_time_str, time_format)
            formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M')
            st.markdown(f"<span style='font-size: 40px;'>{formatted_time}</span>", unsafe_allow_html=True)

        with subcol1 :
            startdate = st.date_input('Select start date')
        with subcol2:
            starttime = st.time_input('Enter start time', key='start_time')

            if starttime:
                start_datetime = datetime.combine(startdate, starttime)
                starttime_utc = start_datetime.astimezone(pytz.utc)
                st.write('Selected time in UTC:', starttime_utc)

                starttime_str = starttime_utc.isoformat()
                starttime_json_data = json.dumps(starttime_str)

        with subcol3 :
            enddate = st.date_input('Select end date')
        with subcol4 :
            endtime = st.time_input('Enter end time', key='end_time')
            if endtime:
                end_datetime = datetime.combine(enddate, endtime)
                endtime_utc = end_datetime.astimezone(pytz.utc)
                st.write('Selected time in UTC:', endtime_utc)

                endtime_str = endtime_utc.isoformat()
                endtime_json_data = json.dumps(endtime_str)     


    with part1:
        if subcol3.button("Send to Go server", key='check_ward') :
            if endtime_json_data != None:
                data = {'sector_id': 6, 'start_time': starttime_json_data, 'end_time': endtime_json_data}
                userID = requests.get("http://localhost:8502/api", data=json.dumps(data))
                if userID.status_code == 200:
                    if 'json' in userID.headers.get('Content-Type'):
                        userID_response = userID.json()
                        if userID_response["userIDs"] != None:
                            for_check = userID_response["userIDs"]
                            for idx in range(len(for_check)):
                                st.write(for_check[idx])
                    else:
                        print('Response content is not in JSON format.')
                        js = 'spam'

    with placeholder.container():
        chart_data, loaded_data = None, None
        dates = [0]*30
        with chart:
            save_yesterday_data()
            data = {'end_time': endtime_json_data}
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
                if chart_data.size != 0:
                    st.line_chart(data=chart_data, x=None, y=None, width=0, height=500, use_container_width=True)
            with tab2:
                st.header("Loaded Data Histogram")
                if loaded_data.size != 0:
                    fig = px.histogram(data_frame=loaded_data, x='Date', y='Count', nbins=30, text_auto=True)
                    st.write(fig)

        st.markdown("### Detailed Data View")


if __name__ == '__main__' :
    set_page_title()
    set_performance_sidebar()
    place_info_container
    showFirstPage()