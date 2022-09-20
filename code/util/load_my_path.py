import os
import numpy as np
import pandas as pd

path_to_development = "/Users/brinkley97/Documents/development/"

def load_gzip_csv_data(path_to_files, name_of_file):
    dataset = path_to_development + path_to_files + name_of_file 
    original_data = pd.read_csv(dataset, compression='gzip')
    copy_of_data = original_data.copy()
    
    return copy_of_data
