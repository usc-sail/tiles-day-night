from util.load_data_basic import *
from scipy import stats
from scipy.stats import skew


col_dict = {'stai': 'Anxiety', 'pan_PosAffect': 'Positive Affect', 'pan_NegAffect': 'Negative Affect',
            'rand_GeneralHealth': 'General Health', 'rand_EnergyFatigue': 'Energy',
            'swls': 'Life Satisfaction', 'pss': 'Perceived Stress',
            'waaq': 'Acceptance', 'uwes': 'Work Engagement',
            'bfi_Neuroticism': 'Neuroticism', 'bfi_Conscientiousness': 'Conscientiousness',
            'bfi_Extraversion': 'Extraversion', 'bfi_Agreeableness': 'Agreeableness', 'bfi_Openness': 'Openness',
            'psqi': 'PSQI', 'psqi_subject_quality': 'Subject Quality',
            'psqi_sleep_latency': 'Sleep Latency', 'psqi_sleep_duration': 'Sleep Duration',
            'psqi_sleep_efficiency': 'Sleep Efficiency', 'psqi_sleep_disturbance': 'Sleep Disturbance',
            'psqi_sleep_medication': 'Sleep Medication', 'psqi_day_dysfunction': 'Day-time Dysfunction',
            'sitting_weekday': 'On weekday', 'sitting_weekend': 'On weekend',
            'walk_during_work': 'On workdays', 'walk_during_off': 'On off-days'}


def print_stats(igtb_df, col, func=stats.kruskal, func_name='K-S'):
    # shift_pre-study
    igtb_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    day_nurse_df = igtb_df.loc[igtb_df['Shift'] == 'Day shift']
    night_nurse_df = igtb_df.loc[igtb_df['Shift'] == 'Night shift']

    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(day_nurse_df[col].dropna()), len(night_nurse_df[col].dropna())))

    # Print
    print('Day shift: median = %.2f, mean = %.2f' % (np.nanmedian(day_nurse_df[col]), np.nanmean(day_nurse_df[col])))
    print('Day shift: range %.2f-%.2f' % (np.nanmin(day_nurse_df[col]), np.nanmax(day_nurse_df[col])))

    print('Night shift: median = %.2f, mean = %.2f' % (np.nanmedian(night_nurse_df[col]), np.nanmean(night_nurse_df[col])))
    print('Night shift: range %.2f-%.2f' % (np.nanmin(night_nurse_df[col]), np.nanmax(night_nurse_df[col])))

    # stats test
    stat, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))


