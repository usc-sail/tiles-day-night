from util.load_data_basic import *
from util.load_sensor_data import *
from datetime import timedelta
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns


def convert_days_at_work(days_at_work_df, participant_id, shift='day'):
    if participant_id not in list(days_at_work_df.columns):
        return pd.DataFrame()

    work_df = days_at_work_df[participant_id].dropna()
    if len(work_df) == 0:
        return pd.DataFrame()

    work_df = work_df.sort_index()

    save_df = pd.DataFrame()
    for i in range(len(work_df)):
        date_str = work_df.index[i]
        if shift == 'day':
            start_str = (pd.to_datetime(date_str).replace(hour=7) - timedelta(hours=6)).strftime(date_time_format)[:-3]
            end_str = (pd.to_datetime(date_str).replace(hour=7) + timedelta(hours=18)).strftime(date_time_format)[:-3]
            row_df = pd.DataFrame(index=[start_str])
            row_df['start'] = start_str
            row_df['end'] = end_str
            save_df = save_df.append(row_df)
        else:
            if i + 1 < len(work_df):
                if (pd.to_datetime(work_df.index[i+1]) - pd.to_datetime(work_df.index[i])).total_seconds() < 2 * 3600 * 24:
                    start_str = (pd.to_datetime(date_str).replace(hour=19) - timedelta(hours=6)).strftime(date_time_format)[:-3]
                    end_str = (pd.to_datetime(date_str).replace(hour=19) + timedelta(hours=18)).strftime(date_time_format)[:-3]
                    row_df = pd.DataFrame(index=[start_str])
                    row_df['start'] = start_str
                    row_df['end'] = end_str
                    save_df = save_df.append(row_df)

    if len(save_df) < 15:
        return pd.DataFrame()

    return save_df


def process_fitbit(fitbit_df, workday_timeline_df, days_at_work_df):

    days_at_work_df = days_at_work_df.fillna(0)
    num_of_days = (pd.to_datetime(fitbit_df.index[-1]) - pd.to_datetime(fitbit_df.index[0])).days + 1

    fitbit_df = fitbit_df.sort_index()

    daily_stats_df = pd.DataFrame()
    for i in range(num_of_days):
        date_str = (pd.to_datetime(fitbit_df.index[0]) + timedelta(days=i)).strftime(date_only_date_time_format)
        start_day_str = (pd.to_datetime(fitbit_df.index[0]) + timedelta(days=i)).replace(hour=0, minute=0, second=0).strftime(date_time_format)[:-3]
        end_day_str = (pd.to_datetime(fitbit_df.index[0]) + timedelta(days=i)).replace(hour=23, minute=59, second=0).strftime(date_time_format)[:-3]

        fitbit_day_df = fitbit_df[start_day_str:end_day_str]
        fitbit_day_df = fitbit_day_df.dropna()

        # have 50% of the data
        if len(fitbit_day_df) < 720:
            continue

        row_df = pd.DataFrame(index=[start_day_str])
        if float(days_at_work_df.loc[date_str, id]) == 1.0:
            row_df['workday'] = 1
        else:
            row_df['workday'] = 0

        # Daily HR region
        max_hr = np.nanmax(fitbit_day_df['heart_rate'])
        row_df['light'] = np.nanmean((0.5 * max_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.7 * max_hr))
        row_df['moderate'] = np.nanmean((0.7 * max_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.85 * max_hr))
        row_df['intense'] = np.nanmean((0.85 * max_hr <= np.array(fitbit_day_df['heart_rate'])))
        row_df['step'] = np.nanmean(fitbit_day_df['StepCount'])

        for j in range(6):
            reg_start_str = (pd.to_datetime(start_day_str) + timedelta(hours=j*4)).strftime(date_time_format)[:-3]
            reg_end_str = (pd.to_datetime(start_day_str) + timedelta(hours=j*4+3, minutes=59)).strftime(date_time_format)[:-3]

            reg_df = fitbit_day_df[reg_start_str:reg_end_str]
            # have 50% of the data
            if len(reg_df) > 120:
                row_df['light_'+str(j)] = np.nanmean((0.5 * max_hr <= np.array(reg_df['heart_rate'])) & (np.array(reg_df['heart_rate']) < 0.7 * max_hr))
                row_df['moderate_'+str(j)] = np.nanmean((0.7 * max_hr <= np.array(reg_df['heart_rate'])) & (np.array(reg_df['heart_rate']) < 0.85 * max_hr))
                row_df['intense_'+str(j)] = np.nanmean((0.85 * max_hr <= np.array(reg_df['heart_rate'])))
                row_df['step_'+str(j)] = np.nanmean(reg_df['StepCount'])
        daily_stats_df = daily_stats_df.append(row_df)
    workday_stats_df = daily_stats_df.loc[daily_stats_df['workday'] == 1]
    offday_stats_df = daily_stats_df.loc[daily_stats_df['workday'] == 0]

    save_cols = list(workday_stats_df.columns)
    workday_sum_df = pd.DataFrame(index=[id], columns=save_cols, data=np.nanmean(workday_stats_df, axis=0).reshape(1, len(save_cols)))
    offday_sum_df = pd.DataFrame(index=[id], columns=save_cols, data=np.nanmean(offday_stats_df, axis=0).reshape(1, len(save_cols)))

    return workday_sum_df, offday_sum_df


