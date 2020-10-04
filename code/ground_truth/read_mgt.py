from util.load_data_basic import *
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
from matplotlib import font_manager


def read_participant_mgt(mgt_df, work_timeline_df, type, shift='day'):
    tmp_df = mgt_df.loc[mgt_df['participant_id'] == id]
    tmp_df = tmp_df.dropna()

    save_df = pd.DataFrame()

    for i, row_df in tmp_df.iterrows():
        adj_time_str = pd.to_datetime(row_df['start_ts']).asm8
        # adj_date_str = pd.to_datetime(adj_time_str).strftime(date_time_format)[:-3]

        start_off_list = list(pd.to_datetime(adj_time_str) - pd.to_datetime(work_timeline_df['start']))
        end_off_list = list(pd.to_datetime(workday_timeline_df['end']) - pd.to_datetime(adj_time_str))

        save_row_df = pd.DataFrame(index=[row_df['start_ts']])
        save_row_df.loc[:, 'score'] = row_df[type]
        save_row_df['work'] = 0
        for j in range(len(start_off_list)):
            if start_off_list[j].total_seconds() > 0 and end_off_list[j].total_seconds() > 0:
                save_row_df['work'] = 1
        save_df = save_df.append(save_row_df)

    if len(save_df) == 0:
        return pd.DataFrame()

    participant_work_df = pd.DataFrame(index=[id])
    participant_work_df.loc[:, 'type'] = type
    participant_work_df.loc[:, 'shift'] = shift
    participant_work_df.loc[:, 'score'] = np.nanmean(save_df.loc[save_df['work'] == 1]['score'])
    participant_work_df.loc[:, 'work'] = 1

    participant_off_df = pd.DataFrame(index=[id])
    participant_off_df.loc[:, 'type'] = type
    participant_off_df.loc[:, 'shift'] = shift
    participant_off_df.loc[:, 'score'] = np.nanmean(save_df.loc[save_df['work'] == 0]['score'])
    participant_off_df.loc[:, 'work'] = 0

    return_df = participant_work_df.append(participant_off_df)

    return return_df


def print_stats(day_data, night_data, col, func=stats.kruskal, func_name='K-S'):
    print(col)
    print('Number of valid participant: day: %i; night: %i\n' % (len(day_data), len(night_data)))

    # Print
    print('Day shift: mean = %.2f, std = %.2f' % (np.nanmean(day_data), np.nanstd(day_data)))
    print('Night shift: mean = %.2f, std = %.2f' % (np.nanmean(night_data), np.nanstd(night_data)))

    # stats test
    stat, p = func(day_data, night_data)
    print(func_name + ' test for %s' % col)
    print('Statistics = %.3f, p = %.3f\n\n' % (stat, p))

    return p


def convert_days_at_work(days_at_work_df, participant_id, shift='day'):
    if participant_id not in list(days_at_work_df.columns):
        return pd.DataFrame()

    work_df = days_at_work_df[participant_id].dropna()
    if len(work_df) == 0:
        return pd.DataFrame()

    work_df = work_df.sort_index()

    save_df = pd.DataFrame()
    for i in range(len(work_df)):
        date_str = work_df.index[i]
        if shift == 'day':
            start_str = (pd.to_datetime(date_str).replace(hour=7) - timedelta(hours=6)).strftime(date_time_format)[:-3]
            end_str = (pd.to_datetime(date_str).replace(hour=7) + timedelta(hours=18)).strftime(date_time_format)[:-3]
            row_df = pd.DataFrame(index=[start_str])
            row_df['start'] = start_str
            row_df['end'] = end_str
            save_df = save_df.append(row_df)
        else:
            if i + 1 < len(work_df):
                if (pd.to_datetime(work_df.index[i+1]) - pd.to_datetime(work_df.index[i])).total_seconds() < 2 * 3600 * 24:
                    start_str = (pd.to_datetime(date_str).replace(hour=19) - timedelta(hours=6)).strftime(date_time_format)[:-3]
                    end_str = (pd.to_datetime(date_str).replace(hour=19) + timedelta(hours=18)).strftime(date_time_format)[:-3]
                    row_df = pd.DataFrame(index=[start_str])
                    row_df['start'] = start_str
                    row_df['end'] = end_str
                    save_df = save_df.append(row_df)

    if len(save_df) < 15:
        return pd.DataFrame()

    return save_df

