import os, errno
import pandas as pd
import numpy as np
from pathlib import Path

# date_time format
date_time_format = '%Y-%m-%dT%H:%M:%S.%f'
date_only_date_time_format = '%Y-%m-%d'


# Load raw IGTB data
def read_IGTB_Raw(data_directory):
    Day_IGTB = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_DAY_IGTB.csv'), index_col=2).iloc[1:, :]
    Night_IGTB = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_NIGHT_IGTB.csv'), index_col=2).iloc[1:, :]
    Pilot_IGTB = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_PILOT_IGTB.csv'), index_col=2).iloc[1:, :]

    IGTB = Day_IGTB.append(Night_IGTB)
    IGTB = IGTB.append(Pilot_IGTB)

    return IGTB


# Load IGTB data
def read_IGTB(data_directory):
    IGTB_part1 = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'scored', 'baseline', 'part_one-abs_vocab_gats_audit_psqi_ipaq_iod_ocb_irb_itp_bfi_pan_stai.csv.gz'), index_col=1)
    IGTB_part2 = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'scored', 'baseline', 'part_two-rand_swls_pss_mpfi_waaq_uwes_pcq_chss.csv.gz'), index_col=1)

    IGTB = pd.merge(IGTB_part1, IGTB_part2, left_on='participant_id', right_on='participant_id', how='outer')

    return IGTB


def read_IGTB_sub(data_directory):
    
#     igtb_pilot_df = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_PILOT_IGTB.csv'), index_col=2)
#     igtb_pilot_df = igtb_pilot_df.drop(index=['Name'])

#     igtb_night_df = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_NIGHT_IGTB.csv'), index_col=2)
#     igtb_night_df = igtb_night_df.drop(index=['Name'])

#     igtb_day_df = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_DAY_IGTB.csv'), index_col=2)
#     igtb_day_df = igtb_day_df.drop(index=['Name'])

#     igtb_df = pd.DataFrame()
#     igtb_df = igtb_df.append(igtb_pilot_df)
#     igtb_df = igtb_df.append(igtb_night_df)
#     igtb_df = igtb_df.append(igtb_day_df)
    
    igtb_df = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'demographics', 'igtb_day_night.csv.gz'), index_col=2)
    return igtb_df


def getParticipantInfo(data_directory, index=1):
    IDs = pd.read_csv(Path.joinpath(data_directory, 'metadata', 'participant-info', 'mitreids.csv')) # mitreids is from id mapping folder
    participant_info = pd.read_csv(Path.joinpath(data_directory, 'metadata', 'participant-info', 'participant-info.csv.gz'))
    participant_info = participant_info.fillna("")

    for index, row in participant_info.iterrows():
        participant_id = row['ParticipantID']
        participant_info.loc[index, 'MitreID'] = IDs.loc[IDs['participant_id'] == participant_id]['mitre_id'].values[0]

    return participant_info


# Load DemoGraphic data
def read_Demographic(data_directory):
    DemoGraphic = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'demographics', 'part_one-demographics.csv.gz'))
    DemoGraphic.index = pd.to_datetime(DemoGraphic.index)

    return DemoGraphic


# Load pre study data
def read_pre_study_info(data_directory):
    PreStudyInfo = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'demographics', 'part_two-demographics_timings.csv.gz'), index_col=3)
    PreStudyInfo.index = pd.to_datetime(PreStudyInfo.index)

    return PreStudyInfo


