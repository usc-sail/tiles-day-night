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
    return sleep_metadata_df


# Load fitbit data
def read_fitbit_data(data_directory, id):
    if Path.exists(Path.joinpath(data_directory, 'fitbit', 'heart-rate', id + '.csv.gz')) is False:
        return None, None

    hr_df = pd.read_csv(Path.joinpath(data_directory, 'fitbit', 'heart-rate', id + '.csv.gz'), index_col=0)
    step_df = pd.read_csv(Path.joinpath(data_directory, 'fitbit', 'step-count', id + '.csv.gz'), index_col=0)

    return hr_df, step_df


# Load fitbit data
def read_prossed_fitbit_data(data_directory, id):
    if Path.exists(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'fitbit', id + '.csv.gz')) is False:
        return None
    fitbit_df = pd.read_csv(Path.joinpath(Path.resolve(data_directory).parent, 'processed', 'fitbit', id + '.csv.gz'), index_col=0)
    return fitbit_df