import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 누적 막대그래프 이거 100까지 안 차는 거 수정해야 함 

def plot_combined_bar_and_line_chart(whole_daily_datas, cnt: int, whole_daily_data_cnts: list):
    max_cnt = float(max(whole_daily_data_cnts))
    daily_dates = [whole_daily_datas['calc_date'][5:10] for date in whole_daily_datas] # ['Category 1', 'Category 2', 'Category 3', 'Category 4']
    threshold_10 = [whole_daily_datas['threshold_10'] for date in whole_daily_datas]
    threshold_30 = [whole_daily_datas['threshold_30'] for date in whole_daily_datas]
    threshold_50 = [whole_daily_datas['threshold_50'] for date in whole_daily_datas]
    under_10 = []
    for val in range(cnt):
        under_10.append(float(100)-float(threshold_10[val])-float(threshold_30[val])-float(threshold_50[val]))

    width = 0.35
    ind = np.arange(len(daily_dates))

    whole_daily_data_cnts = [rate*float(100)/max_cnt for rate in whole_daily_data_cnts]
    
    plt.figure(figsize=(12, 6))

    # 막대 그래프 그리기
    plt.bar(ind, threshold_50, width, bottom=[float(t30) for t30 in threshold_30], label='loc_diff 50~ (m)')
    plt.bar(ind, threshold_30, width, bottom=[float(t10) for t10 in threshold_10], label='loc_diff 30~50 (m)')
    plt.bar(ind, [float(t10) for t10 in threshold_10], width, label='loc_diff 10~30 (m)')
    plt.bar(ind, under_10, width, bottom=[float(t50) for t50 in threshold_50], label='loc_diff 50~ (m)')

    # 꺾은선 그래프 그리기
    plt.plot(ind, whole_daily_data_cnts, marker='o', color='b', label='Dataset 3')

    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title('Combined Bar and Line Chart')
    plt.xticks(ind, daily_dates)
    plt.legend()

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

    plot_combined_bar_and_line_chart(whole_daily_datas[0], len(whole_daily_datas[0]), whole_daily_data_cnts['Count'])

