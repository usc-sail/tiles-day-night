# from util.load_data_basic import *
import sys
sys.path.insert(1, '/Users/brinkley97/Documents/development/lab-information_sciences_institute/tiles-day-night/code/util')
from load_data_basic import read_AllBasic
from scipy import stats
from scipy.stats import skew
import pingouin as pg
from statsmodels.formula.api import ols
import statsmodels.api as sm
from pathlib import Path
import pandas as pd
import numpy as np


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

def print_latex(first_df, second_df, demo, demo_option, print_col, end=False):

    print('\multicolumn{1}{l}{\\hspace{0.5cm}{%s}} &' % print_col)
    print('\multicolumn{1}{c}{{%d}} &' % len(first_df.loc[first_df[demo] == demo_option]))
    print('\multicolumn{1}{c}{{%.2f}} &' % (len(first_df.loc[first_df[demo] == demo_option]) / len(first_df) * 100))
    print('\multicolumn{1}{c}{{%d}} &' % len(second_df.loc[second_df[demo] == demo_option]))
    print('\multicolumn{1}{c}{{%.2f}} \\rule{0pt}{2ex} \\\\' % (len(second_df.loc[second_df[demo] == demo_option]) / len(second_df) * 100))
    if end == True:
        print('\\midrule')
    print()

def print_latex_all(all_df, first_df, second_df, demo, demo_option, print_col, end=False, stat='num'):

    # print('\multicolumn{1}{l|}{\\hspace{0.5cm}{%s}} &' % print_col)
    print('\multicolumn{1}{l|}{{%s}} &' % print_col)
    stats_df = pd.DataFrame(index=[demo])

    if stat != 'num':
        len1 = len(first_df.loc[first_df[demo] == demo_option])
        per1 = (len(first_df.loc[first_df[demo] == demo_option]) / len(first_df) * 100)
        len2 = len(second_df.loc[second_df[demo] == demo_option])
        per2 = (len(second_df.loc[second_df[demo] == demo_option]) / len(second_df) * 100)
        len_all = len(all_df.loc[all_df[demo] == demo_option])
        per_all = (len(all_df.loc[all_df[demo] == demo_option]) / len(all_df) * 100)

        print('\multicolumn{1}{c|}{{%d (%.1f\\%%)}} &' % (len1, per1))
        print('\multicolumn{1}{c|}{{%d (%.1f\\%%)}} &' % (len2, per2))
        print('\multicolumn{1}{c|}{{%d (%.1f\\%%)}} &' % (len_all, per_all))
        print('\multicolumn{1}{c|}{} &')
        print('\multicolumn{1}{c}{} \\rule{0pt}{2.25ex} \\\\')
    else:
        mean1 = np.nanmean(first_df[demo])
        std1 = np.nanstd(first_df[demo])
        mean2 = np.nanmean(second_df[demo])
        std2 = np.nanstd(second_df[demo])
        mean_all = np.nanmean(all_df[demo])
        std_all = np.nanstd(all_df[demo])
        min = np.nanmin(all_df[demo])
        max = np.nanmax(all_df[demo])

        print('\multicolumn{1}{c|}{{%.1f $\\pm$ %.1f}} &' % (mean1, std1))
        print('\multicolumn{1}{c|}{{%.1f $\\pm$ %.1f}} &' % (mean2, std2))
        print('\multicolumn{1}{c|}{{%.1f $\\pm$ %.1f}} &' % (mean_all, std_all))
        print('\multicolumn{1}{c|}{{%.1f - %.1f}} &' % (min, max))

        # u_stats, p = stats.mannwhitneyu(first_df[demo].dropna(), second_df[demo].dropna())
        # result = pg.mwu(first_df[demo].dropna(), second_df[demo].dropna(), tail='two-sided')
        result = pg.ttest(np.array(first_df[demo].dropna()), np.array(second_df[demo].dropna()))
        # lm = ols(demo + ' ~ Shift', data=all_df).fit()
        # result = sm.stats.anova_lm(lm, typ=2)  # Type 2 ANOVA DataFrame

        p = result['p-val'].values[0]
        t = result['T'].values[0]
        df = result['dof'].values[0]


        stats_df['p'] = p
        stats_df['T'] = t
        stats_df['df'] = df

        if p < 0.01: print('\multicolumn{1}{c}{$\mathbf{%.3f^{**}}$} \\rule{0pt}{2.25ex} \\\\' % (p))
        elif p < 0.05: print('\multicolumn{1}{c}{$\mathbf{%.3f^*}$} \\rule{0pt}{2.25ex} \\\\' % (p))
        else: print('\multicolumn{1}{c}{$%.3f$} \\rule{0pt}{2.25ex} \\\\' % (p))

    if end == True: print('\\hline')
    print()
    return stats_df


