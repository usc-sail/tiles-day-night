from util.load_data_basic import *
import statsmodels.api as sm


def mr_reg(nurse_df, feat_cols):
    igtb_cols = ['psqi', 'ipaq', 'ocb', 'irb', 'itp',
                 'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness',
                 'pan_PosAffect', 'pan_NegAffect', 'stai'] + list(psqi_raw_igtb.columns)

    result_df = pd.DataFrame()
    nurse_df = nurse_df[igtb_cols+feat_cols]
    nurse_df = nurse_df.dropna()
    for col in igtb_cols:
        mr_df = nurse_df[[col] + feat_cols].dropna()
        y = mr_df[col]
        x = mr_df[feat_cols]
        x = pd.DataFrame(x, dtype=float)
        # x = (x - x.min()) / (x.max() - x.min())
        y = (y - y.mean()) / y.std()
        x = (x - x.mean()) / x.std()
        x = sm.add_constant(x)
        model = sm.OLS(y, x).fit()
        # model = sm.OLS(y, x).fit_regularized(alpha=1, L1_wt=0)
        # model = sm.GLSAR(y, x).iterative_fit()

        row_df = pd.DataFrame(index=[col])
        row_df['r_2'] = model.rsquared
        row_df['adj_r_2'] = model.rsquared_adj
        row_df['f_pval'] = model.f_pvalue
        row_df['resid'] = model.mse_resid
        row_df['mean'] = np.nanmean(y)

        for index in list(model.pvalues.index):
            if 'const' in index:
                continue
            row_df[index + '_p'] = model.pvalues[index]
        for index in list(model.params.index):
            if 'const' in index:
                continue
            row_df[index + '_param'] = model.params[index]

        row_df['num'] = len(mr_df)
        result_df = result_df.append(row_df)

        # print(model.summary())
    return result_df


