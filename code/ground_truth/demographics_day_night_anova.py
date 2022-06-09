from util.load_data_basic import *
from scipy import stats
from scipy.stats import skew
import pingouin as pg
from statsmodels.formula.api import ols
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


def anova(igtb_df, col, factor1, factor2):
    data_df = igtb_df[[col]+['shift', factor1, factor2]]
    data_df = data_df.dropna()

    data_df[factor1] = pd.get_dummies(data_df[factor1], drop_first=True)
    data_df[factor2] = pd.get_dummies(data_df[factor2], drop_first=True)
    data_df['shift'] = pd.get_dummies(data_df['shift'], drop_first=True)

    print(col)
    lm = ols(col + ' ~ shift +' + factor1 + ' + ' + factor2, data = data_df).fit()
    table = sm.stats.anova_lm(lm, typ=2)  # Type 2 ANOVA DataFrame
    print(table)

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
        gender = igtb_df.loc[igtb_df['participant_id'] == participant_id].gender[0]
        age = igtb_df.loc[igtb_df['participant_id'] == participant_id].age[0]
        educ = igtb_df.loc[igtb_df['participant_id'] == participant_id].educ[0]
        lang = igtb_df.loc[igtb_df['participant_id'] == participant_id].lang[0]
        psqi = igtb_df.loc[igtb_df['participant_id'] == participant_id].psqi[0]

        job_str = 'nurse' if nurse == 'A' else 'non_nurse'
        shift_str = 'day' if shift == 'Day shift' else 'night'
        gender_str = 'Male' if gender == 1 else 'Female'
        lang_str = 'Yes' if lang == 1 else 'No'
        psqi_str = 'PSQI >= 7' if psqi >= 7 else 'PSQI < 7'

        uid = list(igtb_df.loc[igtb_df['participant_id'] == participant_id].index)[0]


        if age < 40:
            igtb_df.loc[uid, 'Age'] = '< 40 Years'
        else:
            igtb_df.loc[uid, 'Age'] = '>= 40 Years'

        if educ == 'A' or educ == 'B':
            igtb_df.loc[uid, 'Educ'] = 'Some college or College'
        elif educ == 'C':
            igtb_df.loc[uid, 'Educ'] = 'Graduate'

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

        igtb_df.loc[uid, 'walk_during_work'] = float(walk_during_work)
        igtb_df.loc[uid, 'walk_during_off'] = float(walk_during_off)
        igtb_df.loc[uid, 'sitting_weekday'] = sitting_on_weekdays
        igtb_df.loc[uid, 'sitting_weekend'] = sitting_on_weekend

        igtb_df.loc[uid, 'job'] = job_str
        igtb_df.loc[uid, 'Gender'] = gender_str
        igtb_df.loc[uid, 'native_lang'] = lang_str
        igtb_df.loc[uid, 'PSQI'] = psqi_str


    # shift_pre-study
    nurse_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    print('Total number of participants: %d' % (len(nurse_df)))

    print()
    day_df = nurse_df.loc[nurse_df['Shift'] == 'Day shift']
    night_df = nurse_df.loc[nurse_df['Shift'] == 'Night shift']

    affect_cols = ['pan_NegAffect', 'swls', 'psqi']

    affect_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect', 'swls',
                   'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness', 'psqi']
    nurse_df.to_csv('igtb.csv.gz')

    for col in affect_cols:
        # for demo in ['Age', 'Gender', 'native_lang', 'Educ']:
        anova(nurse_df, col=col, factor1='Age', factor2='Gender')