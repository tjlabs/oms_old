import streamlit as st
import time, json, pytz
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import altair as alt

def showFirstPage():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", layout="wide")
    st.title(":desktop_computer: Jupiter Health Check System")

    current_time = datetime.now()
    current_time_utc = current_time.astimezone(pytz.utc)
    current_time_str = current_time_utc.isoformat()
    current_time_json_data = json.dumps(current_time_str)   
    data = {'start_time': current_time_json_data}
    response_data = requests.get("http://localhost:8502/", data=json.dumps(data))
    if response_data.status_code == 200:
        st.write("Welcome")

    row4 = st.columns(1)
    part1, _ = st.columns([4, 3])
    show, chart = st.columns([1, 7])
    endtime_json_data = None 
    with row4[0]:
        st.markdown("<h3 style='text-align: right; color: black;'>Data retrieval period</h3>", unsafe_allow_html=True)
        _, subcol1, subcol2, subcol3, subcol4 = st.columns([1,2,2,2,2])

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


    with show:
        plot_button = show.button("Plot Chart", key='plot_daily_status')

    with chart:
        if plot_button:
            data = {'start_time': starttime_json_data}
            response_data = requests.get("http://localhost:8502/performance-statistics", data=json.dumps(data))
            if response_data.status_code == 200:
                data = response_data.json()
                daily_datas = data["dailyStatus"]

                chart_data = {}         

                dates = [0]*30
                chart_data = np.zeros((30, 4))
                for idx, daily_data in enumerate(daily_datas):
                    dates[idx] = daily_data["calc_date"][2:10]
                    chart_data[idx][0] = daily_data["threshold_50"]
                    chart_data[idx][1] = daily_data["threshold_30"]
                    chart_data[idx][2] = daily_data["threshold_10"]
                    chart_data[idx][3] = 100.0 - (daily_data["threshold_10"] + daily_data["threshold_30"] + daily_data["threshold_50"])
                
                columns = ["threshold_10", "threshold_30", "threshold_50", "threshold_over_50"]

                chart_data = pd.DataFrame(chart_data, columns=columns, index=dates)

                st.bar_chart(data=chart_data, x=None, y=None, width=0, height=1000, use_container_width=True)

if __name__ == '__main__' :
    showFirstPage()