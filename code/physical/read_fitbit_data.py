from util.load_data_basic import *
from util.load_sensor_data import *
from datetime import timedelta
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns

# 0 is actually 11pm - 3am, ..., 5 is 7pm - 11pm
# day starts with 2, which is 7am -11am, night starts with 5, which is 7pm - 11pm
day_map = {0: 2, 1: 3, 2: 4, 3: 5, 4: 0, 5: 1}
night_map = {0: 5, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4}


def process_fitbit(fitbit_df, timeline_df, maximum_hr, resting_hr, shift='day'):

    fitbit_df = fitbit_df.sort_index()
    daily_stats_df = pd.DataFrame()

    hr_reserve = maximum_hr - resting_hr

    for i in range(len(timeline_df)):
        start_day_str = timeline_df['start'][i]
        end_day_str = timeline_df['end'][i]

        fitbit_day_df = fitbit_df[start_day_str:end_day_str]
        fitbit_day_df = fitbit_day_df.dropna()

        # have 50% of the data
        if len(fitbit_day_df) < 720:
            continue

        fitbit_day_df = fitbit_day_df.loc[fitbit_day_df['heart_rate'] < maximum_hr]

        row_df = pd.DataFrame(index=[start_day_str])
        row_df['work'] = 1 if timeline_df['work'][i] == 1 else 0

        # Daily HR region
        # max_hr = np.nanmax(fitbit_day_df['heart_rate'])
        row_df['rest'] = np.nanmean((0.5 * maximum_hr > np.array(fitbit_day_df['heart_rate'])))
        row_df['moderate'] = np.nanmean((0.5 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.7 * maximum_hr))
        row_df['vigorous'] = np.nanmean((0.7 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.85 * maximum_hr))
        row_df['intense'] = np.nanmean((0.85 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])))

        # row_df['rest'] = np.nanmean((0.5 * maximum_hr > np.array(fitbit_day_df['heart_rate'])))
        # row_df['moderate'] = np.nanmean((0.5 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.64 * maximum_hr))
        # row_df['vigorous'] = np.nanmean((0.64 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.76 * maximum_hr))
        # row_df['intense'] = np.nanmean((0.76 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.93 * maximum_hr))

        # row_df['rest'] = np.nanmean(((0.4 * hr_reserve + resting_hr) > np.array(fitbit_day_df['heart_rate'])))
        # row_df['moderate'] = np.nanmean(((0.4 * hr_reserve + resting_hr) <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < (0.6 * hr_reserve + resting_hr)))
        # row_df['vigorous'] = np.nanmean(((0.6 * hr_reserve + resting_hr) <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < (0.85 * hr_reserve + resting_hr)))
        # row_df['intense'] = np.nanmean(((0.85 * hr_reserve + resting_hr) <= np.array(fitbit_day_df['heart_rate'])))
        row_df['step'] = np.nanmean(fitbit_day_df['StepCount'])

        for j in range(6):
            reg_start_str = (pd.to_datetime(start_day_str) + timedelta(hours=j*4)).strftime(date_time_format)[:-3]
            reg_end_str = (pd.to_datetime(start_day_str) + timedelta(hours=j*4+3, minutes=59)).strftime(date_time_format)[:-3]

            reg_df = fitbit_day_df[reg_start_str:reg_end_str]
            # have 50% of the data
            if len(reg_df) > 120:
                # offset comparing to 11pm, for day/night shift nurses it starts at 7am/7pm
                offset = day_map[j] if shift == 'day' else night_map[j]
                row_df['rest_' + str(offset)] = np.nanmean((0.5 * maximum_hr > np.array(reg_df['heart_rate'])))
                row_df['moderate_' + str(offset)] = np.nanmean((0.5 * maximum_hr <= np.array(reg_df['heart_rate'])) & (np.array(reg_df['heart_rate']) < 0.7 * maximum_hr))
                row_df['vigorous_' + str(offset)] = np.nanmean((0.7 * maximum_hr <= np.array(reg_df['heart_rate'])) & (np.array(reg_df['heart_rate']) < 0.85 * maximum_hr))
                row_df['intense_' + str(offset)] = np.nanmean((0.85 * maximum_hr <= np.array(reg_df['heart_rate'])))


                row_df['step_'+str(offset)] = np.nanmean(reg_df['StepCount'])
        daily_stats_df = daily_stats_df.append(row_df)
    workday_stats_df = daily_stats_df.loc[daily_stats_df['work'] == 1]
    offday_stats_df = daily_stats_df.loc[daily_stats_df['work'] == 0]

    save_cols = list(workday_stats_df.columns)

    # we only keep analyses with 10 data per participant
    workday_sum_df, offday_sum_df = pd.DataFrame(), pd.DataFrame()
    if len(workday_stats_df) > 10: workday_sum_df = pd.DataFrame(index=[id], columns=save_cols, data=np.nanmean(workday_stats_df, axis=0).reshape(1, len(save_cols)))
    if len(offday_stats_df) > 10: offday_sum_df = pd.DataFrame(index=[id], columns=save_cols, data=np.nanmean(offday_stats_df, axis=0).reshape(1, len(save_cols)))

    daily_sum_df = pd.DataFrame(index=[id], columns=save_cols, data=np.nanmean(daily_stats_df, axis=0).reshape(1, len(save_cols)))
    daily_sum_df['work'] = 0.5

    return workday_sum_df, offday_sum_df, daily_sum_df


