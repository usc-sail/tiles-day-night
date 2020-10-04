from util.load_data_basic import *
from scipy import stats
from scipy.stats import skew


def print_psqi_igtb(day_df, night_df, cols):
    print('\multicolumn{1}{l}{\\textbf{Total PSQI score}} &')
    print('\multicolumn{1}{c}{$%.2f$} &' % (np.mean(day_df['psqi_igtb'])))
    print('\multicolumn{1}{c}{$%.2f$} &' % (np.std(day_df['psqi_igtb'])))
    print('\multicolumn{1}{c}{$%.2f$} &' % (skew(day_df['psqi_igtb'].dropna())))
    print('\multicolumn{1}{c}{$%.2f$} &' % (np.mean(night_df['psqi_igtb'])))
    print('\multicolumn{1}{c}{$%.2f$} &' % (np.std(night_df['psqi_igtb'])))
    print('\multicolumn{1}{c}{$%.2f$} &' % (skew(night_df['psqi_igtb'].dropna())))

    stat, p = stats.ks_2samp(day_df['psqi_igtb'].dropna(), night_df['psqi_igtb'].dropna())

    if p < 0.001:
        print('\multicolumn{1}{c}{\mathbf{<0.001}} \\rule{0pt}{3ex} \\\\')
    elif p < 0.05:
        print('\multicolumn{1}{c}{$\mathbf{%.3f}$} \\rule{0pt}{3ex} \\\\' % (p))
    else:
        print('\multicolumn{1}{c}{$%.3f$} \\rule{0pt}{3ex} \\\\' % (p))
    print('\n')

    for col in cols:

        if 'dysfunction' in col:
            print_col = 'Daytime dysfunction'
        elif 'med' in col:
            print_col = 'Sleep medication'
        elif 'sub' in col:
            print_col = 'Subjective sleep quality'
        elif 'tency' in col:
            print_col = 'Sleep latency'
        elif 'fficiency' in col:
            print_col = 'Sleep efficiency'
        elif 'disturbance' in col:
            print_col = 'Sleep disturbance'
        else:
            print_col = 'Sleep duration'

        print('\multicolumn{1}{l}{\hspace{0.5cm}' + print_col + '} &')
        print('\multicolumn{1}{c}{$%.2f$} &' % (np.mean(day_df[col])))
        print('\multicolumn{1}{c}{$%.2f$} &' % (np.std(day_df[col])))
        print('\multicolumn{1}{c}{$%.2f$} &' % (skew(day_df[col])))
        print('\multicolumn{1}{c}{$%.2f$} &' % (np.mean(night_df[col])))
        print('\multicolumn{1}{c}{$%.2f$} &' % (np.std(night_df[col])))
        print('\multicolumn{1}{c}{$%.2f$} &' % (skew(night_df[col])))

        stat, p = stats.ks_2samp(day_df[col].dropna(), night_df[col].dropna())

        if p < 0.001:
            print('\multicolumn{1}{c}{\mathbf{<0.001}} \\rule{0pt}{3ex} \\\\')
        elif p < 0.05:
            print('\multicolumn{1}{c}{$\mathbf{%.3f}$} \\rule{0pt}{3ex} \\\\' % (p))
        else:
            print('\multicolumn{1}{c}{$%.3f$} \\rule{0pt}{3ex} \\\\' % (p))
        print('\n')


