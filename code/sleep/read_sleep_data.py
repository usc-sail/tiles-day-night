from util.load_data_basic import *
from util.load_sensor_data import *
from scipy import stats
from datetime import timedelta


def process_main_sleep(sleep_df, timeline_df, realizd_df):

    sleep_df = sleep_df.sort_index()
    save_sleep_df = pd.DataFrame()
    for i in range(len(timeline_df)):
        start_day_str = timeline_df['start'][i]
        end_day_str = timeline_df['end'][i]
        day_sleep_df = sleep_df[start_day_str:end_day_str]

        if len(day_sleep_df) == 0:
            continue

        for j in range(len(day_sleep_df)):
            row_df = day_sleep_df.iloc[j, :]
            start_str = day_sleep_df.index[j]
            end_str = row_df['endTime']

            save_row_df = pd.DataFrame(index=[start_str])
            save_row_df['start'] = pd.to_datetime(start_str).hour + pd.to_datetime(start_str).minute / 60
            save_row_df['end'] = pd.to_datetime(end_str).hour + pd.to_datetime(end_str).minute / 60
            save_row_df['duration'] = (pd.to_datetime(end_str) - pd.to_datetime(start_str)).total_seconds() / 60
            save_row_df['mid'] = pd.to_datetime(start_str) + timedelta(minutes=int(save_row_df['duration']/2))
            save_row_df['mid'] = pd.to_datetime(save_row_df['mid'][0]).hour + pd.to_datetime(save_row_df['mid'][0]).minute / 60

            save_row_df['total_seconds'] = np.nan
            save_row_df['mean_seconds'] = np.nan
            save_row_df['frequency'] = np.nan
            if realizd_df is not None:
                if len(realizd_df) > 700:
                    inertia_end_str = (pd.to_datetime(end_str) + timedelta(hours=2)).strftime(date_time_format)[:-3]
                    inertia_df = realizd_df[end_str:inertia_end_str]
                    if len(inertia_df) != 0:
                        save_row_df['total_seconds'] = np.nansum(inertia_df['duration']) / 60
                        save_row_df['mean_seconds'] = np.nanmean(inertia_df['duration']) / 60
                        save_row_df['frequency'] = len(inertia_df)

            save_row_df['work'] = 1 if timeline_df['work'][i] == 1 else 0

            save_row_df['efficiency'] = row_df['efficiency']
            save_row_df['minutesAsleep'] = (row_df['minutesAsleep'] / row_df['timeInBed']) * 100

            if save_row_df['minutesAsleep'][0] == 0:
                save_row_df['minutesAsleep'] = np.nan

            save_sleep_df = save_sleep_df.append(save_row_df)

    return save_sleep_df


def return_sleep_stats(data_df, shift='day', work='workday'):
    row_df = pd.DataFrame(index=[id])

    if len(data_df) < 5:
        row_df['duration'] = np.nan
        row_df['efficiency'] = np.nan
        row_df['minutesAsleep'] = np.nan
        row_df['total_seconds'] = np.nan
        row_df['mean_seconds'] = np.nan
        row_df['frequency'] = np.nan
        row_df['mid'] = np.nan
        row_df['start'] = np.nan
        row_df['end'] = np.nan
    else:
        row_df['duration'] = np.nanmean(data_df['duration'])
        row_df['efficiency'] = np.nanmean(data_df['efficiency'])
        row_df['minutesAsleep'] = np.nanmean(data_df['minutesAsleep'])
        row_df['total_seconds'] = np.nanmean(data_df['total_seconds'])
        row_df['mean_seconds'] = np.nanmean(data_df['mean_seconds'])
        row_df['frequency'] = np.nanmean(data_df['frequency'])

    if work == 'all':
        workday_sleep = sleep_df.loc[sleep_df['work'] == 1]
        offday_sleep = sleep_df.loc[sleep_df['work'] == 0]

        workday_mid_array = np.array(workday_sleep['mid'])
        offday_mid_array = np.array(offday_sleep['mid'])
        if shift == 'day':
            # workday_mid_array[np.array(workday_mid_array) >= 12] = workday_mid_array[np.array(workday_mid_array) >= 12] - 24
            # offday_mid_array[np.array(offday_mid_array) >= 12] = offday_mid_array[np.array(offday_mid_array) >= 12] - 24
            row_df['mid'] = np.abs(np.nanmedian(workday_mid_array) - np.nanmedian(offday_mid_array)) * 60
        else:
            # offday_mid_array[np.array(offday_mid_array) >= 12] = offday_mid_array[np.array(offday_mid_array) >= 12] - 24
            # workday_mid_array[np.array(workday_mid_array) >= 12] = workday_mid_array[np.array(workday_mid_array) >= 12] - 24
            row_df['mid'] = np.abs(np.nanmedian(workday_mid_array) - np.nanmedian(offday_mid_array)) * 60

        row_df['mid_std'] = np.nanstd(offday_mid_array)
        row_df['duration_diff'] = np.abs(np.nanmedian(np.array(workday_sleep['duration'])) - np.nanmedian(np.array(offday_sleep['duration'])))
    else:
        mid_array = np.array(data_df['mid'])
        start_array = np.array(data_df['start'])
        end_array = np.array(data_df['end'])
        if shift == 'day':
            mid_array[np.array(mid_array) >= 12] = mid_array[np.array(mid_array) >= 12] - 24
            start_array[np.array(start_array) >= 12] = start_array[np.array(start_array) >= 12] - 24

            row_df['start'] = np.nanmedian(start_array) + 24 if np.nanmedian(start_array) < 0 else np.nanmedian(start_array)
            row_df['end'] = np.nanmedian(end_array) + 24 if np.nanmedian(end_array) < 0 else np.nanmedian(end_array)
            row_df['mid'] = np.nanmedian(mid_array)
        else:
            if work == 'offday':
                mid_array[np.array(mid_array) >= 12] = mid_array[np.array(mid_array) >= 12] - 24
                start_array[np.array(start_array) >= 12] = start_array[np.array(start_array) >= 12] - 24
                row_df['start'] = np.nanmedian(start_array) + 24 if np.nanmedian(start_array) < 0 else np.nanmedian(start_array)
                row_df['end'] = np.nanmedian(end_array) + 24 if np.nanmedian(end_array) < 0 else np.nanmedian(end_array)
                row_df['mid'] = np.nanmedian(mid_array) + 24 if np.nanmedian(mid_array) < 0 else np.nanmedian(mid_array)
            else:
                row_df['start'] = np.nanmedian(start_array)
                row_df['end'] = np.nanmedian(end_array)
                row_df['mid'] = np.nanmedian(mid_array)

    row_df['shift'] = shift
    row_df['work'] = work
    return row_df