# Load all basic data
def read_AllBasic(data_directory):
    # Read participant information
    participant_info = getParticipantInfo(data_directory)

    # Demographic
    Demographic = read_Demographic(data_directory)

    # Read Pre-Study info
    PreStudyInfo = read_pre_study_info(data_directory)

    # Read IGTB info
    IGTB = read_IGTB(data_directory)
    IGTB_sub = read_IGTB_sub(data_directory)
    UserInfo = pd.merge(IGTB, Demographic, left_on='participant_id', right_on='participant_id', how='outer')
    UserInfo = pd.merge(UserInfo, PreStudyInfo, left_on='participant_id', right_on='participant_id', how='outer')
    UserInfo = pd.merge(UserInfo, participant_info, left_on='participant_id', right_on='ParticipantID', how='outer')
    UserInfo = UserInfo.set_index('MitreID').drop(columns='ParticipantID')

    for uid in list(UserInfo.index):
        if uid not in list(IGTB_sub.index):
            continue
        UserInfo.loc[uid, 'gender'] = int(IGTB_sub.loc[uid, 'gender']) if len(str(IGTB_sub.loc[uid, 'gender'])) < 3 else np.nan
        UserInfo.loc[uid, 'age'] = int(IGTB_sub.loc[uid, 'age']) if len(str(IGTB_sub.loc[uid, 'age'])) < 3 else np.nan
        UserInfo.loc[uid, 'bornUS'] = int(IGTB_sub.loc[uid, 'bornUS']) if len(str(IGTB_sub.loc[uid, 'bornUS'])) < 3 else np.nan
        UserInfo.loc[uid, 'language'] = int(IGTB_sub.loc[uid, 'lang']) if len(str(IGTB_sub.loc[uid, 'lang'])) < 3 else np.nan
        UserInfo.loc[uid, 'education'] = int(IGTB_sub.loc[uid, 'educ']) if len(str(IGTB_sub.loc[uid, 'educ'])) < 2 else np.nan
        UserInfo.loc[uid, 'supervise'] = int(IGTB_sub.loc[uid, 'supervise']) if len(str(IGTB_sub.loc[uid, 'supervise'])) < 3 else np.nan
        UserInfo.loc[uid, 'employer_duration'] = int(IGTB_sub.loc[uid, 'duration']) if len(str(IGTB_sub.loc[uid, 'duration'])) < 3 else np.nan
        UserInfo.loc[uid, 'income'] = int(IGTB_sub.loc[uid, 'income']) if len(str(IGTB_sub.loc[uid, 'income'])) < 3 else np.nan

    return UserInfo


