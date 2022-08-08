from datetime import timedelta
from util.load_data_basic import *
import pytz

pt = pytz.timezone('US/Pacific')
utc = pytz.timezone('UTC')


def create_folder(save_path):
    if Path.exists(save_path) is False: Path.mkdir(save_path)


def return_day_data(start_str, end_str, data):
    if len(data) == 0:
        return pd.DataFrame()
    else:
        return data[start_str:end_str]


if __name__ == '__main__':

    # Bucket information
    bucket_str = 'tiles-phase1-opendataset'
    audio_bucket_str = 'tiles-phase1-opendataset-audio'

    # Download the participant information data
    root_data_path = Path(__file__).parent.absolute().parents[1].joinpath('data', bucket_str)

    # Read all igtb
    # please contact the author to access: igtb_day_night.csv.gz
    if Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz').exists() == False:
        igtb_df = read_AllBasic(root_data_path)
        igtb_df.to_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'))
    igtb_df = pd.read_csv(Path(os.path.realpath(__file__)).parents[1].joinpath('igtb_day_night.csv.gz'), index_col=0)
    days_at_work_df = read_days_at_work(root_data_path)

    nurse_df = return_nurse_df(igtb_df)
    day_nurse_id = list(nurse_df.loc[nurse_df['Shift'] == 'Day shift'].participant_id)
    night_nurse_id = list(nurse_df.loc[nurse_df['Shift'] == 'Night shift'].participant_id)
    nurse_id_list = list(nurse_df.participant_id)
    nurse_id_list.sort()

    ema_days_at_work_df = pd.read_csv(root_data_path.joinpath('surveys', 'scored', 'EMAs', 'work.csv.gz'), index_col=3)
    save_days_at_work = days_at_work_df.copy()

    for id in nurse_id_list[:]:

        print('process %s' % (id))

        shift = 'day' if nurse_df.loc[nurse_df['participant_id'] == id]['Shift'].values[0] == 'Day shift' else 'night'
        owl_in_one_df, om_df = pd.DataFrame(), pd.DataFrame()

        if Path.exists(root_data_path.joinpath('owlinone', 'jelly', id + '.csv.gz')) is True:
            owl_in_one_df = pd.read_csv(root_data_path.joinpath('owlinone', 'jelly', id + '.csv.gz'), index_col=0)
            owl_in_one_df = owl_in_one_df.sort_index()
        if Path.exists(root_data_path.joinpath('omsignal', 'features', id + '.csv.gz')) is True:
            om_df = pd.read_csv(root_data_path.joinpath('omsignal', 'features', id + '.csv.gz'), index_col=0)
            om_df = om_df.sort_index()

        ema_id_df = ema_days_at_work_df.loc[ema_days_at_work_df['participant_id'] == id]
        save_df = pd.DataFrame()

        # id is not in days at work data or data is empty
        if id not in list(days_at_work_df.columns):
            continue

        for i in range(len(days_at_work_df)):
            # a day cycle for day shift start 7am to next 7am, and 7pm-7pm for a night shift nurses
            start_hour = 7 if shift == 'day' else 19
            start_str = pd.to_datetime(days_at_work_df.index[i]).replace(hour=start_hour).strftime(date_time_format)[:-3]
            end_str = (pd.to_datetime(start_str) + timedelta(hours=24)).strftime(date_time_format)[:-3]

            # data for a day cycle
            tmp_om_df = return_day_data(start_str, end_str, om_df)
            tmp_owl_df = return_day_data(start_str, end_str, owl_in_one_df)
            tmp_ema_df = return_day_data(start_str, end_str, ema_id_df)

            # save the tag
            ema_work = False
            if len(tmp_ema_df) != 0:
                ema_work = True if 'yes' in list(tmp_ema_df['work_status']) else False

            row_df = pd.DataFrame(index=[start_str])
            row_df['start'] = start_str
            row_df['end'] = end_str
            if len(tmp_om_df) != 0 or len(tmp_owl_df) != 0 or ema_work is True: row_df['work'] = 1
            else: row_df['work'] = 0
            save_df = save_df.append(row_df)

        save_path = Path(__file__).parent.absolute().parents[1].joinpath('data')
        create_folder(save_path.joinpath('processed'))
        create_folder(save_path.joinpath('processed', 'timeline'))
        save_df.to_csv(save_path.joinpath('processed', 'timeline', id + '.csv.gz'), compression='gzip')

