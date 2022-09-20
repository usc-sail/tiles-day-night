# from util.load_data_basic import *
# from util.load_sensor_data import *
import sys
sys.path.insert(1, '/Users/brinkley97/Documents/development/lab-kcad/tiles-day-night/code/util/')
from load_data_basic import read_AllBasic, return_nurse_df
from load_my_path import load_gzip_csv_data
from datetime import timedelta
from scipy import stats
from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

day_map = {0: '3rd', 1: '4th', 2: '5th', 3: '6th', 4: '1st', 5: '2nd'}
night_map = {0: '6th', 1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th'}

time_list = ['1st', '2nd', '3rd', '4th', '5th', '6th']
num_seg = 6

def print_stats(sleep_df, col, func=stats.kruskal, func_name='K-S'):
    day_nurse_df = sleep_df.loc[sleep_df['shift'] == 'day']
    night_nurse_df = sleep_df.loc[sleep_df['shift'] == 'night']
    # day_nurse_df = sleep_df.loc[sleep_df['work'] == 'workday']
    # night_nurse_df = sleep_df.loc[sleep_df['work'] == 'offday']

    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(day_nurse_df[col].dropna()), len(night_nurse_df[col].dropna())))

    # Print
    print('Day shift: median = %.2f, mean = %.2f' % (np.nanmedian(day_nurse_df[col])*100, np.nanmean(day_nurse_df[col])*100))
    print('Night shift: median = %.2f, mean = %.2f' % (np.nanmedian(night_nurse_df[col])*100, np.nanmean(night_nurse_df[col])*100))

    # stats test
    stat, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))


if __name__ == '__main__':
    # Read ground truth data
    # bucket_str = 'tiles-phase1-opendataset'
    bucket_str = 'tiles_dataset'
    
    # root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)
    root_data_path = Path(__file__).parent.absolute().parents[2].joinpath('datasets', bucket_str)

    # read ground-truth data
    igtb_df = read_AllBasic(root_data_path)
    nurse_df = return_nurse_df(igtb_df)

    id_list = list(nurse_df['participant_id'])
    id_list.sort()
    
#     path_to_data =  "lab-kcad/datasets/tiles_dataset/" 
#     work_data = "figure_2/physical/diurnal_work_lm_6.csv.gz"
#     off_data = "figure_2/physical/diurnal_off_lm_6.csv.gz"
    
#     workday_stats_df = load_gzip_csv_data(path_to_data, work_data)
#     offday_stats_df = load_gzip_csv_data(path_to_data, off_data)
    