def read_PSQI_Raw(data_directory):
    if Path.exists(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'survey', 'psqi_raw.csv.gz')) is True:
        psqi_df = pd.read_csv(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'survey', 'psqi_raw.csv.gz'), index_col=0)
        return psqi_df

    Day_IGTB = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_DAY_IGTB.csv'), index_col=2).iloc[1:, :]
    Night_IGTB = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_NIGHT_IGTB.csv'), index_col=2).iloc[1:, :]
    Pilot_IGTB = pd.read_csv(Path.joinpath(data_directory, 'surveys', 'raw', 'IGTB', 'USC_PILOT_IGTB.csv'), index_col=2).iloc[1:, :]

    IGTB = Day_IGTB.append(Night_IGTB)
    IGTB = IGTB.append(Pilot_IGTB)

    psqi_cols = [col for col in list(IGTB.columns) if 'psqi' in col]
    IGTB = IGTB[psqi_cols]

    psqi_df = pd.DataFrame(index=list(IGTB.index), columns=['psqi_subject_quality', 'psqi_sleep_latency',
                                                            'psqi_sleep_duration', 'psqi_sleep_efficiency',
                                                            'psqi_sleep_disturbance', 'psqi_sleep_medication',
                                                            'psqi_day_dysfunction'])

    for i in range(len(IGTB)):
        uid = list(IGTB.index)[i]
        participant_psqi_df = IGTB.iloc[i, :]

        if uid == 'SG1074':
            print()

        # Component 1
        psqi_df.loc[uid, 'psqi_subject_quality'] = float(participant_psqi_df['psqi9']) - 1

        # Component 2
        sleep_latency = float(participant_psqi_df['psqi2'])
        if sleep_latency <= 15:
            tmp_score = 0
        elif 15 < sleep_latency <= 30:
            tmp_score = 1
        elif 30 < sleep_latency <= 60:
            tmp_score = 2
        else:
            tmp_score = 3

        tmp_score += float(participant_psqi_df['psqi5a'])
        component2_dict = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3}
        psqi_df.loc[uid, 'psqi_sleep_latency'] = component2_dict[tmp_score]

        # Component 3
        sleep_duration = float(participant_psqi_df['psqi4'])

        if sleep_duration >= 7:
            tmp_score = 0
        elif 6 <= sleep_duration < 7:
            tmp_score = 1
        elif 5 <= sleep_duration < 6:
            tmp_score = 2
        else:
            tmp_score = 3
        psqi_df.loc[uid, 'psqi_sleep_duration'] = tmp_score

        # Component 4
        time1 = float(participant_psqi_df['psqi1'][:-2]) + float(participant_psqi_df['psqi1'][-2:]) / 60
        time2 = float(participant_psqi_df['psqi3'][:-2]) + float(participant_psqi_df['psqi3'][-2:]) / 60

        if float(participant_psqi_df['psqi1ampm']) == 1200 and time1 != 12 and time1 != 12.5:
            time1 = time1 + 12
        if float(participant_psqi_df['psqi3ampm']) == 1200 and time2 != 12 and time1 != 12.5:
            time2 = time2 + 12

        if float(participant_psqi_df['psqi1ampm']) == 0 and (time1 == 12 or time1 == 12.5):
            time1 = time1 + 12
        if float(participant_psqi_df['psqi3ampm']) == 0 and (time2 == 12 or time2 == 12.5):
            time2 = time2 + 12

        # if float(participant_psqi_df['psqi1ampm']) == float(participant_psqi_df['psqi3ampm']):
        #    time_in_bed = time2 - time1
        # else:
        time_in_bed = 24 - time1 + time2
        if time_in_bed > 24:
            time_in_bed = time_in_bed - 24

        sleep_effieciency = sleep_duration / time_in_bed
        if sleep_effieciency >= 0.85:
            tmp_score = 0
        elif 0.75 <= sleep_effieciency < 0.85:
            tmp_score = 1
        elif 0.65 <= sleep_effieciency < 0.75:
            tmp_score = 2
        else:
            tmp_score = 3

        psqi_df.loc[uid, 'psqi_sleep_efficiency'] = tmp_score

        # Component 5
        sleep_disturbance = float(participant_psqi_df['psqi5b']) + float(participant_psqi_df['psqi5c'])
        sleep_disturbance += float(participant_psqi_df['psqi5d']) + float(participant_psqi_df['psqi5e'])
        sleep_disturbance += float(participant_psqi_df['psqi5f']) + float(participant_psqi_df['psqi5g'])
        sleep_disturbance += float(participant_psqi_df['psqi5h']) + float(participant_psqi_df['psqi5i'])
        if str(participant_psqi_df['psqi5jb']) != 'nan':
            sleep_disturbance = float(participant_psqi_df['psqi5jb']) + sleep_disturbance

        if sleep_disturbance < 1:
            tmp_score = 0
        elif 1 <= sleep_disturbance <= 9:
            tmp_score = 1
        elif 9 < sleep_disturbance <= 18:
            tmp_score = 2
        else:
            tmp_score = 3

        psqi_df.loc[uid, 'psqi_sleep_disturbance'] = tmp_score

        # Component 6
        psqi_df.loc[uid, 'psqi_sleep_medication'] = int(participant_psqi_df['psqi6'])

        # Component 7
        # tmp_score = float(participant_psqi_df['psqi8']) + float(participant_psqi_df['psqi9']) - 1
        tmp_score = float(participant_psqi_df['psqi7']) + float(participant_psqi_df['psqi8'])
        component7_dict = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3}
        psqi_df.loc[uid, 'psqi_day_dysfunction'] = component7_dict[tmp_score]

    if Path.exists(Path.joinpath(Path.resolve(data_directory).parent, 'processed')) is False:
        Path.mkdir(Path.joinpath(Path.resolve(data_directory).parent, 'processed'))
    if Path.exists(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'survey')) is False:
        Path.mkdir(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'survey'))

    # psqi_df.to_csv(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'survey', 'psqi_raw.csv.gz'), compression='gzip')

    return psqi_df


# Load mgt data
def read_MGT(data_directory):
    anxiety_mgt_df = pd.read_csv(os.path.join(data_directory, 'surveys', 'scored', 'EMAs', 'anxiety.csv.gz'), index_col=3)
    stress_mgt_df = pd.read_csv(os.path.join(data_directory, 'surveys', 'scored', 'EMAs', 'stressd.csv.gz'), index_col=3)
    pand_mgt_df = pd.read_csv(os.path.join(data_directory, 'surveys', 'scored', 'EMAs', 'pand.csv.gz'), index_col=3)

    return anxiety_mgt_df, stress_mgt_df, pand_mgt_df


# Load days at work data
def read_days_at_work(data_directory):
    days_at_work_df = pd.read_csv(os.path.join(data_directory, 'metadata', 'days-at-work', 'merged_days_at_work.csv.gz'), index_col=0)
    days_at_work_df = days_at_work_df.iloc[1:, :]
    return days_at_work_df


# Return igtb of nurses only
def return_nurse_df(igtb_df):
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
    return nurse_df