def print_stats(sleep_df, col, func=stats.kruskal, func_name='K-S'):
    day_nurse_df = sleep_df.loc[sleep_df['shift'] == 'day']
    night_nurse_df = sleep_df.loc[sleep_df['shift'] == 'night']

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
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path(__file__).parent.absolute().parents[1].joinpath('data')

    # read ground-truth data
    # please contact the author to access: igtb_day_night.csv.gz
    if Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz').exists() == False:
        igtb_df = read_AllBasic(root_data_path)
        igtb_df.to_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'))
    igtb_df = pd.read_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'), index_col=0)
    nurse_df = return_nurse_df(igtb_df)

    id_list = list(nurse_df['participant_id'])
    id_list.sort()

    if Path.exists(Path.joinpath(Path.cwd(), 'stats.csv.gz')) is True:
        fitbit_stats_df = pd.read_csv('stats.csv.gz', index_col=0)
    else:
        fitbit_stats_df = pd.DataFrame()
        for id in id_list:
            print('Process participant: %s' % (id))
            shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
            age = nurse_df.loc[nurse_df['participant_id'] == id].age[0]

            fitbit_df = read_prossed_fitbit_data(root_data_path.joinpath(bucket_str), id)
            summary_df = read_fitbit_daily_data(root_data_path.joinpath(bucket_str), id)

            if fitbit_df is None: continue

            # heart rate basic
            maximum_hr = 220 - age
            resting_hr = int(np.nanmean(summary_df['RestingHeartRate']))

            if Path.exists(root_data_path.joinpath('processed', 'timeline', id + '.csv.gz')) is False:
                continue
            timeline_df = pd.read_csv(root_data_path.joinpath('processed', 'timeline', id + '.csv.gz'), index_col=0)

            workday_sum_df, offday_sum_df, daily_sum_df = process_fitbit(fitbit_df, timeline_df, maximum_hr, resting_hr, shift)
            workday_sum_df['shift'] = shift
            offday_sum_df['shift'] = shift
            daily_sum_df['shift'] = shift

            if len(workday_sum_df) > 0 and len(offday_sum_df) > 0:
                daily_sum_df['rest_diff'] = workday_sum_df['rest'][0] - offday_sum_df['rest'][0]
                daily_sum_df['moderate_diff'] = workday_sum_df['moderate'][0] - offday_sum_df['moderate'][0]
                daily_sum_df['vigorous_diff'] = workday_sum_df['vigorous'][0] - offday_sum_df['vigorous'][0]
                daily_sum_df['intense_diff'] = workday_sum_df['intense'][0] - offday_sum_df['intense'][0]
                daily_sum_df['step_diff'] = workday_sum_df['step'][0] - offday_sum_df['step'][0]

            fitbit_stats_df = fitbit_stats_df.append(workday_sum_df)
            fitbit_stats_df = fitbit_stats_df.append(offday_sum_df)
            fitbit_stats_df = fitbit_stats_df.append(daily_sum_df)

        fitbit_stats_df.to_csv(Path.joinpath(Path.cwd(), 'stats.csv.gz'), compression='gzip')

    compare_cols = ['rest', 'moderate', 'vigorous', 'intense', 'step']
    plot_list = ['11PM-3AM', '3AM-7AM', '7AM-11AM', '11AM-3PM', '3PM-7PM', '7PM-11PM']

    workday_stats_df = fitbit_stats_df.loc[fitbit_stats_df['work'] == 1]
    offday_stats_df = fitbit_stats_df.loc[fitbit_stats_df['work'] == 0]
    save_work_df, save_off_df = pd.DataFrame(), pd.DataFrame()

    for col in compare_cols:
        print('workdays')
        print_stats(workday_stats_df, col, func=stats.mannwhitneyu)

        print('off-days')
        print_stats(offday_stats_df, col, func=stats.mannwhitneyu)

    for i in range(6):
        for j in range(len(workday_stats_df)):
            for col in compare_cols:
                row_df = pd.DataFrame(index=[workday_stats_df.index[j]])
                row_df['time'] = plot_list[i]
                row_df['data'] = workday_stats_df[col + '_' + str(i)][j]
                row_df['shift'] = 'Day Shift' if workday_stats_df['shift'][j] == 'day' else 'Night Shift'
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
    y_lim_list = [[0.5, 1.2], [0, 0.6], [-0.01, 0.03], [0, 0.025], [0, 22]]
    y_tick_list = [[0.5, 0.6, 0.7, 0.8, 0.9, 1], [0, 0.2, 0.4, 0.6], [-0.01, 0.0, 0.01, 0.02, 0.03],
                   [0, 0.01, 0.02, 0.03, 0.04, 0.05], [0, 4, 8, 12, 16, 20]]

    title_list = ['Rest Activity Ratio', 'Moderate Activity Ratio', 'Vigorous Activity Ratio', 'Intense Activity Ratio', 'Step Count (Per Minute)']
    for j, col in enumerate(compare_cols):
        fig, axes = plt.subplots(figsize=(12, 2.55), nrows=1, ncols=2)

        for i in range(2):
            plt_df = plot_data[i].loc[plot_data[i]['type'] == col].dropna()
            day_df = plt_df.loc[plt_df['shift'] == 'Day Shift']
            night_df = plt_df.loc[plt_df['shift'] == 'Night Shift']

            sns.lineplot(x="time", y='data', dashes=False, marker="o", hue='shift', data=plt_df, palette="seismic", ax=axes[i])

            # Calculate p value
            # x_tick_list = ['0-4', '4-8', '8-12', '12-16', '16-20', '20-24']
            x_tick_list = ['11PM-3AM', '3AM-7AM', '7AM-11AM', '11AM-3PM', '3PM-7PM', '7PM-11PM']
            for time in range(6):
                tmp_day_df = day_df.loc[day_df['time'] == plot_list[time]]
                tmp_night_df = night_df.loc[night_df['time'] == plot_list[time]]

                stats_value, p = stats.mannwhitneyu(np.array(tmp_day_df.loc[tmp_day_df['type'] == col]['data']), np.array(tmp_night_df.loc[tmp_night_df['type'] == col]['data']))
                x_tick_list[time] = x_tick_list[time] + '\n(p<0.01)' if p < 0.01 else x_tick_list[time] + '\n(p=' + str(p)[:4] + ')'

            axes[i].set_xlim([-0.25, 6 - 0.75])
            axes[i].set_xlabel('')

            if col == 'step': axes[i].set_ylabel('Step Count')
            else: axes[i].set_ylabel('')
            axes[0].set_title('Workday', fontdict={'fontweight': 'bold', 'fontsize': 12})
            axes[1].set_title('Off-day', fontdict={'fontweight': 'bold', 'fontsize': 12})

            axes[i].set_xticks(range(6))
            axes[i].set_yticks(y_tick_list[j])
            axes[i].grid(linestyle='--')
            axes[i].grid(False, axis='y')
            axes[i].set_yticklabels(y_tick_list[j], fontdict={'fontweight': 'bold', 'fontsize': 10.5})
            axes[i].set_ylim(y_lim_list[j])

            plt.rcParams["font.weight"] = "bold"
            plt.rcParams['axes.labelweight'] = 'bold'

            axes[i].set_xticklabels(x_tick_list, fontdict={'fontweight': 'bold', 'fontsize': 10.5})
            axes[i].yaxis.set_tick_params(size=1)

            handles, labels = axes[i].get_legend_handles_labels()
            axes[i].legend(handles=handles[0:], labels=labels[0:], prop={'size': 11, 'weight':'bold'}, loc='upper right')
            for tick in axes[i].yaxis.get_major_ticks():
                tick.label1.set_fontsize(12)
                tick.label1.set_fontweight('bold')

        plt.tight_layout(rect=[0, 0.02, 1, 0.93])
        plt.figtext(0.5, 0.95, title_list[j], ha='center', va='center', fontsize=13.5, fontweight='bold')
        plt.savefig(os.path.join(col + '.png'), dpi=300)
        plt.close()