#     workday_stats_df = pd.read_csv('diurnal_work_lm_' + str(num_seg) +'.csv.gz', index_col=0)
#     offday_stats_df = pd.read_csv('diurnal_off_lm_' + str(num_seg) + '.csv.gz', index_col=0)
#     stats_df = pd.read_csv('stats_work_lm.csv.gz', index_col=0)
    
    workday_stats_df = pd.read_csv("/Users/brinkley97/Documents/development/lab-kcad/datasets/tiles_dataset/figure_2/physical/diurnal_work_lm_6.csv.gz", index_col=0)
    # print(workday_stats_df)
    offday_stats_df = pd.read_csv("/Users/brinkley97/Documents/development/lab-kcad/datasets/tiles_dataset/figure_2/physical/diurnal_off_lm_6.csv.gz", index_col=0)
    # stats_df = pd.read_csv('stats_work_lm.csv.gz', index_col=0)

    compare_cols = ['rest', 'step_ratio']
    plot_list = ['23h-3h', '3h-7h', '7h-11h', '11h-15h', '15h-19h', '19h-23h']

    save_work_df, save_off_df = pd.DataFrame(), pd.DataFrame()
    for i in range(6):
        tmp_work_df = workday_stats_df.loc[workday_stats_df['time'] == time_list[i]]
        # print(tmp_work_df)
        tmp_off_df = offday_stats_df.loc[offday_stats_df['time'] == time_list[i]]

        for j in range(len(tmp_work_df)):
            for col in compare_cols:
                row_df = pd.DataFrame(index=[tmp_work_df.index[j]])
                # print(row_df)
                row_df['time'] = plot_list[i]
                # print(type(row_df['time']))
                row_df['data'] = tmp_work_df[col][j] * 100
                # print("\nrow_df['data']", type(row_df['data']))
                # row_df['data'] = tmp_work_df[col][j]
                # print(col)
                # print("\nrow_df['data']", row_df['data'])
                row_df['shift'] = 'Day Shift' if tmp_work_df['shift'][j] == 'day' else 'Night Shift'
                row_df['type'] = col
                # print(row_df['type'])
                # save_work_df = save_work_df.append(row_df)
                save_work_df = pd.concat([save_work_df, row_df])
                # print("Save work df", save_work_df)
        for j in range(len(tmp_off_df)):
            for col in compare_cols:
                row_df = pd.DataFrame(index=[tmp_off_df.index[j]])
                row_df['time'] = plot_list[i]
                row_df['data'] = tmp_off_df[col][j] * 100
                row_df['shift'] = 'Day Shift' if tmp_off_df['shift'][j] == 'day' else 'Night Shift'
                row_df['type'] = col
                # save_off_df = save_off_df.append(row_df)
                save_off_df = pd.concat([save_off_df, row_df])

    plot_data = [save_work_df, save_off_df]
    y_lim_list = [[50, 110], [-10, 80]]
    y_tick_list = [[60, 70, 80, 90, 100], [0, 20, 40, 60, 80]]

    title_list = ['Rest Activity Ratio', 'Walk Activity Ratio']
    for j, col in enumerate(compare_cols):
        # print("###########j, col:", j, col)
        # fig, axes = plt.subplots(figsize=(12, 3), nrows=1, ncols=2)

        for i in range(2):
            # print(i)
            plt_df = plot_data[i].loc[plot_data[i]['type'] == col].dropna()
            day_df = plt_df.loc[plt_df['shift'] == 'Day Shift']
            # print("day_df", day_df)
            night_df = plt_df.loc[plt_df['shift'] == 'Night Shift']
            # print("night_df", night_df)
            
            # sns.lineplot(x="time", y='data', dashes=False, marker="o", hue='shift', data=plt_df, palette="seismic", ax=axes[i])

            # Calculate p value
            x_tick_list = ['23h-3h', '3h-7h', '7h-11h', '11h-15h', '15h-19h', '19h-23h']
            p_val_df = pd.DataFrame(index=x_tick_list)
            # Calculate p value
            x_tick_list = ['23h-3h', '3h-7h', '7h-11h', '11h-15h', '15h-19h', '19h-23h']

            for time in range(num_seg):
                print("###########j, col:", j, col)
                tmp_day_df = day_df.loc[day_df['time'] == plot_list[time]]
                tmp_night_df = night_df.loc[night_df['time'] == plot_list[time]]
                print("\nDAY", tmp_day_df, "\nNIGHT", tmp_night_df)
                
                stats_value, p = stats.ttest_ind(np.array(tmp_day_df.loc[tmp_day_df['type'] == col]['data']), np.array(tmp_night_df.loc[tmp_night_df['type'] == col]['data']))        
                
                # p_val_df.loc[x_tick_list[time], "p-val"] = p
                # print("\nP_VALUE ", p_val_df)
                # print("------------------------------------")
                if p < 0.01:
                    x_tick_list[time] = x_tick_list[time] + '**'
                elif p < 0.05:
                    x_tick_list[time] = x_tick_list[time] + '*'
            work_cond = ["work_day", "off_day"]
            # compression_opts = dict(method='zip', archive_name='p-val.csv')
            # p_val_df.to_csv('p-val.zip', index=False, compression=compression_opts)
            # print("analysis for %s, work condition: %s" % (title_list[j], work_cond[i]))
            # print(p_val_df)
#             axes[i].set_xlim([-0.25, 6 - 0.75])
#             axes[i].set_xlabel('')
#             axes[i].set_ylabel('Percentage (%)', fontdict={'fontweight': 'bold', 'fontsize': 12})
#             axes[0].set_title('Workday', fontdict={'fontweight': 'bold', 'fontsize': 12})
#             axes[1].set_title('Off-day', fontdict={'fontweight': 'bold', 'fontsize': 12})

#             axes[i].set_xticks(range(6))
#             axes[i].set_yticks(y_tick_list[j])
#             axes[i].grid(linestyle='--')
#             axes[i].grid(False, axis='y')
#             axes[i].set_yticklabels(y_tick_list[j], fontdict={'fontweight': 'bold', 'fontsize': 10.5})
#             axes[i].set_ylim(y_lim_list[j])

#             plt.rcParams["font.weight"] = "bold"
#             plt.rcParams['axes.labelweight'] = 'bold'

#             axes[i].set_xticklabels(x_tick_list, fontdict={'fontweight': 'bold', 'fontsize': 10.5})
#             axes[i].yaxis.set_tick_params(size=1)

#             handles, labels = axes[i].get_legend_handles_labels()
#             axes[i].legend(handles=handles[0:], labels=labels[0:], prop={'size': 11, 'weight':'bold'}, loc='upper right')
#             for tick in axes[i].yaxis.get_major_ticks():
#                 tick.label1.set_fontsize(12)
#                 tick.label1.set_fontweight('bold')

#         plt.tight_layout(rect=[0, 0.02, 1, 0.93])
#         plt.figtext(0.5, 0.95, title_list[j], ha='center', va='center', fontsize=13.5, fontweight='bold')
#         plt.savefig(os.path.join(col + '.png'), dpi=300)
#         plt.close()











