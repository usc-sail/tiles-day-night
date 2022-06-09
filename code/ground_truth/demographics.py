from util.load_data_basic import *
from scipy import stats
from scipy.stats import skew


def print_stats(igtb_df, col, demo='', demo_option=[], func=stats.kruskal, group=''):
    first_df = igtb_df.loc[igtb_df[demo] == demo_option[0]]
    second_df = igtb_df.loc[igtb_df[demo] == demo_option[1]]

    print('Group')
    print(col)
    print('Number of valid participant: %s: %i; %s: %i\n' % (demo_option[0], len(first_df[col].dropna()),
                                                             demo_option[1], len(second_df[col].dropna())))

    # Print
    # print('Total: mean = %.2f, std = %.2f, range is %.3f - %.3f' % (np.mean(igtb_df[col]), np.std(igtb_df[col]), np.min(igtb_df[col]), np.max(igtb_df[col])))
    print('%s: mean = %.2f, std = %.2f' % (demo_option[0], np.nanmean(first_df[col]), np.nanstd(second_df[col])))
    # print('Day shift: range is %.3f - %.3f' % (np.min(day_nurse_df[col]), np.max(day_nurse_df[col])))
    # print('Day shift: skew = %.3f' % (skew(day_nurse_df[col])))

    print('%s: mean = %.2f, std = %.2f' % (demo_option[1], np.nanmean(first_df[col]), np.nanstd(second_df[col])))
    # print('Night shift: range is %.3f - %.3f' % (np.min(night_nurse_df[col]), np.max(night_nurse_df[col])))
    # print('Night shift: skew = %.3f' % (skew(night_nurse_df[col])))

    # stats test
    stat, p = func(first_df[col].dropna(), second_df[col].dropna())
    print('test for %s' % col)
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

    # shift_pre-study
    nurse_df = igtb_df.loc[igtb_df['job'] == 'nurse']
    print('Total number of participants: %d' % (len(nurse_df)))

    print()
    day_df = nurse_df.loc[nurse_df['Shift'] == 'Day shift']
    night_df = nurse_df.loc[nurse_df['Shift'] == 'Night shift']
    print('Day shift: %d (%.2f)' % (len(day_df), len(day_df)/len(nurse_df) * 100))
    print('Night shift: %d (%.2f)' % (len(night_df), len(night_df) / len(nurse_df) * 100))

    print()
    male_df = nurse_df.loc[nurse_df['gender'] == 1]
    female_df = nurse_df.loc[nurse_df['gender'] == 2]
    print('Male: %d (%.2f)' % (len(male_df), len(male_df) / len(nurse_df) * 100))
    print('Female: %d (%.2f)' % (len(female_df), len(female_df) / len(nurse_df) * 100))

    print()
    college_df = nurse_df.loc[nurse_df['education'] > 2]
    graduate_df = nurse_df.loc[nurse_df['education'] > 4]
    print('College: %d (%.2f)' % (len(college_df), len(college_df) / len(nurse_df) * 100))
    print('Graduate: %d (%.2f)' % (len(graduate_df), len(graduate_df) / len(nurse_df) * 100))

    print()

    first_df = nurse_df.loc[(nurse_df['age'] >= 20) & (nurse_df['age'] < 30)]
    second_df = nurse_df.loc[(nurse_df['age'] >= 30) & (nurse_df['age'] < 40)]
    third_df = nurse_df.loc[(nurse_df['age'] >= 40)]

    print('Mean age: %.2f (SD: %.2f, (%d - %d))' % (np.nanmean(nurse_df['age']), np.nanstd(nurse_df['age']), np.nanmin(nurse_df['age']), np.nanmax(nurse_df['age'])))
    print('20 - 29 year old: %d (%.2f)' % (len(first_df), len(first_df) / len(nurse_df) * 100))
    print('30 - 39 year old: %d (%.2f)' % (len(second_df), len(second_df) / len(nurse_df) * 100))
    print('Above 40 year old: %d (%.2f)' % (len(third_df), len(third_df) / len(nurse_df) * 100))

    print()
    supervise_df = nurse_df.loc[nurse_df['supervise'] == 1]
    print('Supervisor: %d (%.2f)' % (len(supervise_df), len(supervise_df) / len(nurse_df) * 100))



