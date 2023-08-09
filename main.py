import streamlit as st
from datetime import datetime, timedelta
from utils import data_requests, process_data
from modules.plot import plot_charts
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt

def set_page_title():
    st.set_page_config(page_title="Jupiter Health Check System", page_icon=":desktop_computer:", 
                       layout="wide", initial_sidebar_state="expanded")
    st.title(":desktop_computer: Jupiter Health Check System")
    st.divider()

@st.cache_data
def load_performance_tables() -> list:
    table_list = data_requests.request_performance_indicators()
    return table_list

def set_performance_sidebar(table_list: list) -> None:
    with st.sidebar:
        st.sidebar.multiselect(
            "Please select the performance metrics you would like to see.",
            table_list
        )

@st.cache_data
def get_place_datas() -> dict:
    place_info = data_requests.request_place_info()
    return place_info

@st.cache_data
def extract_sectors(place_info: dict) -> dict:
    sector = {}
    for key, value in place_info.items():
        sector[key] = value[0]
    return sector

def set_place_selection(place_info: dict, sector:dict) -> str:
    st.header("Place Information")

    command, col1, col2, col3 = st.columns([1,2,2,2])
    sector_key = 1
    with command:
        st.write("Select Place you want to Search")

    with col1:
        sector_key = select_sector(sector)
        if sector_key == '':
            st.selectbox('No sector', ())

    with col2:
        building_idx = select_building(sector_key, place_info)
        if building_idx == -1:
            st.selectbox('No building', ())

    with col3:
        level_name = select_level(sector_key, building_idx, place_info)
        if level_name == "":
            st.selectbox('No level', ())

    return sector_key

def select_sector(sectors: dict) -> str:
    sector = st.selectbox('Select sector', sectors.values())
    sector_key = process_data.find_key(sectors, sector) # type: ignore
    return sector_key
    
def select_building(sector_key: str, place_info: dict) -> int:
    building_idx = 0
    if len(place_info[sector_key]) > 1:
        building_list = place_info[sector_key][1]
        building_name = st.selectbox('Select building', sorted(building_list))
        building_idx = building_list.index(building_name)
        return building_idx
    return -1

def select_level(sector_key: str, building_idx: int, place_info) -> str:
    if len(place_info[sector_key]) > 2:
        levels_list = place_info[sector_key][2]
        each_level = process_data.divide_levels(levels_list)
        level_name = st.selectbox('Select level', sorted(each_level[building_idx], key=process_data.custom_sort_key))
        return level_name # type: ignore
    return ""

@st.cache_data
def get_current_time_and_json() -> tuple[str, str]: 
    with st.columns(1)[0]:
        st.header("Current Time")
        korea_timezone = timedelta(hours=9)
        utc_time = datetime.utcnow()
        korea_time = utc_time + korea_timezone
        today_date = utc_time.strftime('%Y-%m-%d %H:%M:%S')

    formatted_korea_time = korea_time.strftime('%Y-%m-%d %H:%M:%S')
    st.markdown(f"<span style='font-size: 40px;'>{formatted_korea_time}</span>", unsafe_allow_html=True)
    start_time, end_time = process_data.change_time_format_to_postgresdb(today_date)
    return start_time, end_time
        
@st.cache_data
def save_until_yesterday_data(start_time: str, end_time: str, sector_key: str):
    users, total_count = data_requests.request_yesterday_whole_users(start_time, end_time)

    is_updated = data_requests.check_yesterday_stats('location_difference', end_time)
    if is_updated == False:
        data_requests.update_postition_err_dist(users, start_time, end_time, sector_key)
    
    is_updated = data_requests.check_yesterday_stats('time_to_first_fix', end_time)
    if is_updated == False:
        data_requests.update_time_to_first_fix(users, start_time, end_time, sector_key)
        st.success('Updated until yesterday stats')