'''
def plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks, work=0):
    # Plot
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))

    color_list = ['r', 'y', 'b', 'g']
    x_label = ['Postive affect', 'Negative affect', 'Anxiety', 'Stress']
    plot_col_list = ['pand_PosAffect', 'pand_NegAffect', 'anxiety', 'stressd']
    shift_list = ['day', 'night']

    data_dict = {}

    for i, shift in enumerate(shift_list):
        axes[0][0].set_ylabel('Participant Number\n(Day shift)', fontsize=13, fontweight='bold')
        axes[1][0].set_ylabel('Participant Number\n(Night shift)', fontsize=13, fontweight='bold')
        data_dict[i] = {}

        for j, plot_col in enumerate(plot_col_list):
            tmp_df = mgt_df.loc[mgt_df['type'] == plot_col_list[j]]
            tmp_df = tmp_df.loc[tmp_df['work'] == work]
            tmp_df = tmp_df[['score', 'shift']]

            tmp_df = tmp_df.loc[tmp_df['shift'] == shift]
            data_dict[i][j] = tmp_df['score'].dropna()

            sns.set_style("white")
            sns.distplot(tmp_df['score'].dropna(), bins=bins[j], kde=False, ax=axes[i][j], color=color_list[j],
                         hist_kws={"rwidth": 0.8, 'edgecolor': 'black', 'alpha': 0.65, 'linewidth': 1})
            axes[i][j].set_xticks(x_ticks[j], minor=False)
            axes[i][j].set_yticks(y_ticks[j], minor=False)
            axes[i][j].xaxis.set_tick_params(labelsize=13)
            axes[i][j].yaxis.set_tick_params(labelsize=13)

            axes[0][j].set_xlabel('')
            axes[1][j].set_xlabel(x_label[j], fontsize=13, fontweight='bold')

            for label in axes[i][j].get_xticklabels():
                label.set_weight('bold')
            for label in axes[i][j].get_yticklabels():
                label.set_weight('bold')

    for j, plot_col in enumerate(plot_col_list):
        day_data = data_dict[0][j]
        night_data = data_dict[1][j]
        
        print_stats(day_data, night_data, plot_col)


    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    # plt.figtext(0.5,0.95, "Average EMA responses On Workdays", ha="center", va="top", fontsize=14, color="black", weight='bold')
    if work == 1:
        plt.figtext(0.5, 0.95, "Average EMA responses On Workdays", ha="center", va="top", fontsize=14, color="black", weight='bold')
        plt.savefig('day_night_work.png', dpi=400, bbox_inches='tight', pad_inches=0)
    else:
        plt.figtext(0.5, 0.95, "Average EMA responses On Off-days", ha="center", va="top", fontsize=14, color="black", weight='bold')
        plt.savefig('day_night_off.png', dpi=400, bbox_inches='tight', pad_inches=0)
    # plt.show()
'''


def plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks, shift='day'):
    # Plot
    fig, axes = plt.subplots(2, 4, figsize=(12, 6))

    color_list = ['r', 'y', 'b', 'g']
    x_label = ['Postive affect', 'Negative affect', 'Anxiety', 'Stress']
    plot_col_list = ['pand_PosAffect', 'pand_NegAffect', 'anxiety', 'stressd']
    work_list = [0, 1]

    data_dict = {}

    for i, work in enumerate(work_list):
        axes[0][0].set_ylabel('Participant Number\n(Workdays)', fontsize=13, fontweight='bold')
        axes[1][0].set_ylabel('Participant Number\n(Off-days)', fontsize=13, fontweight='bold')
        data_dict[i] = {}

        for j, plot_col in enumerate(plot_col_list):
            tmp_df = mgt_df.loc[mgt_df['type'] == plot_col_list[j]]
            tmp_df = tmp_df.loc[tmp_df['shift'] == shift]
            tmp_df = tmp_df[['score', 'work']]

            tmp_df = tmp_df.loc[tmp_df['work'] == work]
            data_dict[i][j] = tmp_df['score'].dropna()

            sns.set_style("white")
            sns.distplot(tmp_df['score'].dropna(), bins=bins[j], kde=False, ax=axes[i][j], color=color_list[j],
                         hist_kws={"rwidth": 0.8, 'edgecolor': 'black', 'alpha': 0.65, 'linewidth': 1})

            # sns.displot(tmp_df['score'].dropna(), ax=axes[i][j], kind="kde", fill=True)

            axes[i][j].set_xticks(x_ticks[j], minor=False)
            axes[i][j].set_yticks(y_ticks[j], minor=False)
            axes[i][j].xaxis.set_tick_params(labelsize=13)
            axes[i][j].yaxis.set_tick_params(labelsize=13)

            for label in axes[i][j].get_xticklabels():
                label.set_weight('bold')
            for label in axes[i][j].get_yticklabels():
                label.set_weight('bold')

    for j, plot_col in enumerate(plot_col_list):
        day_data = data_dict[0][j]
        night_data = data_dict[1][j]

        p = print_stats(day_data, night_data, plot_col)

        axes[0][j].set_xlabel('')
        axes[1][j].set_xlabel(x_label[j]+'\n(p='+"{:.3f}".format(p)+')', fontsize=13, fontweight='bold')

    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    # plt.figtext(0.5,0.95, "Average EMA responses On Workdays", ha="center", va="top", fontsize=14, color="black", weight='bold')

    if shift == 'day':
        plt.figtext(0.5, 0.95, "Average EMA Responses Of Day Shift Nurses", ha="center", va="top", fontsize=14, color="black", weight='bold')
        plt.savefig('day.png', dpi=400, bbox_inches='tight', pad_inches=0)
    else:
        plt.figtext(0.5, 0.95, "Average EMA Responses Of Night Shift Nurses", ha="center", va="top", fontsize=14, color="black", weight='bold')
        plt.savefig('night.png', dpi=400, bbox_inches='tight', pad_inches=0)

    plt.show()


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path(__file__).parent.absolute().parents[1].joinpath('data', bucket_str)

    # Read demographics, igtb, etc.
    igtb_df = read_AllBasic(root_data_path)
    psqi_raw_igtb = read_PSQI_Raw(root_data_path)
    igtb_raw = read_IGTB_Raw(root_data_path)
    days_at_work_df = read_days_at_work(root_data_path)

    nurse_df = return_nurse_df(igtb_df)
    day_nurse_id = list(nurse_df.loc[nurse_df['Shift'] == 'Day shift'].participant_id)
    night_nurse_id = list(nurse_df.loc[nurse_df['Shift'] == 'Night shift'].participant_id)

    # Read daily EMAs
    anxiety_mgt_df, stress_mgt_df, pand_mgt_df = read_MGT(root_data_path)

    mgt_df = pd.DataFrame()
    for id in day_nurse_id:
        workday_timeline_df = convert_days_at_work(days_at_work_df, id, shift='day')
        if len(workday_timeline_df) == 0:
            continue

        mgt_df = mgt_df.append(read_participant_mgt(anxiety_mgt_df, workday_timeline_df, 'anxiety', shift='day'))
        mgt_df = mgt_df.append(read_participant_mgt(stress_mgt_df, workday_timeline_df, 'stressd', shift='day'))
        mgt_df = mgt_df.append(read_participant_mgt(pand_mgt_df, workday_timeline_df, 'pand_PosAffect', shift='day'))
        mgt_df = mgt_df.append(read_participant_mgt(pand_mgt_df, workday_timeline_df, 'pand_NegAffect', shift='day'))

    for id in night_nurse_id:
        workday_timeline_df = convert_days_at_work(days_at_work_df, id, shift='night')
        if len(workday_timeline_df) == 0:
            continue

        mgt_df = mgt_df.append(read_participant_mgt(anxiety_mgt_df, workday_timeline_df, 'anxiety', shift='night'))
        mgt_df = mgt_df.append(read_participant_mgt(stress_mgt_df, workday_timeline_df, 'stressd', shift='night'))
        mgt_df = mgt_df.append(read_participant_mgt(pand_mgt_df, workday_timeline_df, 'pand_PosAffect', shift='night'))
        mgt_df = mgt_df.append(read_participant_mgt(pand_mgt_df, workday_timeline_df, 'pand_NegAffect', shift='night'))

    # Plot parameters
    bins = [np.arange(4.5, 26, 1), np.arange(4.5, 26, 1), np.arange(0.25, 6, 0.5), np.arange(0.25, 6, 0.5)]
    x_ticks = [[5, 10, 15, 20, 25], [5, 10, 15, 20, 25], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]
    y_ticks1 = [np.arange(0, 13, 3), np.arange(0, 34, 8), np.arange(0, 34, 8), np.arange(0, 34, 8)]
    y_ticks2 = [np.arange(0, 13, 3), np.arange(0, 21, 5), np.arange(0, 21, 5), np.arange(0, 21, 5)]
    plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks1, shift='day')
    plot_day_night_mgt(mgt_df, bins, x_ticks, y_ticks2, shift='night')




