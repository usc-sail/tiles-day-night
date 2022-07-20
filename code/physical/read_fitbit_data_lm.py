from util.load_data_basic import *
from util.load_sensor_data import *
from datetime import timedelta
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns



def process_fitbit(fitbit_df, timeline_df, maximum_hr, resting_hr, shift='day'):

    fitbit_df = fitbit_df.sort_index()
    daily_stats_df = pd.DataFrame()

    for i in range(len(timeline_df)):
        start_day_str = timeline_df['start'][i]
        end_day_str = timeline_df['end'][i]

        fitbit_day_df = fitbit_df[start_day_str:end_day_str]
        fitbit_day_df = fitbit_day_df.dropna()

        # have 60% of the data, otherwise skip
        if len(fitbit_day_df) < 1440 * 0.6:
            continue

        fitbit_day_df = fitbit_day_df.loc[fitbit_day_df['heart_rate'] < maximum_hr]
        row_df = pd.DataFrame(index=[start_day_str])
        row_df['work'] = 'work' if timeline_df['work'][i] == 1 else 'off'

        # Daily HR region
        row_df['rest'] = np.nanmean((0.5 * maximum_hr > np.array(fitbit_day_df['heart_rate'])))
        row_df['moderate'] = np.nanmean((0.5 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.7 * maximum_hr))
        row_df['vigorous'] = np.nanmean((0.7 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.85 * maximum_hr))
        row_df['vigorous_min'] = np.nansum((0.7 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])) & (np.array(fitbit_day_df['heart_rate']) < 0.85 * maximum_hr))
        row_df['intense'] = np.nanmean((0.85 * maximum_hr <= np.array(fitbit_day_df['heart_rate'])))
        row_df['step'] = np.nanmean(fitbit_day_df['StepCount'])
        row_df['step_ratio'] = np.nanmean(fitbit_day_df['StepCount'] > 0)
        row_df['run_ratio'] = np.nanmean(fitbit_day_df['StepCount'] > 50)
        daily_stats_df = daily_stats_df.append(row_df)

    work_list = list(set(list(daily_stats_df['work'])))
    final_df = pd.DataFrame()
    for work in work_list:
        data_df = daily_stats_df.loc[daily_stats_df['work'] == work]
        if len(data_df) < 5:
            continue
        row_df = pd.DataFrame(index=[work])
        row_df['work'] = work
        row_df['rest'] = np.nanmean(data_df['rest'])
        row_df['vigorous'] = np.nanmean(data_df['vigorous'])
        row_df['step_ratio'] = np.nanmean(data_df['step_ratio'])
        row_df['run_ratio'] = np.nanmean(data_df['run_ratio'])
        row_df['vigorous_min'] = np.nanmean(data_df['vigorous_min'])
        final_df = pd.concat([final_df, row_df])

    return final_df


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    # read ground-truth data
    igtb_df = read_AllBasic(root_data_path)
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
            stai = igtb_df.loc[igtb_df['participant_id'] == id].stai[0]
            pan_PosAffect = igtb_df.loc[igtb_df['participant_id'] == id].pan_PosAffect[0]
            pan_NegAffect = igtb_df.loc[igtb_df['participant_id'] == id].pan_NegAffect[0]
            swls = igtb_df.loc[igtb_df['participant_id'] == id].swls[0]
            psqi = igtb_df.loc[igtb_df['participant_id'] == id].psqi[0]
            bfi_Neuroticism = igtb_df.loc[igtb_df['participant_id'] == id].bfi_Neuroticism[0]

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
            daily_df.loc[:, 'stai'] = stai
            daily_df.loc[:, 'pan_PosAffect'] = pan_PosAffect
            daily_df.loc[:, 'pan_NegAffect'] = pan_NegAffect
            daily_df.loc[:, 'swls'] = swls
            daily_df.loc[:, 'psqi'] = psqi
            daily_df.loc[:, 'bfi_Neuroticism'] = bfi_Neuroticism

            fitbit_stats_df = pd.concat([fitbit_stats_df, daily_df])

        work_stats = fitbit_stats_df.loc[fitbit_stats_df['work'] == 'work']
        off_stats = fitbit_stats_df.loc[fitbit_stats_df['work'] == 'off']
        work_stats.to_csv(Path.joinpath(Path.cwd(), 'stats_work_lm.csv.gz'), compression='gzip')
        off_stats.to_csv(Path.joinpath(Path.cwd(), 'stats_off_lm.csv.gz'), compression='gzip')
        fitbit_stats_df.to_csv(Path.joinpath(Path.cwd(), 'stats_lm.csv.gz'), compression='gzip')






