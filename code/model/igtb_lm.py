from util.load_data_basic import *
import statsmodels.api as sm
from scipy.stats.mstats import zscore
from statsmodels.formula.api import ols

col_dict = {'rest_work': 'Rest Activity (workday)',
            'rest_off': 'Rest Activity (off-day)',
            'step_ratio_work': 'Walk Activity (workday)',
            'step_ratio_off': 'Walk Activity (off-day)',
            'duration_work': 'Sleep duration (workday)',
            'duration_off': 'Sleep duration (off-day)',
            'efficiency_work': 'Sleep efficiency (workday)',
            'efficiency_off': 'Sleep efficiency (off-day)'}


print_dict = {'r2': 'Adjust $R^2$',
              'age': 'Age [< 40 Years]',
              'gender': 'Gender [Female]',
              'day': 'Shift [Day shift]',
              'intercept': 'Intercept',
              'observation': 'Number of Observations',
              'step_ratio_work': 'Walk Activity Ratio(Workday)',
              'rest_work': 'Rest Activity Ratio(Workday)',
              'rest_off': 'Rest-activity Ratio(Off-day)',
              'step_ratio_off': 'Walk-activity Ratio(Off-day)',
              'efficiency_off': 'Sleep Efficiency(Off-day)',
              'efficiency_work': 'Sleep Efficiency(Workday)',
              'duration_off': 'Sleep Duration(Off-day)',
              'duration_work': 'Sleep Duration(Workday)',
              'day*rest_off': 'Shift [Day shift]$\\times$Rest-activity Ratio(Off-day)',
              'day*step_ratio_off': 'Shift [Day shift]$\\times$Walk-activity Ratio(Off-day)',
              'day*rest_work': 'Shift [Day shift]$\\times$Rest-activity Ratio(Workday)',
              'day*step_ratio_work': 'Shift [Day shift]$\\times$Walk-activity Ratio(Workday)',
              'day*efficiency_off': 'Shift [Day shift]$\\times$Sleep Efficiency(Off-day)',
              'day*efficiency_work': 'Shift [Day shift]$\\times$Sleep Efficiency(Workday)',
              'day*duration_off': 'Shift [Day shift]$\\times$Sleep Duration(Off-day)',
              'day*duration_work': 'Shift [Day shift] $\\times$ Sleep Duration (Workday)',
              'night*rest_off': 'Shift [Night shift]$\\times$Rest Activity Ratio(Off-day)',
              'night*step_ratio_off': 'Shift [Night shift]$\\times$Walk Activity Ratio(Off-day)',
              'night*rest_work': 'Shift [Night shift]$\\times$Rest Activity Ratio(Workday)',
              'night*step_ratio_work': 'Shift [Night shift]$\\times$Walk Activity Ratio(Workday)',
              'night*efficiency_off': 'Shift [Night shift]$\\times$Sleep Efficiency(Off-day)',
              'night*duration_off': 'Shift [Night shift]$\\times$Sleep Duration(Off-day)',
              'night*duration_work': 'Shift [Night shift]$\\times$Sleep Duration(Workday)'
              }
              #'night*rest_off': 'Shift [Night shift] $\\times$ Rest Activity \% (Off-day)'}

