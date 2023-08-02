import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_with_two_y_axis(whole_daily_datas):
    whole_daily_datas = np.array(whole_daily_datas)
    x = [date['calc_date'][5:10] for date in whole_daily_datas]
    y1 = [rate['threshold_10'] for rate in whole_daily_datas]
    y2 = [rate['threshold_30'] for rate in whole_daily_datas]

    # 그래프 그리기
    fig, ax1 = plt.subplots()

    # 첫 번째 y축 (왼쪽 축) 설정
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y1', color='tab:red')  # Y1 레이블 색상 설정
    ax1.plot(x, y1, color='tab:red', label='Y1 데이터')  # Y1 데이터를 빨간색으로 꺾은선 그래프로 표시
    ax1.tick_params(axis='y', labelcolor='tab:red')  # Y1 축 눈금 레이블 색상 설정

    # 두 번째 y축 (오른쪽 축) 설정
    ax2 = ax1.twinx()  # 첫 번째 축(ax1)과 x축을 공유하는 새로운 축(ax2) 생성
    ax2.set_ylabel('Y2', color='tab:blue')  # Y2 레이블 색상 설정
    ax2.plot(x, y2, color='tab:blue', label='Y2 데이터')  # Y2 데이터를 파란색으로 꺾은선 그래프로 표시
    ax2.tick_params(axis='y', labelcolor='tab:blue')  # Y2 축 눈금 레이블 색상 설정

    # 범례 표시
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.title("2개의 y축을 갖는 그래프")
    plt.show()



if __name__ == '__main__':
    whole_daily_datas = [
        {'sector_id': 0, 'calc_date': '2023-07-31T00:00:00Z', 'total_data': 109760, 'threshold_10': 2.15825265099124, 'threshold_30': 0.2795066851083448, 'threshold_50': 0.23340248962655602},
        {'sector_id': 0, 'calc_date': '2023-07-30T00:00:00Z', 'total_data': 5152, 'threshold_10': 3.299689440993789, 'threshold_30': 1.106366459627329, 'threshold_50': 0.6599378881987578},
        {'sector_id': 0, 'calc_date': '2023-07-29T00:00:00Z', 'total_data': 8788, 'threshold_10': 5.4278561675011385, 'threshold_30': 1.1492944924897586, 'threshold_50': 0.7396449704142012},
        {'sector_id': 0, 'calc_date': '2023-07-28T00:00:00Z', 'total_data': 50248, 'threshold_10': 3.068778856869925, 'threshold_30': 0.5472854640980735, 'threshold_50': 0.4179270816748925},
        {'sector_id': 0, 'calc_date': '2023-07-26T00:00:00Z', 'total_data': 132331, 'threshold_10': 1.923207713989919, 'threshold_30': 0.3476131820964098, 'threshold_50': 0.239550823314265},
        {'sector_id': 0, 'calc_date': '2023-07-25T00:00:00Z', 'total_data': 132903, 'threshold_10': 2.2918970978834188, 'threshold_30': 0.3506316636945742, 'threshold_50': 0.19036440110456498}
    ]

    whole_daily_data_cnts = pd.DataFrame({
                                'Count': [109760, 5152, 8788, 50248, 132331, 132903]
                                })

    # plot_combined_bar_and_line_chart(whole_daily_datas[0], len(whole_daily_datas[0]), whole_daily_data_cnts['Count'])
    plot_with_two_y_axis(whole_daily_datas)
