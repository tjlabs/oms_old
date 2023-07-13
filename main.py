import streamlit as st
import time, json, pytz
import numpy as np
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

def showFirstPage():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", layout="wide")
    st.title(":desktop_computer: Jupiter Health Check System")

    row4 = st.columns(1)
    part1, _ = st.columns([4, 3])
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
                data = {'sector_id': 6, 'level_name': "B2", 'start_time': starttime_json_data, 'end_time': endtime_json_data}
                userID = requests.get("http://localhost:8502/api", data=json.dumps(data))
                if userID != None:
                    if 'json' in userID.headers.get('Content-Type'):
                        userID_response = userID.json()
                        if userID_response["userIDs"] != None:
                            for_check = userID_response["userIDs"]
                            for idx in range(len(for_check)):
                                st.write(for_check[idx])
                    else:
                        print('Response content is not in JSON format.')
                        js = 'spam'


    

if __name__ == '__main__' :
    showFirstPage()