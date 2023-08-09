import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from utils import process_data
import altair as alt

def plot_pos_diff_chrt(daily_ped_datas: np.ndarray, height: int) -> None:
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
    st.bar_chart(ped_data_frame.set_index('dates'), height=height, use_container_width=True)

def plot_data_cnt(daily_ped_datas: np.ndarray, height: int) -> None:
    ped_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
        'data count': daily_ped_datas[:, 1],
    })
    st.bar_chart(ped_data_frame, x='dates', y='data count', height=height, use_container_width=True)

def plot_pos_err_one_site(daily_ped_datas: np.ndarray, height: int) -> None:
    max_cnt = max(daily_ped_datas[:, 1])
    bar_heights = [(10*cnt)/max_cnt for cnt in daily_ped_datas[:, 1]]

    th_10 = []
    for idx, ratio in enumerate(bar_heights):
        daily_ped_datas[idx][2:] *= (ratio/10)
        th_10.append(ratio-daily_ped_datas[idx][2]-daily_ped_datas[idx][3]-daily_ped_datas[idx][4])

    ped_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
        'threshold_10': th_10,
        'threshold_30': list(daily_ped_datas[:, 2]),
        'threshold_50': list(daily_ped_datas[:, 3]),
        'threshold__100': list(daily_ped_datas[:, 4]),
    })

    ped_line_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
        'data_counts': list(daily_ped_datas[:, 1]) # bar_heights,
    })

    melted_df = ped_data_frame.melt(id_vars=['dates'], value_vars=['threshold_10', 'threshold_30', 'threshold_50', 'threshold__100'])

    # Altair stacked bar chart
    stacked_bar_chart = alt.Chart(melted_df).mark_bar(size=15).encode(
        x='dates:T',
        y=alt.Y('value:Q', title='Threshold Values', scale=alt.Scale(domain=[0, 10])),
        color=alt.Color('variable:N'),  # Specify stacking order
        tooltip=['variable', 'value']
    ).properties(
        width=alt.Step(15)
    )

    area_chart = alt.Chart(ped_line_data_frame).mark_area(
        color='lightyellow',
        line=True
    ).encode(
        x='dates:T',
        y=alt.Y('data_counts:Q', title='Data Counts', scale=alt.Scale(domain=[0, max_cnt])),
        tooltip=['dates', 'data_counts']
    )

    layered_chart = alt.layer(area_chart, stacked_bar_chart).resolve_scale(
        y='independent'
    ).properties(width=600)

    st.altair_chart(layered_chart, use_container_width=True)

    # line_chart = alt.Chart(ped_line_data_frame).mark_line(color='red').encode(
    #     x='dates:T',
    #     y=alt.Y('data_counts:Q', title='Data Counts'),
    #     tooltip=['dates', 'data_counts']
    # )

    # layered_chart = alt.layer(stacked_bar_chart, line_chart).resolve_scale(
    #     y='independent'
    # ).properties(width=600)

    # st.altair_chart(layered_chart, use_container_width=True)

    # st.bar_chart(ped_data_frame.set_index('dates'), height=height, use_container_width=True)

def plot_daily_ttff(daily_tf_datas: tuple, height: int) -> None:
    dates = [item[0] for item in daily_tf_datas]
    avg_time = [item[1] for item in daily_tf_datas]
    ttff_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(np.array(dates)),
        'avg stabilization time': avg_time,
    })
    st.line_chart(ttff_data_frame, x='dates', y='avg stabilization time', height=height, use_container_width=True)