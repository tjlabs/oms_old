from turtle import title
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from utils import process_data
import altair as alt

def plot_position_loc_stats(daily_ped_datas: np.ndarray):
    th_10 = [50- data[3] - data[4] - data[5] for data in daily_ped_datas]

    ped_data_frame = pd.DataFrame({
        'dates': list(daily_ped_datas[:, 0]),
        'threshold_010': th_10,
        'threshold_030': list(daily_ped_datas[:, 3]),
        'threshold_050': list(daily_ped_datas[:, 4]),
        'threshold_100': list(daily_ped_datas[:, 5]),
    })

    ped_line_data_frame = pd.DataFrame({
        'dates': list(daily_ped_datas[:, 0]),
        'data_counts': list(daily_ped_datas[:, 2]),
    })

    # line = alt.Chart(ped_line_data_frame).mark_line(color='red').encode(
    #     x='dates:N',
    #     y=alt.Y('data_counts:Q', title='Data Counts')
    # )

    melted_data = pd.melt(ped_data_frame, id_vars=['dates'], value_vars=['threshold_010', 'threshold_030', 'threshold_050', 'threshold_100'], var_name='threshold')

    x_order = list(daily_ped_datas[:, 0])
    color_scale = alt.Scale(domain=['threshold_010', 'threshold_030', 'threshold_050', 'threshold_100'],
        range=['lightskyblue', 'lightgreen', 'lightsalmon', 'tomato'])

    bar = alt.Chart(melted_data).mark_bar(size=15).encode(
        x=alt.X('dates:N', sort=x_order),
        y=alt.Y('value:Q', title='Location Difference', scale=alt.Scale(domain=[0, 10])),
        color=alt.Color('threshold:N', scale=color_scale),
        tooltip=['value', 'threshold']
    ).properties(
        width=alt.Step(0),
        height=700
    ).interactive().properties(
        title=alt.TitleParams(text="Location Difference Chart", fontSize=20)
    )

    # layered_chart = alt.layer(bar, line).resolve_scale(
    #     y='independent'
    # ).properties(width=0)

    st.altair_chart(bar, use_container_width=True) # type: ignore


def plot_daily_ttff(daily_tf_datas: np.ndarray, height: int) -> None:
    dates = [item[0] for item in daily_tf_datas]
    avg_time = [item[1] for item in daily_tf_datas]
    ttff_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(np.array(dates)),
        'avg stabilization time': avg_time,
    })
    st.line_chart(ttff_data_frame, x='dates', y='avg stabilization time', height=height, use_container_width=True)

def ttff_line_chart(daily_tf_datas: tuple):
    id, avg_time = [], []

    # iphone, android, total = 

    for i in range(len(daily_tf_datas)):
        aa = list(daily_tf_datas[i])
        id.append(aa[0])
        avg_time.append(aa[2])

    # avg_time = [item[1] for item in daily_tf_datas]

    ttff_data_frame = pd.DataFrame({
        'id': id,
        'avg time to first fix': avg_time,
    })
    x_order = id

    line_chart = alt.Chart(ttff_data_frame).mark_line(
        color='blue'
    ).encode(
        x=alt.X('id:N', sort=x_order),
        y='avg time to first fix:Q'
    ).interactive().properties(
        title=alt.TitleParams(text="Time To First Fix Chart", fontSize=20)
    )

    st.altair_chart(line_chart, use_container_width=True) # type: ignore