def print_stats(sleep_df, col, func=stats.kruskal, func_name='K-S'):
    day_nurse_df = sleep_df.loc[sleep_df['shift'] == 'day']
    night_nurse_df = sleep_df.loc[sleep_df['shift'] == 'night']

    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(day_nurse_df[col].dropna()), len(night_nurse_df[col].dropna())))

    # Print
    print('Day shift: median = %.2f, mean = %.2f' % (np.nanmedian(day_nurse_df[col]), np.nanmean(day_nurse_df[col])))
    print('Night shift: median = %.2f, mean = %.2f' % (np.nanmedian(night_nurse_df[col]), np.nanmean(night_nurse_df[col])))

    # stats test
    stat, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path(__file__).parent.absolute().parents[1].joinpath('data')

    # read ground-truth data
    igtb_df = read_AllBasic(root_data_path.joinpath(bucket_str))

    nurse_df = return_nurse_df(igtb_df)
    sleep_stats_df = pd.DataFrame()

    id_list = list(nurse_df['participant_id'])
    id_list.sort()

    for id in id_list:

        shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
        sleep_metadata_df = read_sleep_data(root_data_path.joinpath(bucket_str), id)
        realizd_df = read_realizd_data(root_data_path.joinpath(bucket_str), id)
        if sleep_metadata_df is None:
            continue

        print('Process participant: %s' % (id))

        if Path.exists(root_data_path.joinpath('processed', 'timeline', id + '.csv.gz')) is False:
            continue
        timeline_df = pd.read_csv(root_data_path.joinpath('processed', 'timeline', id + '.csv.gz'), index_col=0)
        main_sleep_df = sleep_metadata_df.loc[sleep_metadata_df['isMainSleep'] == True]

        if len(main_sleep_df) < 10:
            continue

        sleep_df = process_main_sleep(main_sleep_df, timeline_df, realizd_df)

        workday_sleep = sleep_df.loc[sleep_df['work'] == 1]
        offday_sleep = sleep_df.loc[sleep_df['work'] == 0]

        sleep_stats_df = sleep_stats_df.append(return_sleep_stats(sleep_df, shift=shift, work='all'))
        sleep_stats_df = sleep_stats_df.append(return_sleep_stats(workday_sleep, shift=shift, work='workday'))
        sleep_stats_df = sleep_stats_df.append(return_sleep_stats(offday_sleep, shift=shift, work='offday'))

    sleep_stats_df.to_csv(Path.joinpath(Path.cwd(), 'sleep.csv.gz'), compression='gzip')
    compare_cols = ['duration', 'efficiency', 'minutesAsleep', 'total_seconds', 'mean_seconds', 'frequency']

    print('-----------workday-----------')
    all_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'all']
    for col in ['mid', 'duration_diff', 'mid_std']:
        print_stats(all_sleep_sleep, col, func=stats.mannwhitneyu)

    print('-----------workday-----------')
    workday_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'workday']
    for col in compare_cols:
        print_stats(workday_sleep_sleep, col, func=stats.mannwhitneyu)
        # print_stats(sleep_stats_df.loc[sleep_stats_df['shift'] == 'day'], col)

    print('------------offday------------')
    offday_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'offday']
    for col in compare_cols:
        print_stats(offday_sleep_sleep, col, func=stats.mannwhitneyu)
        # print_stats(sleep_stats_df.loc[sleep_stats_df['shift'] == 'night'], col)