def load_webpage(end_time: str):
    ped, ttff = st.columns([4,2])

    with ped:
        st.subheader('Position Err Distance Data Chart')
        tab1, tab2, tab3, tab4 = st.tabs(["One Site", "With Line Chart", "Pos Diff Ratio", "Data Cnt"])
        daily_ped_datas = None
        daily_ped_datas = data_requests.position_err_dist_stats(end_time)

        if len(daily_ped_datas) == 30:
            with tab1:
                th_10 = [20 - data[2] - data[3] - data[4] for data in daily_ped_datas]

                # th_10 = []
                # for idx in range(len(daily_ped_datas)):
                #     daily_ped_datas[idx][2:] /= 10
                #     th_10.append(10-daily_ped_datas[idx][2]-daily_ped_datas[idx][3]-daily_ped_datas[idx][4])

                ped_data_frame = pd.DataFrame({
                    'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
                    'threshold_10': th_10,
                    'threshold_30': list(daily_ped_datas[:, 2]),
                    'threshold_50': list(daily_ped_datas[:, 3]),
                    'threshold__100': list(daily_ped_datas[:, 4]),
                })

                ped_line_data_frame = pd.DataFrame({
                    'dates': process_data.convert_date_format(daily_ped_datas[:, 0]),
                    'data_counts': list(daily_ped_datas[:, 1]),
                })

                line = alt.Chart(ped_line_data_frame).mark_line(color='yellow').encode(
                    x='dates:T',
                    y=alt.Y('data_counts:Q', title='Data Counts')
                )

                melted_data = pd.melt(ped_data_frame, id_vars=['dates'], value_vars=['threshold_10', 'threshold_30', 'threshold_50', 'threshold__100'], var_name='threshold')

                color_scale = alt.Scale(domain=['threshold_10', 'threshold_30', 'threshold_50', 'threshold__100'],
                    range=['blue', 'green', 'orange', 'red'])

                bar = alt.Chart(melted_data).mark_bar(size=15).encode(
                    x='dates:T',
                    y=alt.Y('value:Q', title='Threshold Values', scale=alt.Scale(domain=[0, 20])),
                    color=alt.Color('threshold:N', scale=color_scale),
                    tooltip=['value', 'threshold']
                ).properties(
                    width=alt.Step(0)
                ).interactive()

                layered_chart = alt.layer(bar, line).resolve_scale(
                    y='independent'
                ).properties(width=0)

                st.altair_chart(layered_chart, use_container_width=True)

            with tab2:
                plot_charts.plot_pos_err_one_site(daily_ped_datas, height=500)

            with tab3:
                plot_charts.plot_pos_diff_chrt(daily_ped_datas, height=500)
                
            with tab4:
                plot_charts.plot_data_cnt(daily_ped_datas, height=500)



    with ttff:
        st.subheader('Time To First Fix Data Chart')
        # tftab2 = st.tabs("Hour unit")
        daily_tf_datas = None        
        daily_tf_datas = data_requests.TTFF_stats(end_time)

        if len(daily_tf_datas) == 30:
            # with tftab1:
            #     plot_charts.plot_daily_ttff(daily_tf_datas, height=500)
            # with tftab2:
            dates = [item[0] for item in daily_tf_datas]
            avg_time = [item[1] for item in daily_tf_datas]
            combined_list = []
            for item in daily_tf_datas:
                combined_list += item[2]

            # Create a DataFrame
            ttff_data_frame = pd.DataFrame({
                'dates': process_data.convert_date_format(np.array(dates)),
                'avg stabilization time': avg_time,
            })

            ttff_hour_frame = pd.DataFrame({
                'hours': [x for x in range(0, 24*30)],
                'hour unit stab time': combined_list,
            })

            point_chart = alt.Chart(ttff_hour_frame).mark_point().encode(
                x='hours:Q',  # x축에 hours 열 사용
                y='hour unit stab time:Q',  # y축에 hour unit stab time 열 사용
                tooltip=['hours', 'hour unit stab time']  # 마우스 오버 시 나타날 정보 설정
            ).properties(
                width=600
            )

            # Create an Altair area gradient chart
            area_chart = alt.Chart(ttff_data_frame).mark_area(
                line=True,
                color='lightblue',
                opacity=0.4
            ).encode(
                x='dates:T',
                y='avg stabilization time:Q'
            )

            # Create a line chart for comparison
            line_chart = alt.Chart(ttff_data_frame).mark_line(
                color='blue'
            ).encode(
                x='dates:T',
                y='avg stabilization time:Q'
            )

            combined_chart = alt.layer(area_chart, line_chart, point_chart).resolve_scale(
                # x='independent'
            ).properties(width=600)

            # Display the combined chart using st.altair_chart
            st.altair_chart(combined_chart, use_container_width=True)

            # Combine the area chart and line chart
            combined_chart = area_chart + line_chart

            # Display the combined chart using st.altair_chart
            st.altair_chart(combined_chart, use_container_width=True)

# class 다 없애도 될 듯 --> PlaceInfo는 음 파이썬 클래스 공부하고 다시 생각해보기
# DBConnection 쪽 클래스에 있는 함수들은 다른데로 옯겨야 함
# main, data_request 등등 에서 불필요한 단계는 생략하기
# pylance 빨간줄 고치기
# 그래프 제대로 나오게 확인하기
# 파이썬 클래스 공부하기

if __name__ == '__main__' :
    set_page_title()
    table_list = load_performance_tables()
    set_performance_sidebar(table_list)
    place_info = get_place_datas()
    sector = extract_sectors(place_info)
    sector_key = set_place_selection(place_info, sector)
    start_time, end_time = get_current_time_and_json()

    # save_until_yesterday_data(start_time, end_time, sector_key)
    load_webpage(end_time)