def print_stats(igtb_df, col, func=stats.kruskal, func_name='K-S'):
    # shift_pre-study
    igtb_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    day_nurse_df = igtb_df.loc[igtb_df['Shift'] == 'Day shift']
    night_nurse_df = igtb_df.loc[igtb_df['Shift'] == 'Night shift']

    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(day_nurse_df[col].dropna()), len(night_nurse_df[col].dropna())))

    # Print
    # print('Total: mean = %.2f, std = %.2f, range is %.3f - %.3f' % (np.mean(igtb_df[col]), np.std(igtb_df[col]), np.min(igtb_df[col]), np.max(igtb_df[col])))
    print('Day shift: mean = %.2f, std = %.2f' % (np.nanmean(day_nurse_df[col]), np.nanstd(day_nurse_df[col])))
    # print('Day shift: range is %.3f - %.3f' % (np.min(day_nurse_df[col]), np.max(day_nurse_df[col])))
    # print('Day shift: skew = %.3f' % (skew(day_nurse_df[col])))

    print('Night shift: mean = %.2f, std = %.2f' % (np.nanmean(night_nurse_df[col]), np.nanstd(night_nurse_df[col])))
    # print('Night shift: range is %.3f - %.3f' % (np.min(night_nurse_df[col]), np.max(night_nurse_df[col])))
    # print('Night shift: skew = %.3f' % (skew(night_nurse_df[col])))

    # stats test
    stat, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path(__file__).parent.absolute().parents[1].joinpath('data', bucket_str)

    igtb_df = read_AllBasic(root_data_path)
    psqi_raw_igtb = read_PSQI_Raw(root_data_path)
    igtb_raw = read_IGTB_Raw(root_data_path)

    for participant_id in list(igtb_df.participant_id):
        nurse = str(igtb_df.loc[igtb_df['participant_id'] == participant_id].currentposition[0])
        shift = igtb_df.loc[igtb_df['participant_id'] == participant_id].Shift[0]
        job_str = 'nurse' if nurse == 'A' else 'non_nurse'
        shift_str = 'day' if shift == 'Day shift' else 'night'
        uid = list(igtb_df.loc[igtb_df['participant_id'] == participant_id].index)[0]

        igtb_df.loc[uid, 'job'] = job_str
        igtb_df.loc[uid, 'shift'] = shift_str

        sitting_on_weekdays = int(igtb_raw.loc[uid, 'ipaq26'])
        if sitting_on_weekdays < 10 or sitting_on_weekdays == 999:
            sitting_on_weekdays = np.nan
        # elif sitting_on_weekdays <= 15:
            # sitting_on_weekdays = sitting_on_weekdays * 60
        #    sitting_on_weekdays = np.nan

        sitting_on_weekend = int(igtb_raw.loc[uid, 'ipaq27'])
        if sitting_on_weekend < 10 or sitting_on_weekend == 999:
            sitting_on_weekend = np.nan
        # elif sitting_on_weekend <= 30:
            # sitting_on_weekend = sitting_on_weekend * 60
        #    sitting_on_weekend = np.nan

        walk_during_work = str(igtb_raw.loc[uid, 'ipaq7'])
        if walk_during_work == 'nan':
            walk_during_work = 0
        if int(walk_during_work) < 10 or int(walk_during_work) == 999:
            walk_during_work = np.nan

        walk_during_off = str(igtb_raw.loc[uid, 'ipaq21'])
        if walk_during_off == 'nan':
            walk_during_off = 0
        if int(walk_during_off) < 10 or int(walk_during_off) == 999:
            walk_during_off = np.nan

        igtb_df.loc[uid, 'sitting_weekday'] = sitting_on_weekdays
        igtb_df.loc[uid, 'sitting_weekend'] = sitting_on_weekend
        igtb_df.loc[uid, 'walk_during_work'] = float(walk_during_work)
        igtb_df.loc[uid, 'walk_during_off'] = float(walk_during_off)

        for col in list(psqi_raw_igtb.columns):
            igtb_df.loc[uid, col] = psqi_raw_igtb.loc[uid, col]

    psqi_col = ['psqi', 'sitting_weekday', 'sitting_weekend', 'walk_during_work', 'walk_during_off']
    psqi_col = psqi_col + list(psqi_raw_igtb.columns)
    for col in psqi_col:
        # print_stats(igtb_df, col, func=stats.ttest_ind, func_name='t_test')
        print_stats(igtb_df, col, func=stats.kruskal)

    affect_col = ['stai', 'pan_PosAffect', 'pan_NegAffect',
                  'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness']

    # affect_col = ['stai', 'pan_PosAffect', 'pan_NegAffect']

    for col in affect_col:
        print_stats(igtb_df, col, func=stats.kruskal)
    # print_psqi_igtb(day_nurse_df, night_nurse_df, list(psqi_raw_igtb.columns))
