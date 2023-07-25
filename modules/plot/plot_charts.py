import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

def plot_stacked_bar_chart(daily_datas):
    chart_data = np.zeros((30, 4))
    dates, loaded_data = [0]*30, [0]*30
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
    return chart_data, loaded_data

def plot_line_chart(chart_data, loaded_data):
    tab1, tab2 = st.tabs(["Line Chart", "Loaded Data Histogram"])
    with tab1:
        st.header("Line Chart")
        st.line_chart(data=chart_data, x=None, y=None, width=0, height=500, use_container_width=True)
    with tab2:
        st.header("Loaded Data Histogram")
        st.write(px.histogram(data_frame=loaded_data, x='Date', y='Count', nbins=30, text_auto=True))