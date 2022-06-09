from util.load_data_basic import *
from util.load_sensor_data import *
from scipy import stats
from datetime import timedelta


if __name__ == '__main__':
    # Read ground truth data
    bucket_str = 'tiles-phase1-opendataset'
    root_data_path = Path('/Volumes/Tiles/').joinpath(bucket_str)

    # read ground-truth data
    igtb_df = read_AllBasic(root_data_path)

    nurse_df = return_nurse_df(igtb_df)
    sleep_stats_df = pd.DataFrame()

    id_list = list(nurse_df['participant_id'])
    id_list.sort()

    for id in id_list:

        shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id].Shift[0] == 'Day shift' else 'night'
        sleep_metadata_df = read_sleep_data(root_data_path, id)
        if sleep_metadata_df is None:
            continue

        print('Process participant: %s' % (id))
        if Path.exists(Path.cwd().joinpath('..', '..', '..', 'data', 'processed', 'timeline', id + '.csv.gz')) is False:
            continue
        timeline_df = pd.read_csv(Path.cwd().joinpath('..', '..', '..', 'data', 'processed', 'timeline', id + '.csv.gz'), index_col=0)
        main_sleep_df = sleep_metadata_df.loc[sleep_metadata_df['isMainSleep'] == True]

        if len(main_sleep_df) == 0:
            continue

        sleep_df = pd.DataFrame(index=[id])

        sleep_df.loc[:, 'id'] = id
        sleep_df.loc[:, 'shift'] = shift
        sleep_df.loc[:, 'len'] = len(main_sleep_df)

        sleep_stats_df = pd.concat([sleep_stats_df, sleep_df])

    print()


