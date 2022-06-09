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

        if timeline_df['work'][i] == 1:
            # sleep can only happen outside work time
            tmp_start = (pd.to_datetime(start_day_str) + timedelta(hours=12)).strftime(date_time_format)[:-3]
            day_sleep_df = sleep_df[tmp_start:end_day_str]
        else:
            day_sleep_df = sleep_df[start_day_str:end_day_str]

        if len(day_sleep_df) == 0:
            continue

        for j in range(len(day_sleep_df)):
            row_df = day_sleep_df.iloc[j, :]
            start_str = day_sleep_df.index[j]
            end_str = row_df['endTime']

            if (pd.to_datetime(end_str) - pd.to_datetime(start_str)).total_seconds() / 60 < 120:
                continue

            save_row_df = pd.DataFrame(index=[start_str])
            save_row_df['start'] = pd.to_datetime(start_str).hour + pd.to_datetime(start_str).minute / 60
            save_row_df['end'] = pd.to_datetime(end_str).hour + pd.to_datetime(end_str).minute / 60
            save_row_df['duration'] = (pd.to_datetime(end_str) - pd.to_datetime(start_str)).total_seconds() / 60
            save_row_df['mid'] = pd.to_datetime(start_str) + timedelta(minutes=int(save_row_df['duration']/2))
            save_row_df['mid'] = pd.to_datetime(save_row_df['mid'][0]).hour + pd.to_datetime(save_row_df['mid'][0]).minute / 60

            save_row_df['total_seconds'] = np.nan
            save_row_df['mean_seconds'] = np.nan
            save_row_df['frequency'] = np.nan
            '''
            if realizd_df is not None:
                if len(realizd_df) > 700:
                    inertia_end_str = (pd.to_datetime(end_str) + timedelta(hours=2)).strftime(date_time_format)[:-3]
                    inertia_df = realizd_df[end_str:inertia_end_str]
                    if len(inertia_df) != 0:
                        save_row_df['total_seconds'] = np.nansum(inertia_df['duration']) / 60
                        save_row_df['mean_seconds'] = np.nanmean(inertia_df['duration']) / 60
                        save_row_df['frequency'] = len(inertia_df)
            '''

            save_row_df['work'] = 1 if timeline_df['work'][i] == 1 else 0

            save_row_df['efficiency'] = row_df['efficiency']
            save_row_df['minutesAsleep'] = (row_df['minutesAsleep'] / row_df['timeInBed']) * 100
            if save_row_df['minutesAsleep'][0] == 0:
                save_row_df['minutesAsleep'] = np.nan

            save_sleep_df = save_sleep_df.append(save_row_df)

    return save_sleep_df


def return_sleep_stats(data_df, lang=0, shift='day', work='workday'):
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
        # row_df['total_seconds'] = np.nanmean(data_df['total_seconds'])
        # row_df['mean_seconds'] = np.nanmean(data_df['mean_seconds'])
        # row_df['frequency'] = np.nanmean(data_df['frequency'])

        if work == 'all':
            workday_sleep = sleep_df.loc[sleep_df['work'] == 1]
            offday_sleep = sleep_df.loc[sleep_df['work'] == 0]

            if len(workday_sleep) < 5 or len(offday_sleep) < 5:
                print('not enough data')
            else:
                workday_mid_array = np.array(workday_sleep['mid'])
                offday_mid_array = np.array(offday_sleep['mid'])
                if shift == 'day':
                    row_df['mid'] = np.abs(np.nanmedian(workday_mid_array) - np.nanmedian(offday_mid_array)) * 60
                else:
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
    row_df['lang'] = lang
    row_df['work'] = work
    return row_df


def print_stats(sleep_df, col, func=stats.kruskal, func_name='K-S', demo='lang'):

    if demo == 'lang':
        first_df = sleep_df.loc[sleep_df['lang'] == 1]
        second_df = sleep_df.loc[sleep_df['lang'] == 2]
    else:
        first_df = sleep_df.loc[sleep_df['shift'] == 'day']
        second_df = sleep_df.loc[sleep_df['shift'] == 'night']

    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(first_df[col].dropna()), len(second_df[col].dropna())))

    # Print
    print('Day shift: median = %.2f, mean = %.2f' % (np.nanmedian(first_df[col]), np.nanmean(first_df[col])))
    print('Night shift: median = %.2f, mean = %.2f' % (np.nanmedian(second_df[col]), np.nanmean(second_df[col])))

    # stats test
    stat, p = func(first_df[col].dropna(), second_df[col].dropna())
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))


