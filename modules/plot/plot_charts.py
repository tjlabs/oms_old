import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from utils import process_data

def plot_pos_diff_chrt(daily_ped_datas: np.ndarray) -> None:
    th_10 = []
    for idx in range(len(daily_ped_datas[:, 0])):
        th_10.append(100-daily_ped_datas[idx][2]-daily_ped_datas[idx][3]-daily_ped_datas[idx][4])

    ped_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
        'threshold_10': th_10,
        'threshold_30': list(daily_ped_datas[:, 2]),
        'threshold_50': list(daily_ped_datas[:, 3]),
        'threshold_100': list(daily_ped_datas[:, 4]),
    })
    st.bar_chart(ped_data_frame.set_index('dates'), height=1000, use_container_width=True)

def plot_data_cnt(daily_ped_datas: np.ndarray) -> None:
    ped_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
        'data count': daily_ped_datas[:, 1],
    })
    st.bar_chart(ped_data_frame, x='dates', y='data count', height=1000, use_container_width=True)

def plot_pos_err_one_site(daily_ped_datas: np.ndarray) -> None:
    max_cnt = max(daily_ped_datas[:, 1])
    bar_heights = [(100*cnt)/max_cnt for cnt in daily_ped_datas[:, 1]]

    th_10 = []
    for idx, ratio in enumerate(bar_heights):
        daily_ped_datas[idx][2:] *= (ratio/100)
        th_10.append(ratio-daily_ped_datas[idx][2]-daily_ped_datas[idx][3]-daily_ped_datas[idx][4])

    ped_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
        'threshold_10': th_10,
        'threshold_30': list(daily_ped_datas[:, 2]),
        'threshold_50': list(daily_ped_datas[:, 3]),
        'threshold_100': list(daily_ped_datas[:, 4]),
    })

    st.bar_chart(ped_data_frame.set_index('dates'), height=1000, use_container_width=True)

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