def print_latex(igtb_df, col, func=stats.kruskal, func_name='K-S', end_str='\\rule{0pt}{2ex} \\\\'):
    # shift_pre-study
    igtb_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    day_nurse_df = igtb_df.loc[igtb_df['Shift'] == 'Day shift']
    night_nurse_df = igtb_df.loc[igtb_df['Shift'] == 'Night shift']

    if 'psqi_' in col:
        print('\multicolumn{1}{l}{\hspace{0.3cm}{%s}} &' % col_dict[col])
    elif 'sitting' in col or 'walk' in col:
        if 'weekday' in col or 'work' in col:
            if 'sitting' in col:
                print('\multicolumn{1}{l}{\\textbf{Time in Sitting (min)}} & & & & & & & \\rule{0pt}{2.25ex} \\\\')
            else:
                print('\multicolumn{1}{l}{\\textbf{Time in Walking (min)}} & & & & & & & \\rule{0pt}{2.25ex} \\\\')
            print()
        print('\multicolumn{1}{l}{\hspace{0.3cm}{%s}} &' % col_dict[col])
    else:
        print('\multicolumn{1}{l}{\\textbf{%s}} &' % col_dict[col])

    if 'sitting' in col or 'walk' in col:
        print('\multicolumn{1}{c}{$%d$} &' % (len(day_nurse_df[col].dropna())))
        print('\multicolumn{1}{c}{$%.0f$ ($%.0f$)} &' % (np.nanmedian(day_nurse_df[col]), np.nanmean(day_nurse_df[col])))
        print('\multicolumn{1}{c}{$%.0f$-$%.0f$} &' % (np.nanmin(day_nurse_df[col]), np.nanmax(day_nurse_df[col])))
        print('\multicolumn{1}{c}{$%d$} &' % (len(night_nurse_df[col].dropna())))
        print('\multicolumn{1}{c}{$%.0f$ ($%.0f$)} &' % (np.nanmedian(night_nurse_df[col]), np.nanmean(night_nurse_df[col])))
        print('\multicolumn{1}{c}{$%.0f$-$%.0f$} &' % (np.nanmin(night_nurse_df[col]), np.nanmax(night_nurse_df[col])))

    else:
        print('\multicolumn{1}{c}{$%d$} &' % (len(day_nurse_df[col].dropna())))
        print('\multicolumn{1}{c}{$%.2f$ ($%.2f$)} &' % (np.nanmedian(day_nurse_df[col]), np.nanmean(day_nurse_df[col])))
        print('\multicolumn{1}{c}{$%.2f$ - $%.2f$} &' % (np.nanmin(day_nurse_df[col]), np.nanmax(day_nurse_df[col])))
        print('\multicolumn{1}{c}{$%d$} &' % (len(night_nurse_df[col].dropna())))
        print('\multicolumn{1}{c}{$%.2f$ ($%.2f$)} &' % (np.nanmedian(night_nurse_df[col]), np.nanmean(night_nurse_df[col])))
        print('\multicolumn{1}{c}{$%.2f$ - $%.2f$} &' % (np.nanmin(night_nurse_df[col]), np.nanmax(night_nurse_df[col])))

    # stats test
    u_stats, p = func(day_nurse_df[col].dropna(), night_nurse_df[col].dropna())

    if p < 0.01:
        print('\multicolumn{1}{c}{$\mathbf{%.3f^{**}}$} &' % (p))
    elif p < 0.05:
        print('\multicolumn{1}{c}{$\mathbf{%.3f^*}$} &' % (p))
    elif p < 0.10:
        print('\multicolumn{1}{c}{$\mathbf{%.3f^\dagger}$} &' % (p))
    else:
        print('\multicolumn{1}{c}{$%.3f$} &' % (p))

    na, nb = len(day_nurse_df[col].dropna()), len(night_nurse_df[col].dropna())
    std_dev = np.sqrt((na * nb) * (na + nb + 1) / 12)
    z = (u_stats - (na * nb / 2)) / std_dev

    # print('\multicolumn{1}{c}{$%.1f$} %s' % (u_stats, end_str))
    print('\multicolumn{1}{c}{$%.2f$} %s' % (z, end_str))
    print()


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

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

        # Process physical activity survey
        sitting_on_weekdays = int(igtb_raw.loc[uid, 'ipaq26'])
        if sitting_on_weekdays < 10 or sitting_on_weekdays == 999:
            sitting_on_weekdays = np.nan

        sitting_on_weekend = int(igtb_raw.loc[uid, 'ipaq27'])
        if sitting_on_weekend < 10 or sitting_on_weekend == 999:
            sitting_on_weekend = np.nan

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

    psqi_col = ['sitting_weekday', 'sitting_weekend', 'walk_during_work', 'walk_during_off', 'psqi']
    psqi_col = psqi_col + list(psqi_raw_igtb.columns)

    raw_sum = igtb_df[list(psqi_raw_igtb.columns)].sum(axis=1)
    raw_psqi = igtb_df['psqi']

    # for col in psqi_col:
        # print_stats(igtb_df, col, func=stats.mannwhitneyu)
    #    print_latex(igtb_df, col, func=stats.mannwhitneyu)

    affect_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect',
                   'rand_GeneralHealth', 'rand_EnergyFatigue', 'swls', 'pss', 'waaq', 'uwes',
                   'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness']

    # for col in affect_cols:
    #    print_stats(igtb_df, col, func=stats.mannwhitneyu)

    # for col in psqi_col:
    for col in affect_cols:
        print_latex(igtb_df, col, func=stats.mannwhitneyu)

    print()