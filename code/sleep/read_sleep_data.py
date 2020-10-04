from util.load_data_basic import *
from util.load_sensor_data import *
from scipy import stats
from datetime import timedelta


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
            start_str = (pd.to_datetime(date_str).replace(hour=7)).strftime(date_time_format)[:-3]
            end_str = (pd.to_datetime(date_str).replace(hour=7) + timedelta(hours=12)).strftime(date_time_format)[:-3]
            row_df = pd.DataFrame(index=[start_str])
            row_df['start'] = start_str
            row_df['end'] = end_str
            save_df = save_df.append(row_df)
        else:
            if i + 1 < len(work_df):
                if (pd.to_datetime(work_df.index[i+1]) - pd.to_datetime(work_df.index[i])).total_seconds() < 2 * 3600 * 24:
                    start_str = (pd.to_datetime(date_str).replace(hour=19)).strftime(date_time_format)[:-3]
                    end_str = (pd.to_datetime(date_str).replace(hour=19) + timedelta(hours=12)).strftime(date_time_format)[:-3]
                    row_df = pd.DataFrame(index=[start_str])
                    row_df['start'] = start_str
                    row_df['end'] = end_str
                    save_df = save_df.append(row_df)

    return save_df


def process_main_sleep(sleep_df, workday_timeline_df, days_at_work_df):

    save_sleep_df = pd.DataFrame()
    days_at_work_df = days_at_work_df.fillna(0)
    for i in range(len(sleep_df)):
        row_df = sleep_df.iloc[i, :]
        start_str = row_df['startTime']
        end_str = row_df['endTime']

        start_off_list = list(pd.to_datetime(workday_timeline_df['start']) - pd.to_datetime(end_str))
        # end_off_list = list(pd.to_datetime(start_str) - pd.to_datetime(workday_timeline_df['end']))

        save_row_df = pd.DataFrame(index=[start_str])
        save_row_df['start'] = pd.to_datetime(start_str).hour + pd.to_datetime(start_str).minute / 60
        save_row_df['end'] = pd.to_datetime(end_str).hour + pd.to_datetime(end_str).minute / 60
        save_row_df['duration'] = (pd.to_datetime(end_str) - pd.to_datetime(start_str)).total_seconds() / 60
        if float(days_at_work_df.loc[row_df['dateOfSleep'], id]) == 1.0:
            save_row_df['workday'] = 1
        else:
            save_row_df['workday'] = 0

        save_row_df['efficiency'] = row_df['efficiency']
        save_row_df['minutesAsleep'] = row_df['minutesAsleep'] / row_df['timeInBed']

        save_row_df['before_work'] = 0
        for j in range(len(start_off_list)):
            if 0 < start_off_list[j].total_seconds() < 6 * 3600:
                save_row_df['before_work'] = 1
        save_sleep_df = save_sleep_df.append(save_row_df)

    return save_sleep_df


def return_sleep_stats(sleep_df, shift='day', work='workday'):
    row_df = pd.DataFrame(index=[id])
    row_df['duration'] = np.nanmean(sleep_df['duration'])
    row_df['efficiency'] = np.nanmean(sleep_df['efficiency'])
    row_df['minutesAsleep'] = np.nanmean(sleep_df['minutesAsleep'])
    row_df['shift'] = shift
    row_df['work'] = work
    return row_df


def print_stats(sleep_df, col, func=stats.kruskal, func_name='K-S'):
    day_nurse_df = sleep_df.loc[sleep_df['shift'] == 'day']
    night_nurse_df = sleep_df.loc[sleep_df['shift'] == 'night']

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
    days_at_work_df = read_days_at_work(root_data_path)

    nurse_df = return_nurse_df(igtb_df)
    # day_nurse_id = list(nurse_df.loc[nurse_df['Shift'] == 'Day shift'].participant_id)
    # night_nurse_id = list(nurse_df.loc[nurse_df['Shift'] == 'Night shift'].participant_id)

    day_sleep_start_workday_list, day_sleep_end_workday_list = [], []
    day_sleep_start_offday_list, day_sleep_end_offday_list = [], []

    night_sleep_start_workday_list, night_sleep_end_workday_list = [], []
    night_sleep_start_offday_list, night_sleep_end_offday_list = [], []

    sleep_stats_df = pd.DataFrame()

    id_list = list(nurse_df['participant_id'])
    id_list.sort()
    for id in id_list:

        shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
        sleep_metadata_df = read_sleep_data(root_data_path, id)
        if sleep_metadata_df is None:
            continue

        main_sleep_df = sleep_metadata_df.loc[sleep_metadata_df['isMainSleep'] == True]
        workday_timeline_df = convert_days_at_work(days_at_work_df, id, shift=shift)

        if len(main_sleep_df) < 14 or len(workday_timeline_df) < 14:
            continue

        sleep_df = process_main_sleep(main_sleep_df, workday_timeline_df, days_at_work_df)

        workday_sleep = sleep_df.loc[sleep_df['before_work'] == 1]
        offday_sleep = sleep_df.loc[sleep_df['before_work'] == 0]

        sleep_stats_df = sleep_stats_df.append(return_sleep_stats(sleep_df, shift=shift, work='all'))
        sleep_stats_df = sleep_stats_df.append(return_sleep_stats(workday_sleep, shift=shift, work='workday'))
        sleep_stats_df = sleep_stats_df.append(return_sleep_stats(offday_sleep, shift=shift, work='offday'))

        if shift == 'day':
            for i in range(len(workday_sleep)):
                day_sleep_start_workday_list.append(workday_sleep['start'][i])
                day_sleep_end_workday_list.append(workday_sleep['end'][i])
            for i in range(len(offday_sleep)):
                day_sleep_start_offday_list.append(offday_sleep['start'][i])
                day_sleep_end_offday_list.append(offday_sleep['end'][i])
        else:
            for i in range(len(workday_sleep)):
                night_sleep_start_workday_list.append(workday_sleep['start'][i])
                night_sleep_end_workday_list.append(workday_sleep['end'][i])
            for i in range(len(offday_sleep)):
                night_sleep_start_offday_list.append(offday_sleep['start'][i])
                night_sleep_end_offday_list.append(offday_sleep['end'][i])

    compare_cols = ['duration', 'efficiency', 'minutesAsleep']
    print('-----------workday-----------')
    workday_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'workday']
    for col in compare_cols:
        print_stats(workday_sleep_sleep, col)
        # print_stats(sleep_stats_df.loc[sleep_stats_df['shift'] == 'day'], col)

    print('------------offday------------')
    offday_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'offday']
    for col in compare_cols:
        print_stats(offday_sleep_sleep, col)
        # print_stats(sleep_stats_df.loc[sleep_stats_df['shift'] == 'night'], col)






