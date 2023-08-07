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

def plot_cumulative_bar_chart(whole_daily_datas, whole_daily_data_cnts, cnt: int):
    # 느낌 상 50이상의 수치만 보여주도록 변경 
    whole_daily_datas = np.array(whole_daily_datas)
    whole_daily_datas = whole_daily_datas[:cnt]
    whole_daily_data_cnts = whole_daily_data_cnts[:cnt]

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

    plt.figure(figsize=(60, 30))

    plt.bar(ind, under_10, width, color='royalblue', label='loc_diff 0~10 (m)')
    plt.bar(ind, threshold_10, width, bottom=[float(t0) for t0 in under_10], color='mediumseagreen', label='loc_diff 10~30 (m)')
    plt.bar(ind, threshold_30, width, bottom=[(float(t10) + float(t0)) for t10, t0 in zip(threshold_10, under_10)], color='orange', label='loc_diff 30~50 (m)')
    plt.bar(ind, threshold_50, width, bottom=[(float(t30)+float(t10) + float(t0)) for t30, t10, t0 in zip(threshold_30, threshold_10, under_10)], color='red', label='loc_diff 50~ (m)')
    plt.ylim(70, 100)

    plt.xticks(ind, daily_dates, rotation=45, fontsize=36)  # 글자 크기를 24로 설정
    plt.xlabel('Dates', fontsize=36)  # x축 라벨의 글자 크기를 36으로 설정
    plt.ylabel('Percentage', fontsize=36)  # y축 라벨의 글자 크기를 36으로 설정
    plt.title('Combined Bar and Line Chart', fontsize=48)  # 제목의 글자 크기를 48로 설정
    plt.legend(fontsize=48) 

    bar_chart = plt

    return bar_chart

def plot_cumulative_bar_chart2(whole_daily_datas, whole_daily_data_cnts, cnt: int):
    # 느낌 상 50이상의 수치만 보여주도록 변경 
    whole_daily_datas = np.array(whole_daily_datas)
    whole_daily_datas = whole_daily_datas[:cnt]
    whole_daily_data_cnts = whole_daily_data_cnts[:cnt]

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


    plt.figure(figsize=(60, 30))

    whole_daily_data_cnts = [rate*float(100)/max_cnt for rate in whole_daily_data_cnts]
    plt.plot(ind, whole_daily_data_cnts, marker='o', color='red', label='total data count', linewidth=5)
    plt.xticks(ind, daily_dates, rotation=45, fontsize=36)
    plt.xlabel('Dates', fontsize=36)
    plt.title('Line Chart', fontsize=48)
    plt.legend(fontsize=48)

    line_chart = plt 

    return line_chart

def plot_cumulative_datacnt_height_chart(whole_daily_datas, whole_daily_data_cnts, cnt: int):
    # 느낌 상 50이상의 수치만 보여주도록 변경 
    whole_daily_datas = np.array(whole_daily_datas)
    max_cnt = float(max(whole_daily_data_cnts))
    daily_dates = [date['calc_date'][5:10] for date in whole_daily_datas][:cnt]
    threshold_10 = [rate['threshold_10'] for rate in whole_daily_datas][:cnt]
    threshold_30 = [rate['threshold_30'] for rate in whole_daily_datas][:cnt]
    threshold_50 = [rate['threshold_50'] for rate in whole_daily_datas][:cnt]
    under_10 = []
    for val in range(len(whole_daily_data_cnts)):
        under_10.append(float(100)-float(threshold_10[val])-float(threshold_30[val])-float(threshold_50[val]))

    width = 0.7
    ind = np.arange(len(daily_dates))

    # whole_daily_data_cnts의 각 요소를 사용하여 막대 그래프의 높이 계산
    bar_heights = [rate * 100 / max(whole_daily_data_cnts) for rate in whole_daily_data_cnts]

    plt.figure(figsize=(30, 20))

    # 각 막대 그래프의 높이를 bar_heights 리스트로 지정하여 그래프를 그림
    plt.bar(ind, under_10, width, color='royalblue', label='loc_diff 0~10 (m)')
    plt.bar(ind, threshold_10, width, bottom=[float(t0) for t0 in under_10], color='mediumseagreen', label='loc_diff 10~30 (m)')
    plt.bar(ind, threshold_30, width, bottom=[(float(t10) + float(t0)) for t10, t0 in zip(threshold_10, under_10)], color='orange', label='loc_diff 30~50 (m)')
    plt.bar(ind, threshold_50, width, bottom=[(float(t30) + float(t10) + float(t0)) for t30, t10, t0 in zip(threshold_30, threshold_10, under_10)], color='red', label='loc_diff 50~ (m)')

    # 그래프의 y축 눈금을 whole_daily_data_cnts에 해당하는 값으로 지정
    plt.yticks(whole_daily_data_cnts)

    # 그래프에 레이블, 제목 등을 추가
    plt.xlabel('X-axis label')
    plt.ylabel('Y-axis label')
    plt.title('Bar Chart with Whole Daily Data Counts')
    plt.legend()

    return plt

def plot_with_two_y_axis(whole_daily_datas):
    whole_daily_datas = np.array(whole_daily_datas)

    x = [date['calc_date'][5:10] for date in whole_daily_datas]
    y1 = [rate['stable_time'] for rate in whole_daily_datas]
    y2 = [rate['users_count'] for rate in whole_daily_datas]
    # y3 = [rate['hour_unit_ttff'] for rate in whole_daily_datas]

    fig, ax1 = plt.subplots()

    y1_minutes, y1_seconds = convert_to_minutes_and_seconds(y1)


    # 첫 번째 y축 (왼쪽 축) 설정
    ax1.set_xlabel('X')
    ax1.set_ylabel('Time To First Fix (분:초)', color='tab:red')  # Y1 레이블 색상 설정
    ax1.plot(x, y1_minutes, color='tab:red', label='Time To First Fix')  # Y1 데이터를 분 단위로 꺾은선 그래프로 표시
    ax1.tick_params(axis='y', labelcolor='tab:red')  # Y1 축 눈금 레이블 색상 설정

    # 두 번째 y축 (오른쪽 축) 설정
    ax2 = ax1.twinx()  # 첫 번째 축(ax1)과 x축을 공유하는 새로운 축(ax2) 생성
    ax2.set_ylabel('User Num', color='tab:blue')  # Y2 레이블 색상 설정
    ax2.plot(x, y2, color='tab:blue', label='User Num')  # Y2 데이터를 파란색으로 꺾은선 그래프로 표시
    ax2.tick_params(axis='y', labelcolor='tab:blue')  # Y2 축 눈금 레이블 색상 설정
    ax2.set_ylim(0, 110)

    plt.xticks(range(len(x)), x)

    # 범례 표시
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.title("First Fix Time and User count")
    return plt

def convert_to_minutes_and_seconds(seconds_list):
    minutes = [sec // 60 for sec in seconds_list]
    seconds = [sec % 60 for sec in seconds_list]
    return minutes, seconds