from util.load_data_basic import *
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.formula.api import ols
import statsmodels.api as sm


def read_participant_mgt(id, mgt_df, work_timeline_df, type, shift='day'):
    ema_df = mgt_df.loc[mgt_df['participant_id'] == id]
    ema_df = ema_df.dropna()
    ema_df = ema_df.sort_index()

    save_df = pd.DataFrame()
    for index_work, row_df in work_timeline_df.iterrows():
        day_ema_df = ema_df[row_df['start']:row_df['end']]

        if len(day_ema_df) == 0:
            continue
        for index_ema, row_ema_df in day_ema_df.iterrows():
            save_row_df = pd.DataFrame(index=[index_ema])
            save_row_df['score'] = row_ema_df[type]
            save_row_df['work'] = row_df['work']
            save_df = save_df.append(save_row_df)

    if len(save_df) == 0:
        return pd.DataFrame()

    participant_work_df = pd.DataFrame(index=[id])
    participant_work_df.loc[:, 'type'] = type
    participant_work_df.loc[:, 'shift'] = shift
    if len(save_df.loc[save_df['work'] == 1]) < 10:
        participant_work_df.loc[:, 'score'] = np.nan
    else:
        participant_work_df.loc[:, 'score'] = np.nanmean(save_df.loc[save_df['work'] == 1]['score'])
    participant_work_df.loc[:, 'work'] = 'work'

    participant_off_df = pd.DataFrame(index=[id])
    participant_off_df.loc[:, 'type'] = type
    participant_off_df.loc[:, 'shift'] = shift
    if len(save_df.loc[save_df['work'] == 0]) < 10:
        participant_off_df.loc[:, 'score'] = np.nan
    else:
        participant_off_df.loc[:, 'score'] = np.nanmean(save_df.loc[save_df['work'] == 0]['score'])
    participant_off_df.loc[:, 'work'] = 'off'

    participant_all_df = pd.DataFrame(index=[id])
    participant_all_df.loc[:, 'type'] = type
    participant_all_df.loc[:, 'shift'] = shift
    participant_all_df['total_survey'] = len(ema_df)
    participant_all_df.loc[:, 'work'] = 'all'

    return_df = participant_work_df.append(participant_off_df)
    return_df = return_df.append(participant_all_df)

    return return_df


def print_stats(day_data, night_data, col, func=stats.kruskal, func_name='K-S'):
    print(col)
    print('Number of valid participant: workday: %i; offday: %i\n' % (len(day_data), len(night_data)))

    # Print
    print('Workday: median = %.2f, mean = %.2f' % (np.nanmedian(day_data), np.nanmean(day_data)))
    print('Off-day: median = %.2f, mean = %.2f' % (np.nanmedian(night_data), np.nanmean(night_data)))

    # stats test
    stat, p = func(day_data, night_data)
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))

    return p


def plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks, shift='day', work='work'):
    # Plot
    fig, axes = plt.subplots(2, 4, figsize=(12, 8.5))

    color_list = ['r', 'y', 'b', 'g']
    x_label = ['Postive affect', 'Negative affect', 'Anxiety', 'Stress']
    plot_col_list = ['pand_PosAffect', 'pand_NegAffect', 'anxiety', 'stressd']
    work_list = ['work', 'off']
    shift_list = ['day', 'night']

    data_dict = {}

    for j, plot_col in enumerate(plot_col_list):
        tmp_df = mgt_df.loc[mgt_df['type'] == plot_col_list[j]]
        tmp_df = tmp_df.loc[tmp_df['work'] == 'all']
        print('total survey for %s is %d' % (plot_col_list[j], np.nansum(tmp_df['total_survey'])))

    for i, shift in enumerate(shift_list):

        data_dict[i] = {}

        for j, plot_col in enumerate(plot_col_list):
            tmp_df = mgt_df.loc[mgt_df['type'] == plot_col_list[j]]
            tmp_df = tmp_df.loc[tmp_df['shift'] == shift]
            tmp_df = tmp_df[['score', 'work']]

            tmp_df = tmp_df.loc[tmp_df['work'] == work]
            data_dict[i][j] = tmp_df['score'].dropna()

            sns.set_style("white")
            sns.distplot(tmp_df['score'].dropna(), bins=bins[j], norm_hist=True, hist=False, kde=True,
                         ax=axes[i][j], color=color_list[j], kde_kws={'shade': True, 'linewidth': 1, 'alpha': 0.4})
            axes[i][j].set_ylim([0, y_ticks[j][-1]])
            axes[i][j].set_xlim([0, x_ticks[j][-1]])

            axes[i][j].set_xticks(x_ticks[j], minor=False)
            axes[i][j].set_yticks(y_ticks[j], minor=False)
            axes[i][j].xaxis.set_tick_params(labelsize=18)
            axes[i][j].yaxis.set_tick_params(labelsize=18)

            for label in axes[i][j].get_xticklabels():
                label.set_weight('bold')
            for label in axes[i][j].get_yticklabels():
                label.set_weight('bold')

            axes[i][j].set_ylabel('', fontsize=13, fontweight='bold')

    axes[0][0].set_ylabel('Participant Number\n(Day)', fontsize=18, fontweight='bold')
    axes[1][0].set_ylabel('Participant Number\n(Night)', fontsize=18, fontweight='bold')

    for j, plot_col in enumerate(plot_col_list):
        day_data = data_dict[0][j]
        night_data = data_dict[1][j]

        tmp_df = mgt_df.loc[mgt_df['type'] == plot_col_list[j]]
        tmp_df = tmp_df.loc[tmp_df['work'] == work]

        tmp_df = tmp_df[['score'] + ['shift']]
        tmp_df = tmp_df.dropna()
        tmp_df['shift'] = pd.get_dummies(tmp_df['shift'], drop_first=True)
        lm = ols('score' + ' ~ shift', data=tmp_df).fit()
        result = sm.stats.anova_lm(lm, typ=2)  # Type 2 ANOVA DataFrame
        p = result.loc['shift', 'PR(>F)']
        F = result.loc['shift', 'F']

        print(work + '-' + plot_col)
        print(result)
        # p = print_stats(day_data, night_data, plot_col, func=stats.mannwhitneyu)

        axes[0][j].set_xlabel('')
        if p > 0.001:
            axes[1][j].set_xlabel(x_label[j] + '\n(p='+"{:.3f}".format(p)+')', fontsize=18, fontweight='bold')
        else:
            axes[1][j].set_xlabel(x_label[j] + '\n(p<0.001)', fontsize=18, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.92])

    if work == 'work':
        plt.figtext(0.5, 0.95, "Average EMA Responses On Workdays (PDF)", ha="center", va="top", fontsize=20, color="black", weight='bold')
        plt.savefig('mgt_work.png', dpi=400, bbox_inches='tight', pad_inches=0)
    else:
        plt.figtext(0.5, 0.95, "Average EMA Responses Of Off-days (PDF)", ha="center", va="top", fontsize=20, color="black", weight='bold')
        plt.savefig('mgt_off.png', dpi=400, bbox_inches='tight', pad_inches=0)

    # plt.show()


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    # Read demographics, igtb, etc.
    igtb_df = read_AllBasic(root_data_path)
    psqi_raw_igtb = read_PSQI_Raw(root_data_path)
    igtb_raw = read_IGTB_Raw(root_data_path)

    nurse_df = return_nurse_df(igtb_df)
    nurse_id = list(nurse_df.participant_id)
    nurse_id.sort()

    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    # data = sm.datasets.get_rdataset("dietox", "geepack").data
    # md = smf.mixedlm("Weight ~ Time", data, groups=data["Pig"])
    # mdf = md.fit()

    # Read daily EMAs
    anxiety_mgt_df, stress_mgt_df, pand_mgt_df = read_MGT(root_data_path)

    if Path.exists(Path.cwd().joinpath('mgt.csv.gz')) is False:
        mgt_df = pd.DataFrame()
        for id in nurse_id:
            if Path.exists(root_data_path.joinpath('processed', 'timeline', id + '.csv.gz')) is False:
                continue

            shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id]['Shift'].values[0] == 'Day shift' else 'night'
            timeline_df = pd.read_csv(root_data_path.joinpath('processed', 'timeline', id + '.csv.gz'), index_col=0)

            mgt_df = mgt_df.append(read_participant_mgt(id, anxiety_mgt_df, timeline_df, 'anxiety', shift=shift))
            mgt_df = mgt_df.append(read_participant_mgt(id, stress_mgt_df, timeline_df, 'stressd', shift=shift))
            mgt_df = mgt_df.append(read_participant_mgt(id, pand_mgt_df, timeline_df, 'pand_PosAffect', shift=shift))
            mgt_df = mgt_df.append(read_participant_mgt(id, pand_mgt_df, timeline_df, 'pand_NegAffect', shift=shift))

        mgt_df.to_csv(Path.cwd().joinpath('mgt.csv.gz'), compression='gzip')
    else:
        mgt_df = pd.read_csv(Path.cwd().joinpath('mgt.csv.gz'), index_col=0)

    # Plot parameters
    bins = [np.arange(4.5, 26, 1), np.arange(4.5, 26, 1), np.arange(0.25, 6, 0.5), np.arange(0.25, 6, 0.5)]
    x_ticks = [[5, 10, 15, 20, 25], [5, 10, 15, 20, 25], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]
    y_ticks1 = [np.arange(0, 0.21, 0.05), np.arange(0, 0.51, 0.1), np.arange(0, 1.26, 0.25), np.arange(0, 1.01, 0.25)]
    y_ticks2 = [np.arange(0, 0.21, 0.05), np.arange(0, 0.51, 0.1), np.arange(0, 1.01, 0.25), np.arange(0, 1.01, 0.25)]
    plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks1, work='work')
    plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks2, work='off')




