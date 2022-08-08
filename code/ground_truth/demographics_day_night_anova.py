from util.load_data_basic import *
from scipy import stats
from scipy.stats import skew
import pingouin as pg
from statsmodels.formula.api import ols
import statsmodels.api as sm

sys.path.insert(1, '/Users/brinkley97/Documents/development/lab-information_sciences_institute/tiles-day-night/code/util')

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
    bucket_str = 'tiles_dataset'
    
    # root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)
    root_data_path = Path(__file__).parent.absolute().parents[2].joinpath('datasets', bucket_str)
    
    # please contact the author to access: igtb_day_night.csv.gz
    # igtb_day_night_file = 'igtb_day_night.csv.gz'
    # path_to_file = '/Users/brinkley97/Documents/development/lab-information_sciences_institute/datasets/tiles_dataset/surveys/raw/IGTB/USC_PILOT_IGTB.csv'
    # if Path(os.path.realpath(__file__)).parents[2].joinpath(path_to_file).exists() == False:
    #     igtb_df = read_AllBasic(root_data_path)
    #     igtb_df.to_csv(Path(os.path.realpath(__file__)).parents[2].joinpath('datasets', bucket_str, 'raw', 'demographics', igtb_day_night_file))
    # igtb_df = pd.read_csv(Path(os.path.realpath(__file__)).parents[2].joinpath('datasets', bucket_str, 'raw', 'demographics', igtb_day_night_file), index_col=0)

    # please contact the author to access: igtb_day_night.csv.gz
    if Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz').exists() == False:
        igtb_df = read_AllBasic(root_data_path)
        igtb_df.to_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'))
    igtb_df = pd.read_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'), index_col=0)

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


        if age < 40: igtb_df.loc[uid, 'Age'] = '< 40 Years'
        else: igtb_df.loc[uid, 'Age'] = '>= 40 Years'

        if educ == 'A' or educ == 'B': igtb_df.loc[uid, 'Educ'] = 'Some college or College'
        elif educ == 'C': igtb_df.loc[uid, 'Educ'] = 'Graduate'

        igtb_df.loc[uid, 'job'] = job_str
        igtb_df.loc[uid, 'Gender'] = gender_str
        igtb_df.loc[uid, 'native_lang'] = lang_str
        igtb_df.loc[uid, 'PSQI'] = psqi_str


    # shift_pre-study
    nurse_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    print('Total number of participants: %d' % (len(nurse_df)))
    %store nurse_df

    print()
    day_df = nurse_df.loc[nurse_df['Shift'] == 'Day shift']
    night_df = nurse_df.loc[nurse_df['Shift'] == 'Night shift']
    

    affect_cols = ['pan_NegAffect', 'swls', 'psqi']
    affect_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect', 'swls', 'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness', 'psqi']

    for col in affect_cols:
        anova(nurse_df, col=col, factor1='Age', factor2='Gender')