def print_latex(data_df, feat_cols):

    if len(feat_cols) == 4:
        # Sleep activity
        igtb_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect',
                     'psqi', 'psqi_subject_quality', 'psqi_sleep_latency', 'psqi_sleep_disturbance',
                     'psqi_sleep_duration', 'psqi_sleep_medication', 'psqi_sleep_efficiency', 'psqi_day_dysfunction']
    else:
        # Physical activity
        igtb_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect',
                     'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness', 'psqi']

    igtb_dict = {'psqi': 'PSQI', 'pan_PosAffect': 'Positive Affect', 'pan_NegAffect': 'Negative Affect',
                 'stai': 'Anxiety', 'bfi_Neuroticism': 'Neuroticism', 'bfi_Conscientiousness': 'Conscientiousness',
                 'bfi_Extraversion': 'Extraversion', 'bfi_Agreeableness': 'Agreeableness', 'bfi_Openness': 'Openness',
                 'psqi_subject_quality': 'Subject Quality',
                 'psqi_sleep_latency': 'Sleep Latency', 'psqi_sleep_duration': 'Sleep Duration',
                 'psqi_sleep_efficiency': 'Sleep Efficiency', 'psqi_sleep_disturbance': 'Sleep Disturbance',
                 'psqi_sleep_medication': 'Sleep Medication', 'psqi_day_dysfunction': 'Day Dysfunc.' }


    for col in igtb_cols:
        adj_r = data_df.loc[col, 'adj_r_2']
        r_p_val = data_df.loc[col, 'f_pval']

        print()
        if 'psqi_' in col:
            print('\multicolumn{1}{l}{\\hspace{0.15cm}\\textbf{%s}} &' % igtb_dict[col])
        else:
            print('\multicolumn{1}{l}{\\textbf{%s}} &' % igtb_dict[col])
        if r_p_val < 0.01:
            print('\multicolumn{1}{c}{$\mathbf{%.3f^{**}}$} &' % adj_r)
            print('\multicolumn{1}{c}{$\mathbf{%.3f^{**}}$} &' % r_p_val)
        elif r_p_val < 0.05:
            print('\multicolumn{1}{c}{$\mathbf{%.3f^*}$} &' % adj_r)
            print('\multicolumn{1}{c}{$\mathbf{%.3f^*}$} &' % r_p_val)
        elif r_p_val < 0.10:
            print('\multicolumn{1}{c}{$\mathbf{%.3f^\dagger}$} &' % adj_r)
            print('\multicolumn{1}{c}{$\mathbf{%.3f^\dagger}$} &' % r_p_val)
        else:
            print('\multicolumn{1}{c}{$%.3f$} &' % adj_r)
            print('\multicolumn{1}{c}{$%.3f$} &' % r_p_val)

        for i, feat_col in enumerate(feat_cols):
            param = data_df.loc[col, feat_col + '_param']
            p = data_df.loc[col, feat_col + '_p']

            # vline = '|' if i != len(feat_cols) - 1 else ''
            vline = ''
            end_str = '&' if i != len(feat_cols) - 1 else '\\rule{0pt}{1.75ex} \\\\'
            if p < 0.01:
                print('\multicolumn{1}{c%s}{$\mathbf{%.2f}$} &' % (vline, param))
                print('\multicolumn{1}{c%s}{$\mathbf{%.3f^{**}}$} %s' % (vline, p, end_str))
            elif p < 0.05:
                print('\multicolumn{1}{c%s}{$\mathbf{%.2f}$} &' % (vline, param))
                print('\multicolumn{1}{c%s}{$\mathbf{%.3f^*}$} %s' % (vline, p, end_str))
            elif p < 0.10:
                print('\multicolumn{1}{c%s}{$\mathbf{%.2f}$} &' % (vline, param))
                print('\multicolumn{1}{c%s}{$\mathbf{%.3f^\dagger}$} %s' % (vline, p, end_str))
            else:
                print('\multicolumn{1}{c%s}{$%.2f$} &' % (vline, param))
                print('\multicolumn{1}{c%s}{$%.3f$} %s' % (vline, p, end_str))


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    igtb_df = read_AllBasic(root_data_path)
    psqi_raw_igtb = read_PSQI_Raw(root_data_path)
    igtb_raw = read_IGTB_Raw(root_data_path)

    sleep_stats_df = pd.read_csv(Path(__file__).parent.absolute().parents[0].joinpath('sleep', 'sleep.csv.gz'), index_col=0)
    sleep_work_df = sleep_stats_df.loc[sleep_stats_df['work'] == 'workday']
    sleep_off_df = sleep_stats_df.loc[sleep_stats_df['work'] == 'offday']
    sleep_stats_df = sleep_stats_df.loc[sleep_stats_df['work'] == 'all']

    fitbit_df = pd.read_csv(Path(__file__).parent.absolute().parents[0].joinpath('physical', 'stats.csv.gz'), index_col=0)
    fitbit_work_df = fitbit_df.loc[fitbit_df['work'] == 1]
    fitbit_off_df = fitbit_df.loc[fitbit_df['work'] == 0]
    fitbit_df = fitbit_df.loc[fitbit_df['work'] == 0.5]

    nurse_df = return_nurse_df(igtb_df)
    for participant_id in list(nurse_df.participant_id):
        nurse = str(nurse_df.loc[nurse_df['participant_id'] == participant_id].currentposition[0])
        shift = nurse_df.loc[nurse_df['participant_id'] == participant_id].Shift[0]
        job_str = 'nurse' if nurse == 'A' else 'non_nurse'
        shift_str = 0 if shift == 'Day shift' else 1
        uid = list(nurse_df.loc[nurse_df['participant_id'] == participant_id].index)[0]

        nurse_df.loc[uid, 'job'] = job_str
        nurse_df.loc[uid, 'shift'] = shift_str

        if participant_id in list(fitbit_df.index):
            nurse_df.loc[uid, 'rest'] = fitbit_df.loc[participant_id, 'rest']
            nurse_df.loc[uid, 'moderate'] = fitbit_df.loc[participant_id, 'moderate']
            nurse_df.loc[uid, 'vigorous'] = fitbit_df.loc[participant_id, 'vigorous']
            nurse_df.loc[uid, 'intense'] = fitbit_df.loc[participant_id, 'intense']
            nurse_df.loc[uid, 'step'] = fitbit_df.loc[participant_id, 'step']

            if participant_id in list(fitbit_work_df.index):
                nurse_df.loc[uid, 'rest_work'] = fitbit_work_df.loc[participant_id, 'rest']
                nurse_df.loc[uid, 'moderate_work'] = fitbit_work_df.loc[participant_id, 'moderate']
                nurse_df.loc[uid, 'vigorous_work'] = fitbit_work_df.loc[participant_id, 'vigorous']
                nurse_df.loc[uid, 'intense_work'] = fitbit_work_df.loc[participant_id, 'intense']
                nurse_df.loc[uid, 'step_work'] = fitbit_work_df.loc[participant_id, 'step']

            if participant_id in list(fitbit_off_df.index):
                nurse_df.loc[uid, 'rest_off'] = fitbit_off_df.loc[participant_id, 'rest']
                nurse_df.loc[uid, 'moderate_off'] = fitbit_off_df.loc[participant_id, 'moderate']
                nurse_df.loc[uid, 'vigorous_off'] = fitbit_off_df.loc[participant_id, 'vigorous']
                nurse_df.loc[uid, 'intense_off'] = fitbit_off_df.loc[participant_id, 'intense']
                nurse_df.loc[uid, 'step_off'] = fitbit_off_df.loc[participant_id, 'step']

            nurse_df.loc[uid, 'rest_diff'] = fitbit_df.loc[participant_id, 'rest_diff']
            nurse_df.loc[uid, 'moderate_diff'] = fitbit_df.loc[participant_id, 'moderate_diff']
            nurse_df.loc[uid, 'vigorous_diff'] = fitbit_df.loc[participant_id, 'vigorous_diff']
            nurse_df.loc[uid, 'intense_diff'] = fitbit_df.loc[participant_id, 'intense_diff']
            nurse_df.loc[uid, 'step_diff'] = fitbit_df.loc[participant_id, 'step_diff']

        if participant_id in list(sleep_stats_df.index):
            nurse_df.loc[uid, 'duration'] = sleep_stats_df.loc[participant_id, 'duration']
            nurse_df.loc[uid, 'duration_work'] = sleep_work_df.loc[participant_id, 'duration']
            nurse_df.loc[uid, 'duration_off'] = sleep_off_df.loc[participant_id, 'duration']

            nurse_df.loc[uid, 'efficiency'] = sleep_stats_df.loc[participant_id, 'efficiency']
            nurse_df.loc[uid, 'efficiency_work'] = sleep_work_df.loc[participant_id, 'efficiency']
            nurse_df.loc[uid, 'efficiency_off'] = sleep_off_df.loc[participant_id, 'efficiency']

            nurse_df.loc[uid, 'minutesAsleep'] = sleep_stats_df.loc[participant_id, 'minutesAsleep']
            nurse_df.loc[uid, 'minutesAsleep_work'] = sleep_work_df.loc[participant_id, 'minutesAsleep']
            nurse_df.loc[uid, 'minutesAsleep_off'] = sleep_off_df.loc[participant_id, 'minutesAsleep']

            nurse_df.loc[uid, 'mid'] = sleep_stats_df.loc[participant_id, 'mid']
            nurse_df.loc[uid, 'mid_std'] = sleep_stats_df.loc[participant_id, 'mid_std']
            nurse_df.loc[uid, 'total_seconds'] = sleep_stats_df.loc[participant_id, 'total_seconds']
            nurse_df.loc[uid, 'duration_diff'] = sleep_stats_df.loc[participant_id, 'duration_diff']

        for col in list(psqi_raw_igtb.columns):
            nurse_df.loc[uid, col] = psqi_raw_igtb.loc[uid, col]

    nurse_df = nurse_df[['psqi', 'ipaq', 'ocb', 'irb', 'itp',
                         'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness',
                         'pan_PosAffect', 'pan_NegAffect', 'stai',
                         'shift', 'rest', 'moderate', 'vigorous', 'intense', 'step',
                         'rest_work', 'moderate_work', 'vigorous_work', 'intense_work', 'step_work',
                         'rest_off', 'moderate_off', 'vigorous_off', 'intense_off', 'step_off',
                         'rest_diff', 'moderate_diff', 'vigorous_diff', 'intense_diff', 'step_diff',
                         'duration', 'duration_work', 'duration_off', 'total_seconds', 'mid_std',
                         'minutesAsleep', 'minutesAsleep_work', 'minutesAsleep_off',
                         'efficiency', 'efficiency_work', 'efficiency_off', 'mid', 'duration_diff']+list(psqi_raw_igtb.columns)]

    day_df = nurse_df.loc[nurse_df['shift'] == 0]
    night_df = nurse_df.loc[nurse_df['shift'] == 1]

    # Activity
    # physical_feat_cols = ['rest_off', 'vigorous_off', 'step']
    physical_feat_cols = ['rest', 'vigorous_off', 'step']

    day_physical_df = mr_reg(day_df, physical_feat_cols)
    night_physical_df = mr_reg(night_df, physical_feat_cols)

    day_physical_df.to_csv('day_physical_mr.csv.gz')
    night_physical_df.to_csv('night_physical_mr.csv.gz')

    print('------------day physical mr-------------------')
    print_latex(day_physical_df, physical_feat_cols)
    print('------------------------------------------------')

    print('------------night physical mr-------------------')
    print_latex(night_physical_df, physical_feat_cols)
    print('------------------------------------------------')

    # Sleep
    sleep_feat_cols = ['duration_work', 'duration_off', 'minutesAsleep', 'mid']

    day_sleep_df = mr_reg(day_df, sleep_feat_cols)
    night_sleep_df = mr_reg(night_df, sleep_feat_cols)

    day_sleep_df.to_csv('day_sleep_mr.csv.gz')
    night_sleep_df.to_csv('night_sleep_mr.csv.gz')

    print('------------day sleep mr-------------------')
    print_latex(day_sleep_df, sleep_feat_cols)
    print('------------------------------------------------')

    print('------------night sleep mr-------------------')
    print_latex(night_sleep_df, sleep_feat_cols)
    print('------------------------------------------------')