def mr_reg(nurse_df, igtb_col, index, feat_col):

    # for col in feat_cols:
    data_df = nurse_df[[feat_col, 'less_than_40', 'female', 'day', 'night']+[igtb_col]]
    data_df = data_df.dropna()
    # data_df = (data_df - data_df.mean()) / data_df.std()
    tmp_df = (data_df[[igtb_col, feat_col]] - data_df[[igtb_col, feat_col]].mean()) / data_df[[igtb_col, feat_col]].std()
    data_df.loc[list(tmp_df.index), [igtb_col, feat_col]] = tmp_df.loc[list(tmp_df.index), [igtb_col, feat_col]]
    model = ols(igtb_col + ' ~ less_than_40 + female + day + ' + feat_col + ' + day : ' + feat_col, data=data_df).fit()


    # print('\multicolumn{1}{c}{\hspace{1cm}%s} &' % ('Shift'))
    if igtb_col == 'swls':
        print('%s &' % (print_dict[index]))

    if igtb_col == 'pan_NegAffect':
        end_str = '\\rule{0pt}{1.85ex} \\\\'
    else:
        end_str = '&'

    if index == 'r2':
        # print(model.summary())
        if model.f_pvalue < 0.01:
            print('%.3f\\textsuperscript{**} %s' % (model.rsquared_adj, end_str))
        elif model.f_pvalue < 0.05:
            print('%.3f\\textsuperscript{*} %s' % (model.rsquared_adj, end_str))
        else:
            print('%.3f %s' % (model.rsquared_adj, end_str))
    elif index == 'observation':
        print('\multicolumn{1}{c}{%d} %s' % (len(data_df), end_str))
    elif index == 'intercept':
        if model.pvalues[0] < 0.01:
            print('%.2f\\textsuperscript{**} %s' % (model.params[0], end_str))
        elif model.pvalues[0] < 0.05:
            print('%.2f\\textsuperscript{*} %s' % (model.params[0], end_str))
        else:
            print('%.2f %s' % (model.params[0], end_str))
    else:
        # for print_index in ['r2', 'age', 'gender', 'day', 'feat_col', 'day*feat_col', 'night*feat_col']:
        if index == 'age':
            param_idx = 0
        elif index == 'gender':
            param_idx = 1
        elif index == 'day':
            param_idx = 2
        elif index == feat_col:
            param_idx = 3
        elif index == 'day*'+feat_col:
            param_idx = 4
        elif index == 'night*'+feat_col:
            param_idx = 5

        if model.pvalues[param_idx+1] < 0.01:
            print('%.2f\\textsuperscript{**} %s' % (model.params[param_idx+1], end_str))
        elif model.pvalues[param_idx+1] < 0.05:
            print('%.2f\\textsuperscript{*} %s' % (model.params[param_idx+1], end_str))
        else:
            print('%.2f %s' % (model.params[param_idx+1], end_str))



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

    fitbit_work_df = pd.read_csv(Path(__file__).parent.absolute().parents[0].joinpath('physical', 'stats_work_lm.csv.gz'), index_col=7)
    fitbit_off_df = pd.read_csv(Path(__file__).parent.absolute().parents[0].joinpath('physical', 'stats_off_lm.csv.gz'), index_col=7)

    nurse_df = return_nurse_df(igtb_df)
    for participant_id in list(nurse_df.participant_id):
        nurse = str(nurse_df.loc[nurse_df['participant_id'] == participant_id].currentposition[0])
        shift = nurse_df.loc[nurse_df['participant_id'] == participant_id].Shift[0]
        job_str = 'nurse' if nurse == 'A' else 'non_nurse'

        uid = list(nurse_df.loc[nurse_df['participant_id'] == participant_id].index)[0]
        gender = nurse_df.loc[nurse_df['participant_id'] == participant_id].gender[0]
        age = nurse_df.loc[nurse_df['participant_id'] == participant_id].age[0]

        gender_str = 'Male' if gender == 1 else 'Female'
        age_str = '< 40 Years' if age < 40 else '>= 40 Years'
        shift_str = shift

        nurse_df.loc[uid, 'job'] = job_str
        nurse_df.loc[uid, 'shift'] = shift_str
        nurse_df.loc[uid, 'gender'] = gender_str
        nurse_df.loc[uid, 'age'] = age_str

        if participant_id in list(fitbit_work_df.index):
            nurse_df.loc[uid, 'rest_work'] = fitbit_work_df.loc[participant_id, 'rest']
            nurse_df.loc[uid, 'step_ratio_work'] = fitbit_work_df.loc[participant_id, 'step_ratio']
            nurse_df.loc[uid, 'vigorous_min_work'] = fitbit_work_df.loc[participant_id, 'vigorous_min']
        if participant_id in list(fitbit_off_df.index):
            nurse_df.loc[uid, 'rest_off'] = fitbit_off_df.loc[participant_id, 'rest']
            nurse_df.loc[uid, 'step_ratio_off'] = fitbit_off_df.loc[participant_id, 'step_ratio']
            nurse_df.loc[uid, 'vigorous_min_off'] = fitbit_off_df.loc[participant_id, 'vigorous_min']

        if participant_id in list(sleep_stats_df.index):
            nurse_df.loc[uid, 'duration_work'] = sleep_work_df.loc[participant_id, 'duration']
            nurse_df.loc[uid, 'duration_off'] = sleep_off_df.loc[participant_id, 'duration']

            nurse_df.loc[uid, 'efficiency_work'] = sleep_work_df.loc[participant_id, 'efficiency']
            nurse_df.loc[uid, 'efficiency_off'] = sleep_off_df.loc[participant_id, 'efficiency']

    nurse_df = nurse_df[['psqi', 'swls', 'pan_PosAffect', 'pan_NegAffect', 'stai', 'shift', 'age', 'gender',
                         'rest_work', 'vigorous_min_work', 'step_ratio_work',
                         'rest_off', 'vigorous_min_off', 'step_ratio_off',
                         'duration_work', 'duration_off', 'efficiency_work', 'efficiency_off']]

    tmp_df = pd.get_dummies(nurse_df['shift'])
    for index in list(tmp_df.index):
        nurse_df.loc[index, 'day'] = tmp_df.loc[index, 'Day shift']
        nurse_df.loc[index, 'night'] = tmp_df.loc[index, 'Night shift']

    tmp_df = pd.get_dummies(nurse_df['age'])
    for index in list(tmp_df.index):
        # nurse_df.loc[index, 'less_than_40'] = tmp_df.loc[index, '< 40 Years']
        nurse_df.loc[index, 'less_than_40'] = tmp_df.loc[index, '>= 40 Years']

    tmp_df = pd.get_dummies(nurse_df['gender'])
    for index in list(tmp_df.index):
        nurse_df.loc[index, 'female'] = tmp_df.loc[index, 'Female']
        # nurse_df.loc[index, 'female'] = tmp_df.loc[index, 'Male']

    feat_col = 'efficiency_work'
    for print_index in ['intercept', 'age', 'gender', 'day', feat_col, 'day*' + feat_col, 'observation', 'r2']:
        if print_index == 'observation':
            print('\\midrule')

        for col in ['swls', 'stai', 'psqi', 'pan_PosAffect', 'pan_NegAffect']:
            mr_reg(nurse_df, col, print_index, feat_col=feat_col)
        print()
    print()