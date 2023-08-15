from turtle import title
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from utils import process_data
import altair as alt

def plot_position_loc_stats(daily_ped_datas: np.ndarray):
    th_10 = [65- data[2] - data[3] - data[4] for data in daily_ped_datas]
    dates = process_data.convert_date_format(daily_ped_datas[:, 0])

    ped_data_frame = pd.DataFrame({
        'dates': dates,
        'threshold_010': th_10,
        'threshold_030': list(daily_ped_datas[:, 2]),
        'threshold_050': list(daily_ped_datas[:, 3]),
        'threshold_100': list(daily_ped_datas[:, 4]),
    })

    ped_line_data_frame = pd.DataFrame({
        'dates': dates,
        'data_counts': list(daily_ped_datas[:, 1]),
    })

    line = alt.Chart(ped_line_data_frame).mark_line(color='red').encode(
        x='dates:T',
        y=alt.Y('data_counts:Q', title='Data Counts')
    )

    melted_data = pd.melt(ped_data_frame, id_vars=['dates'], value_vars=['threshold_010', 'threshold_030', 'threshold_050', 'threshold_100'], var_name='threshold')

    color_scale = alt.Scale(domain=['threshold_010', 'threshold_030', 'threshold_050', 'threshold_100'],
        range=['lightskyblue', 'lightgreen', 'lightsalmon', 'tomato'])

    bar = alt.Chart(melted_data).mark_bar(size=2000/len(melted_data)).encode(
        x=alt.X('dates:T', sort=dates),
        y=alt.Y('value:Q', title='Location Difference', scale=alt.Scale(domain=[0, 10])),
        color=alt.Color('threshold:N', scale=color_scale),
        tooltip=['value', 'threshold']
    ).properties(
        width=alt.Step(0),
        height=500
    ).interactive().properties(
        title=alt.TitleParams(text="Location Difference Chart", fontSize=20)
    )

    layered_chart = alt.layer(bar, line).resolve_scale(
        y='independent'
    ).properties(width=0)

    st.altair_chart(layered_chart, use_container_width=True) # type: ignore


def plot_daily_ttff(daily_tf_datas: np.ndarray, height: int) -> None:
    dates = [item[0] for item in daily_tf_datas]
    avg_time = [item[1] for item in daily_tf_datas]
    ttff_data_frame = pd.DataFrame({
        'dates': process_data.convert_date_format(np.array(dates)),
        'avg stabilization time': avg_time,
    })
    st.line_chart(ttff_data_frame, x='dates', y='avg stabilization time', height=height, use_container_width=True)

def scatter_avg_ttff(daily_tf_datas: tuple):
    avg_time = [item[1] for item in daily_tf_datas]
    dates = [item[0] for item in daily_tf_datas]
    dates = process_data.convert_date_format(np.array(dates))

    ttff_data_frame = pd.DataFrame({
        'dates': dates,
        'avg time to first fix': avg_time,
    })

    dot_chart = alt.Chart(ttff_data_frame).mark_circle(size=45,
        color='blue'
    ).encode(
        x=alt.X('dates:T', sort=dates),
        y='avg time to first fix:Q'
    ).interactive().properties(
        title=alt.TitleParams(text="Time To First Fix Chart", fontSize=20)
    )

    st.altair_chart(dot_chart, use_container_width=True) # type: ignore