def print_odd_ratio(first_df, second_df, demo, demo_option1, demo_option2, print_col):

    tabel_df = pd.DataFrame(index=['day', 'night'], columns=[demo_option1, demo_option2])
    tabel_df.loc['day', demo_option1] = len(first_df.loc[first_df[demo] == demo_option1])
    tabel_df.loc['day', demo_option2] = len(first_df.loc[first_df[demo] == demo_option2])
    tabel_df.loc['night', demo_option1] = len(second_df.loc[second_df[demo] == demo_option1])
    tabel_df.loc['night', demo_option2] = len(second_df.loc[second_df[demo] == demo_option2])
    oddsratio, pvalue = stats.fisher_exact(np.array(tabel_df))
    print(print_col)
    print('oddsratio : %.3f, pvalue: %.3f \n' % (oddsratio, pvalue))


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles_dataset'
    root_data_path = Path(__file__).parent.absolute().parents[2].joinpath('datasets', bucket_str)

    igtb_df = read_AllBasic(root_data_path)
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

    print()
    day_df = nurse_df.loc[nurse_df['Shift'] == 'Day shift']
    night_df = nurse_df.loc[nurse_df['Shift'] == 'Night shift']
    final_stats_df = pd.DataFrame()

    # print('\\multicolumn{1}{l}{{\\textbf{%s}}} & & & & & & \\rule{0pt}{2ex} \\\\ \n' % 'Gender')
    print_latex_all(nurse_df, day_df, night_df, demo='Gender', demo_option='Female', print_col='Gender (Female)', stat='cate', end=True)
    print_latex_all(nurse_df, day_df, night_df, demo='native_lang', demo_option='Yes', print_col='Native Language = English', stat='cate', end=True)

    print('\\multicolumn{1}{l|}{{{%s}}} & & & & & & \\rule{0pt}{2.25ex} \\\\ \\hline \n' % 'Education')
    print_latex_all(nurse_df, day_df, night_df, demo='Educ', demo_option='Some college or College', print_col='College', stat='cate')
    print_latex_all(nurse_df, day_df, night_df, demo='Educ', demo_option='Graduate', print_col='Graduate', stat='cate', end=True)

    row_df = print_latex_all(nurse_df, day_df, night_df, demo='age', demo_option='', print_col='Age(Mean $\\pm$ SD)', stat='num')
    final_stats_df = pd.concat([final_stats_df, row_df])

    print_latex_all(nurse_df, day_df, night_df, demo='Age', demo_option='< 40 Years', print_col='Age < 40 Years (n (\\%))', stat='cate')
    print_latex_all(nurse_df, day_df, night_df, demo='Age', demo_option='>= 40 Years', print_col='Age >= 40 Years (n (\\%))', stat='cate', end=True)

    affect_cols = ['stai', 'pan_PosAffect', 'pan_NegAffect', 'swls', 'bfi_Neuroticism', 'bfi_Conscientiousness', 'bfi_Extraversion', 'bfi_Agreeableness', 'bfi_Openness']

    for col in affect_cols:
        row_df = print_latex_all(nurse_df, day_df, night_df, demo=col, demo_option='', print_col=col_dict[col] + '(Mean $\\pm$ SD)', stat='num')
        final_stats_df = pd.concat([final_stats_df, row_df])

    row_df = print_latex_all(nurse_df, day_df, night_df, demo='psqi', demo_option='', print_col=col_dict['psqi'] + '(Mean $\\pm$ SD)', stat='num')
    final_stats_df = pd.concat([final_stats_df, row_df])

    print_latex_all(nurse_df, day_df, night_df, demo='PSQI', demo_option='PSQI < 7', print_col='PSQI < 7 (n (\\%))', stat='cate')
    print_latex_all(nurse_df, day_df, night_df, demo='PSQI', demo_option='PSQI >= 7', print_col='PSQI >= 7 (n (\\%))', stat='cate', end=True)

    print_odd_ratio(day_df, night_df, demo='Age', demo_option1='< 40 Years', demo_option2='>= 40 Years', print_col='Age')
    print_odd_ratio(day_df, night_df, demo='Gender', demo_option1='Female', demo_option2='Male', print_col='Gender')
    print_odd_ratio(day_df, night_df, demo='Educ', demo_option1='Some college or College', demo_option2='Graduate', print_col='Highest Degree Earned')
    print_odd_ratio(day_df, night_df, demo='native_lang', demo_option1='Yes', demo_option2='No', print_col='Native language = English')
