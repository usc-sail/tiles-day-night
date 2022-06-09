import os, errno
import pandas as pd
import numpy as np
from pathlib import Path

# date_time format
date_time_format = '%Y-%m-%dT%H:%M:%S.%f'
date_only_date_time_format = '%Y-%m-%d'


# Load sleep data
def read_sleep_data(data_directory, id):
    if Path.exists(Path.joinpath(data_directory, 'fitbit', 'sleep-metadata', id + '.csv.gz')) is False:
        return None

    sleep_metadata_df = pd.read_csv(Path.joinpath(data_directory, 'fitbit', 'sleep-metadata', id + '.csv.gz'))
    save_col = ['isMainSleep', 'startTime', 'endTime', 'dateOfSleep',
                'timeInBed', 'minutesAsleep', 'minutesAwake',
                'duration', 'efficiency', 'minutesAfterWakeup', 'minutesToFallAsleep']
    sleep_metadata_df = sleep_metadata_df[save_col]
    sleep_metadata_df = sleep_metadata_df.set_index('startTime')
    return sleep_metadata_df


# Load realizd data
def read_realizd_data(data_directory, id):
    if Path.exists(Path.joinpath(data_directory, 'realizd', id + '.csv.gz')) is False:
        return None

    realizd_df = pd.read_csv(Path.joinpath(data_directory, 'realizd', id + '.csv.gz'), index_col=1)
    realizd_df = realizd_df.sort_index()

    time_diff_list = list(pd.to_datetime(realizd_df['session_stop']) - pd.to_datetime(realizd_df.index))
    for i in range(len(realizd_df)):
        realizd_df.loc[realizd_df.index[i], 'duration'] = time_diff_list[i].total_seconds()
    return realizd_df


# Load fitbit data
def read_fitbit_data(data_directory, id):
    if Path.exists(Path.joinpath(data_directory, 'fitbit', 'heart-rate', id + '.csv.gz')) is False:
        return None, None

    hr_df = pd.read_csv(Path.joinpath(data_directory, 'fitbit', 'heart-rate', id + '.csv.gz'), index_col=0)
    step_df = pd.read_csv(Path.joinpath(data_directory, 'fitbit', 'step-count', id + '.csv.gz'), index_col=0)

    return hr_df, step_df


# Load fitbit data
def read_prossed_fitbit_data(data_directory, id):
    if Path.exists(Path.joinpath(Path.resolve(data_directory), 'processed', 'fitbit', id + '.csv.gz')) is False:
        return None
    fitbit_df = pd.read_csv(Path.joinpath(Path.resolve(data_directory), 'processed', 'fitbit', id + '.csv.gz'), index_col=0)
    return fitbit_df


# Load fitbit daily data
def read_fitbit_daily_data(data_directory, id):
    if Path.exists(Path.joinpath(data_directory, 'fitbit', 'daily-summary', id + '.csv.gz')) is False:
        return None
    summary_df = pd.read_csv(Path.joinpath(data_directory, 'fitbit', 'daily-summary', id + '.csv.gz'), index_col=0)
    return summary_df