def print_latex(sleep_df, col, func=stats.kruskal, print_col='', end_str='\\rule{0pt}{2ex} \\\\'):
    # shift_pre-study
    day_nurse_df = sleep_df.loc[sleep_df['shift'] == 'day']
    night_nurse_df = sleep_df.loc[sleep_df['shift'] == 'night']

    if 'workdays' in print_col:
        if 'duration' in col:
            print('\multicolumn{1}{l}{\\textbf{Sleep Time (min)}} & & & & & & & \\rule{0pt}{2.25ex} \\\\')
        elif 'minutesAsleep' in col:
            print('\multicolumn{1}{l}{\\textbf{Asleep Ratio (\\%)}} & & & & & & & \\rule{0pt}{2.25ex} \\\\')
        else:
            print('\multicolumn{1}{l}{\\textbf{SI (min)}} & & & & & & & \\rule{0pt}{2.25ex} \\\\')
        print()

    if 'On' in print_col:
        print('\multicolumn{1}{l}{\hspace{0.3cm}{%s}} &' % print_col)
    else:
        print('\multicolumn{1}{l}{\\textbf{%s}} &' % print_col)

    print('\multicolumn{1}{c}{$%d$} &' % (len(day_nurse_df[col].dropna())))
    print('\multicolumn{1}{c}{$%.1f$ ($%.1f$)} &' % (np.nanmedian(day_nurse_df[col]), np.nanmean(day_nurse_df[col])))
    print('\multicolumn{1}{c}{$%.1f$-$%.1f$} &' % (np.nanmin(day_nurse_df[col]), np.nanmax(day_nurse_df[col])))
    print('\multicolumn{1}{c}{$%d$} &' % (len(night_nurse_df[col].dropna())))
    print('\multicolumn{1}{c}{$%.1f$ ($%.1f$)} &' % (np.nanmedian(night_nurse_df[col]), np.nanmean(night_nurse_df[col])))
    print('\multicolumn{1}{c}{$%.1f$-$%.1f$} &' % (np.nanmin(night_nurse_df[col]), np.nanmax(night_nurse_df[col])))

    # stats test
    u_stats, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())

    if p < 0.01:
        print('\multicolumn{1}{c}{$\mathbf{<0.01^{**}}$} &')
    elif p < 0.05:
        print('\multicolumn{1}{c}{$\mathbf{%.3f^*}$} &' % (p))
    elif p < 0.10:
        print('\multicolumn{1}{c}{$\mathbf{%.3f^\dagger}$} &' % (p))
    else:
        print('\multicolumn{1}{c}{$%.3f$} &' % (p))

    print('\multicolumn{1}{c}{$%.1f$} %s' % (u_stats, end_str))
    print()


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    # read ground-truth data
    igtb_df = read_AllBasic(root_data_path)

    nurse_df = return_nurse_df(igtb_df)
    sleep_stats_df = pd.DataFrame()

    id_list = list(nurse_df['participant_id'])
    id_list.sort()

    if Path.exists(Path.joinpath(Path.cwd(), 'sleep1.csv.gz')) is False:
        for id in id_list:

            shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
            lang = nurse_df.loc[nurse_df['participant_id'] == id].lang[0]
            sleep_metadata_df = read_sleep_data(root_data_path, id)
            realizd_df = read_realizd_data(root_data_path, id)

            gender = igtb_df.loc[igtb_df['participant_id'] == id].gender[0]
            age = igtb_df.loc[igtb_df['participant_id'] == id].age[0]
            stai = igtb_df.loc[igtb_df['participant_id'] == id].stai[0]
            pan_PosAffect = igtb_df.loc[igtb_df['participant_id'] == id].pan_PosAffect[0]
            pan_NegAffect = igtb_df.loc[igtb_df['participant_id'] == id].pan_NegAffect[0]
            swls = igtb_df.loc[igtb_df['participant_id'] == id].swls[0]
            psqi = igtb_df.loc[igtb_df['participant_id'] == id].psqi[0]
            rand_GeneralHealth = igtb_df.loc[igtb_df['participant_id'] == id].rand_GeneralHealth[0]
            rand_EnergyFatigue = igtb_df.loc[igtb_df['participant_id'] == id].rand_EnergyFatigue[0]

            gender_str = 'Male' if gender == 1 else 'Female'
            age_str = '< 40 Years' if age < 40 else '>= 40 Years'

            if sleep_metadata_df is None:
                continue

            print('Process participant: %s' % (id))
            if Path.exists(Path.cwd().joinpath('..', '..', '..', 'data', 'processed', 'timeline', id + '.csv.gz')) is False:
                continue
            timeline_df = pd.read_csv(Path.cwd().joinpath('..', '..', '..', 'data', 'processed', 'timeline', id + '.csv.gz'), index_col=0)
            main_sleep_df = sleep_metadata_df.loc[sleep_metadata_df['isMainSleep'] == True]

            if len(main_sleep_df) == 0:
                continue

            sleep_df = process_main_sleep(main_sleep_df, timeline_df, realizd_df)

            if len(sleep_df) == 0:
                continue
            workday_sleep = sleep_df.loc[sleep_df['work'] == 1]
            offday_sleep = sleep_df.loc[sleep_df['work'] == 0]

            tmp_df = pd.DataFrame()
            tmp_df = tmp_df.append(return_sleep_stats(sleep_df, lang=lang, shift=shift, work='all'))
            tmp_df = tmp_df.append(return_sleep_stats(workday_sleep, lang=lang, shift=shift, work='workday'))
            tmp_df = tmp_df.append(return_sleep_stats(offday_sleep, lang=lang, shift=shift, work='offday'))

            if len(tmp_df) == 0:
                continue
            tmp_df.loc[:, 'id'] = id
            tmp_df.loc[:, 'age'] = age_str
            tmp_df.loc[:, 'gender'] = gender_str
            tmp_df.loc[:, 'stai'] = stai
            tmp_df.loc[:, 'pan_PosAffect'] = pan_PosAffect
            tmp_df.loc[:, 'pan_NegAffect'] = pan_NegAffect
            tmp_df.loc[:, 'swls'] = swls
            tmp_df.loc[:, 'psqi'] = psqi
            tmp_df.loc[:, 'rand_GeneralHealth'] = rand_GeneralHealth
            tmp_df.loc[:, 'rand_EnergyFatigue'] = rand_EnergyFatigue

            sleep_stats_df = pd.concat([sleep_stats_df, tmp_df])

        sleep_stats_df.to_csv(Path.joinpath(Path.cwd(), 'sleep.csv.gz'), compression='gzip')
    else:
        sleep_stats_df = pd.read_csv(Path.joinpath(Path.cwd(), 'sleep.csv.gz'), index_col=0)

    # compare_cols = ['duration', 'efficiency', 'minutesAsleep', 'total_seconds', 'mean_seconds', 'frequency']
    # shift_pre-study
    # sleep_stats_df = sleep_stats_df.loc[sleep_stats_df['shift'] == 'day']

    workday_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'workday']
    offday_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'offday']

    compare_cols = ['duration', 'minutesAsleep', 'total_seconds']
    for col in compare_cols:
        print_latex(workday_sleep_sleep, col, print_col='On workdays', func=stats.mannwhitneyu)
        print_latex(offday_sleep_sleep, col, print_col='On off-days', func=stats.mannwhitneyu)
        # print_stats(sleep_stats_df.loc[sleep_stats_df['shift'] == 'night'], col)
        # print_stats(sleep_stats_df.loc[sleep_stats_df['shift'] == 'day'], col)

    all_sleep_sleep = sleep_stats_df.loc[sleep_stats_df['work'] == 'all']
    # for col in ['mid', 'duration_diff', 'mid_std']:
    for col in ['mid']:
        # print_stats(all_sleep_sleep, col, func=stats.mannwhitneyu, demo='lang')
        print_latex(all_sleep_sleep, col, print_col='$\\Delta\\mathbf{MS}$', func=stats.mannwhitneyu)





