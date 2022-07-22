from util.load_data_basic import *
from scipy import stats
from scipy.stats import skew
from pingouin import ancova
import statsmodels.api as sm


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
    

def ancova_test(igtb_df, col):
    result = ancova(data=igtb_df, dv=col, covar=['age', 'education', 'gender'], between='shift')
    print()

def multiple_regression(igtb_df, col):
    data_df = igtb_df[[col]+['Age', 'Educ', 'Gender', 'shift', 'native_lang']]
    data_df = data_df.dropna()

    data_df['Age'] = pd.get_dummies(data_df['Age'], drop_first=True)
    data_df['Educ'] = pd.get_dummies(data_df['Educ'], drop_first=True)
    data_df['Gender'] = pd.get_dummies(data_df['Gender'], drop_first=True)
    data_df['shift'] = pd.get_dummies(data_df['shift'], drop_first=True)
    data_df['native_lang'] = pd.get_dummies(data_df['native_lang'], drop_first=True)

    print(col)
    X = data_df[['Age', 'Educ', 'Gender', 'shift', 'native_lang']]
    X = sm.add_constant(X)

    Y = data_df[col]
    model = sm.OLS(Y, X).fit()
    print(model.summary())

    print()


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    # please contact the author to access: igtb_day_night.csv.gz
    if Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz').exists() == False:
        igtb_df = read_AllBasic(root_data_path)
        igtb_df.to_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'))
    igtb_df = pd.read_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'), index_col=0)

    for participant_id in list(igtb_df.participant_id):
        nurse = str(igtb_df.loc[igtb_df['participant_id'] == participant_id].currentposition[0])
        shift = igtb_df.loc[igtb_df['participant_id'] == participant_id].Shift[0]
        job_str = 'nurse' if nurse == 'A' else 'non_nurse'
        shift_str = 'day' if shift == 'Day shift' else 'night'
        uid = list(igtb_df.loc[igtb_df['participant_id'] == participant_id].index)[0]

        gender = igtb_df.loc[igtb_df['participant_id'] == participant_id].gender[0]
        age = igtb_df.loc[igtb_df['participant_id'] == participant_id].age[0]
        educ = igtb_df.loc[igtb_df['participant_id'] == participant_id].educ[0]
        lang = igtb_df.loc[igtb_df['participant_id'] == participant_id].lang[0]

        gender_str = 'Male' if gender == 1 else 'Female'
        lang_str = 'Yes' if lang == 1 else 'No'

        if age < 40:
            igtb_df.loc[uid, 'Age'] = '< 40 Years'
        else:
            igtb_df.loc[uid, 'Age'] = '>= 40 Years'
        igtb_df.loc[uid, 'Age'] = age

        if educ == 'A' or educ == 'B':
            igtb_df.loc[uid, 'Educ'] = 'Some college or College'
        elif educ == 'C':
            igtb_df.loc[uid, 'Educ'] = 'Graduate'

        igtb_df.loc[uid, 'job'] = job_str
        igtb_df.loc[uid, 'shift'] = shift_str
        igtb_df.loc[uid, 'Gender'] = gender_str
        igtb_df.loc[uid, 'native_lang'] = lang_str


    igtb_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    psqi_col = ['psqi']

    affect_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect',
                   'rand_GeneralHealth', 'rand_EnergyFatigue', 'swls', 'pss', 'waaq', 'uwes',
                   'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness']

    # for col in psqi_col:
    for col in affect_cols:
        multiple_regression(igtb_df, col)
    print()