def print_stats(sleep_df, col, func=stats.kruskal, func_name='K-S'):
    day_nurse_df = sleep_df.loc[sleep_df['shift'] == 'day']
    night_nurse_df = sleep_df.loc[sleep_df['shift'] == 'night']
    # day_nurse_df = sleep_df.loc[sleep_df['work'] == 'workday']
    # night_nurse_df = sleep_df.loc[sleep_df['work'] == 'offday']

    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(day_nurse_df[col].dropna()), len(night_nurse_df[col].dropna())))

    # Print
    print('Day shift: mean = %.3f, std = %.2f' % (np.nanmean(day_nurse_df[col]), np.nanstd(day_nurse_df[col])))
    print('Night shift: mean = %.3f, std = %.2f' % (np.nanmean(night_nurse_df[col]), np.nanstd(night_nurse_df[col])))

    # stats test
    stat, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path(__file__).parent.absolute().parents[1].joinpath('data', bucket_str)

    # read ground-truth data
    igtb_df = read_AllBasic(root_data_path)
    nurse_df = return_nurse_df(igtb_df)
    days_at_work_df = read_days_at_work(root_data_path)

    id_list = list(nurse_df['participant_id'])
    id_list.sort()

    if Path.exists(Path.joinpath(Path.cwd(), 'stats.csv.gz')) is True:
        fitbit_stats_df = pd.read_csv('stats.csv.gz', index_col=0)
    else:
        fitbit_stats_df = pd.DataFrame()
        for id in id_list:
            print('Process participant: %s' % (id))
            shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
            fitbit_df = read_prossed_fitbit_data(root_data_path, id)
            if fitbit_df is None:
                continue

            workday_timeline_df = convert_days_at_work(days_at_work_df, id, shift=shift)
            if len(workday_timeline_df) == 0:
                continue

            workday_sum_df, offday_sum_df = process_fitbit(fitbit_df, workday_timeline_df, days_at_work_df)
            workday_sum_df['shift'] = shift
            offday_sum_df['shift'] = shift

            fitbit_stats_df = fitbit_stats_df.append(workday_sum_df)
            fitbit_stats_df = fitbit_stats_df.append(offday_sum_df)
        fitbit_stats_df.to_csv(Path.joinpath(Path.cwd(), 'stats.csv.gz'), compression='gzip')

    compare_cols = ['light', 'moderate', 'intense', 'step']
    plot_list = ['0-4', '4-8', '8-12', '12-16', '16-20', '20-24']

    workday_stats_df = fitbit_stats_df.loc[fitbit_stats_df['workday'] == 1]
    offday_stats_df = fitbit_stats_df.loc[fitbit_stats_df['workday'] == 0]
    save_work_df, save_off_df = pd.DataFrame(), pd.DataFrame()

    for i in range(6):
        for j in range(len(workday_stats_df)):
            for col in compare_cols:
                row_df = pd.DataFrame(index=[workday_stats_df.index[j]])
                row_df['time'] = plot_list[i]
                row_df['data'] = workday_stats_df[col + '_' + str(i)][j]
                row_df['shift'] = 'Day Shift' if offday_stats_df['shift'][j] == 'day' else 'Night Shift'
                row_df['type'] = col
                save_work_df = save_work_df.append(row_df)
        for j in range(len(offday_stats_df)):
            for col in compare_cols:
                row_df = pd.DataFrame(index=[offday_stats_df.index[j]])
                row_df['time'] = plot_list[i]
                row_df['data'] = offday_stats_df[col + '_' + str(i)][j]
                row_df['shift'] = 'Day Shift' if offday_stats_df['shift'][j] == 'day' else 'Night Shift'
                row_df['type'] = col
                save_off_df = save_off_df.append(row_df)

    plot_data = [save_work_df, save_off_df]
    y_lim_list = [[0.3, 0.8], [0, 0.45], [0, 0.16], [0, 20]]
    y_tick_list = [[0.3, 0.4, 0.5, 0.6, 0.7, 0.8], [0, 0.09, 0.18, 0.27, 0.36, 0.45],
                   [0, 0.04, 0.08, 0.12, 0.16], [0, 4, 8, 12, 16, 20]]

    title_list = ['Light Activity Ratio', 'Moderate Activity Ratio', 'Intense Activity Ratio', 'Step Count (Per Minute)']
    for j, col in enumerate(compare_cols):
        fig, axes = plt.subplots(figsize=(12, 4), nrows=1, ncols=2)

        for i in range(2):
            plt_df = plot_data[i].loc[plot_data[i]['type'] == col].dropna()
            day_df = plt_df.loc[plt_df['shift'] == 'Day Shift']
            night_df = plt_df.loc[plt_df['shift'] == 'Night Shift']

            sns.lineplot(x="time", y='data', dashes=False, marker="o", hue='shift', data=plt_df, palette="seismic", ax=axes[i])

            # Calculate p value
            x_tick_list = ['0-4', '4-8', '8-12', '12-16', '16-20', '20-24']
            for time in range(6):
                tmp_day_df = day_df.loc[day_df['time'] == plot_list[time]]
                tmp_night_df = night_df.loc[night_df['time'] == plot_list[time]]

                stats_value, p = stats.kruskal(np.array(tmp_day_df.loc[tmp_day_df['type'] == col]['data']), np.array(tmp_night_df.loc[tmp_night_df['type'] == col]['data']))
                x_tick_list[time] = x_tick_list[time] + '\n(p<0.01)' if p < 0.01 else x_tick_list[time] + '\n(p=' + str(p)[:4] + ')'

            axes[i].set_xlim([-0.25, 6 - 0.75])
            axes[i].set_xlabel('')
            axes[i].set_ylabel('')
            axes[i].set_xticks(range(6))
            axes[i].set_yticks(y_tick_list[j])
            axes[i].grid(linestyle='--')
            axes[i].grid(False, axis='y')
            axes[i].set_yticklabels(y_tick_list[j], fontdict={'fontweight': 'bold', 'fontsize': 12})
            axes[i].set_ylim(y_lim_list[j])

            plt.rcParams["font.weight"] = "bold"
            plt.rcParams['axes.labelweight'] = 'bold'

            axes[i].set_xticklabels(x_tick_list, fontdict={'fontweight': 'bold', 'fontsize': 12})
            axes[i].yaxis.set_tick_params(size=1)

            handles, labels = axes[i].get_legend_handles_labels()
            axes[i].legend(handles=handles[0:], labels=labels[0:], prop={'size': 12}, loc='upper right')
            for tick in axes[i].yaxis.get_major_ticks():
                tick.label1.set_fontsize(12)
                tick.label1.set_fontweight('bold')

        plt.tight_layout(rect=[0, 0.02, 1, 0.93])
        plt.figtext(0.5, 0.95, title_list[j], ha='center', va='center', fontsize=13.5, fontweight='bold')
        plt.savefig(os.path.join(col + '.png'), dpi=300)
        plt.close()

    '''
    print('-----------workday-----------')
    workday_stats_df = fitbit_stats_df.loc[fitbit_stats_df['workday'] == 1]
    for col in compare_cols:
        print_stats(workday_stats_df, col)

    print('------------offday------------')
    offday_stats_df = fitbit_stats_df.loc[fitbit_stats_df['workday'] == 0]
    for col in compare_cols:
        print_stats(offday_stats_df, col)
    '''











