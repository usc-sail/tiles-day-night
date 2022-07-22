from util.load_data_basic import *
from util.load_sensor_data import *
from datetime import timedelta
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns

# 0 is actually 11pm - 3am, ..., 5 is 7pm - 11pm
# day starts with 2, which is 7am -11am, night starts with 5, which is 7pm - 11pm
day_map = {0: '3rd', 1: '4th', 2: '5th', 3: '6th', 4: '1st', 5: '2nd'}
night_map = {0: '6th', 1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th'}

# 0 is actually 1am - 7am, ..., 3 is 7pm-1am
# day_map = {0: '2nd', 1: '3rd', 2: '4th', 3: '1st'}
# night_map = {0: '4th', 1: '1st', 2: '2nd', 3: '3rd'}


num_seg = 6
seg_size = int(24 / num_seg)

def process_fitbit(fitbit_df, timeline_df, maximum_hr, resting_hr, shift='day'):

    fitbit_df = fitbit_df.sort_index()
    daily_stats_df = pd.DataFrame()

    for i in range(len(timeline_df)):
        start_day_str = timeline_df['start'][i]
        end_day_str = timeline_df['end'][i]

        fitbit_day_df = fitbit_df[start_day_str:end_day_str]
        fitbit_day_df = fitbit_day_df.dropna()

        tmp_df = pd.DataFrame()
        for j in range(num_seg):
            reg_start_str = (pd.to_datetime(start_day_str) + timedelta(hours=j * seg_size)).strftime(date_time_format)[:-3]
            reg_end_str = (pd.to_datetime(start_day_str) + timedelta(hours=j * seg_size + seg_size - 1, minutes=59)).strftime(date_time_format)[:-3]

            reg_df = fitbit_day_df[reg_start_str:reg_end_str]

            if len(reg_df) < seg_size * 60 * 0.6:
                continue

            row_df = pd.DataFrame(index=[start_day_str])
            row_df['work'] = 'work' if timeline_df['work'][i] == 1 else 'off'
            row_df['time'] = day_map[j] if shift == 'day' else night_map[j]

            # Daily HR region
            row_df['rest'] = np.nanmean((0.5 * maximum_hr > np.array(reg_df['heart_rate'])))
            row_df['moderate'] = np.nanmean((0.5 * maximum_hr <= np.array(reg_df['heart_rate'])) & (np.array(reg_df['heart_rate']) < 0.7 * maximum_hr))
            row_df['vigorous'] = np.nanmean((0.7 * maximum_hr <= np.array(reg_df['heart_rate'])) & (np.array(reg_df['heart_rate']) < 0.85 * maximum_hr))
            row_df['intense'] = np.nanmean((0.85 * maximum_hr <= np.array(reg_df['heart_rate'])))
            row_df['step'] = np.nanmean(reg_df['StepCount'])
            row_df['step_ratio'] = np.nanmean(reg_df['StepCount'] > 0)
            row_df['run_ratio'] = np.nanmean(reg_df['StepCount'] > 10)
            tmp_df = tmp_df.append(row_df)
        # if len(tmp_df) != num_seg:
        #    continue
        daily_stats_df = pd.concat([daily_stats_df, tmp_df])

    # return daily_stats_df

    final_df = pd.DataFrame()
    time_list = list(set(list(daily_stats_df['time'])))
    work_list = list(set(list(daily_stats_df['work'])))
    for work in work_list:
        work_df = daily_stats_df.loc[daily_stats_df['work'] == work]
        if len(work_df) == 0:
            continue

        tmp_df = pd.DataFrame()
        for time in time_list:
            data_df = work_df.loc[work_df['time'] == time]
            if len(data_df) == 0:
                continue
            row_df = pd.DataFrame(index=[work])
            row_df['work'] = work
            row_df['time'] = time
            row_df['rest'] = np.nanmean(data_df['rest'])
            row_df['step_ratio'] = np.nanmean(data_df['step_ratio'])
            row_df['run_ratio'] = np.nanmean(data_df['run_ratio'])

            tmp_df = pd.concat([tmp_df, row_df])
        if len(tmp_df) != num_seg:
            continue
        final_df = pd.concat([final_df, tmp_df])

    return final_df


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    # read ground-truth data
    # please contact the author to access: igtb_day_night.csv.gz
    if Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz').exists() == False:
        igtb_df = read_AllBasic(root_data_path)
        igtb_df.to_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'))
    igtb_df = pd.read_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'), index_col=0)
    nurse_df = return_nurse_df(igtb_df)

    id_list = list(nurse_df['participant_id'])
    id_list.sort()

    if Path.exists(Path.joinpath(Path.cwd(), 'stats_lm1.csv.gz')) is True:
        fitbit_stats_df = pd.read_csv('stats_lm.csv.gz', index_col=0)
    else:
        fitbit_stats_df = pd.DataFrame()
        for id in id_list:
            print('Process participant: %s' % (id))
            shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
            gender = igtb_df.loc[igtb_df['participant_id'] == id].gender[0]
            age = igtb_df.loc[igtb_df['participant_id'] == id].age[0]

            gender_str = 'Male' if gender == 1 else 'Female'
            age_str = '< 40 Years' if age < 40 else '>= 40 Years'

            fitbit_df = read_prossed_fitbit_data(Path.joinpath(Path.cwd().parent.parent, 'data'), id)
            summary_df = read_fitbit_daily_data(root_data_path, id)

            if fitbit_df is None:
                continue

            # heart rate basic
            maximum_hr = 220 - age
            resting_hr = int(np.nanmean(summary_df['RestingHeartRate']))

            if Path.exists(Path.cwd().joinpath('..', '..', '..', 'data', 'processed', 'timeline', id + '.csv.gz')) is False:
                continue
            timeline_df = pd.read_csv(Path.cwd().joinpath('..', '..', '..', 'data', 'processed', 'timeline', id + '.csv.gz'), index_col=0)

            # workday_sum_df, offday_sum_df, daily_sum_df = process_fitbit(fitbit_df, timeline_df, maximum_hr, resting_hr, shift)
            daily_df = process_fitbit(fitbit_df, timeline_df, maximum_hr, resting_hr, shift)

            if len(daily_df) == 0:
                continue
            daily_df.loc[:, 'id'] = id
            daily_df.loc[:, 'age'] = age_str
            daily_df.loc[:, 'gender'] = gender_str
            daily_df.loc[:, 'shift'] = shift

            fitbit_stats_df = pd.concat([fitbit_stats_df, daily_df])

        work_stats = fitbit_stats_df.loc[fitbit_stats_df['work'] == 'work']
        off_stats = fitbit_stats_df.loc[fitbit_stats_df['work'] == 'off']
        work_stats.to_csv(Path.joinpath(Path.cwd(), 'diurnal_work_lm_' + str(num_seg) + '.csv.gz'), compression='gzip')
        off_stats.to_csv(Path.joinpath(Path.cwd(), 'diurnal_off_lm_' + str(num_seg) + '.csv.gz'), compression='gzip')
        fitbit_stats_df.to_csv(Path.joinpath(Path.cwd(), 'diurnal_lm_' + str(num_seg) + '.csv.gz'), compression='gzip')






