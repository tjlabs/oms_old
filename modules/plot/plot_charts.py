import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib

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

def plot_cumulative_bar_chart(whole_daily_datas, whole_daily_data_cnts):
    # 느낌 상 50이상의 수치만 보여주도록 변경 
    whole_daily_datas = np.array(whole_daily_datas)
    max_cnt = float(max(whole_daily_data_cnts))
    daily_dates = [date['calc_date'][5:10] for date in whole_daily_datas] # ['Category 1', 'Category 2', 'Category 3', 'Category 4']
    threshold_10 = [rate['threshold_10'] for rate in whole_daily_datas]
    threshold_30 = [rate['threshold_30'] for rate in whole_daily_datas]
    threshold_50 = [rate['threshold_50'] for rate in whole_daily_datas]
    under_10 = []
    for val in range(len(whole_daily_data_cnts)):
        under_10.append(float(100)-float(threshold_10[val])-float(threshold_30[val])-float(threshold_50[val]))

    width = 0.7
    ind = np.arange(len(daily_dates))

    whole_daily_data_cnts = [rate*float(100)/max_cnt for rate in whole_daily_data_cnts]
    
    plt.figure(figsize=(30, 20))

    plt.bar(ind, under_10, width, color='royalblue', label='loc_diff 0~10 (m)')
    plt.bar(ind, threshold_10, width, bottom=[float(t0) for t0 in under_10], color='mediumseagreen', label='loc_diff 10~30 (m)')
    plt.bar(ind, threshold_30, width, bottom=[(float(t10) + float(t0)) for t10, t0 in zip(threshold_10, under_10)], color='orange', label='loc_diff 30~50 (m)')
    plt.bar(ind, threshold_50, width, bottom=[(float(t30)+float(t10) + float(t0)) for t30, t10, t0 in zip(threshold_30, threshold_10, under_10)], color='red', label='loc_diff 50~ (m)')

    plt.plot(ind, whole_daily_data_cnts, marker='o', color='yellow', label='total data count')

    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title('Combined Bar and Line Chart')
    plt.xticks(ind, daily_dates)
    plt.legend()

    return plt