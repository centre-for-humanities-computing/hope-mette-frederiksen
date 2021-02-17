"""
Join the 00-10 files into one file
"""

import glob
import pandas as pd

### Define Functions ###

def get_df(filenames):
    df = pd.read_csv(filenames[0], header=None)

    for file in filenames[1:]:
        df_0 = pd.read_csv(file, header = None)
        df = df.append(df_0)

    df = df.drop_duplicates()

    return df

def clean_dates(df):
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

## Run these functions
if __name__ == "__main__":
    #filenames = glob.glob("../data/statsmin_file*.csv")
    filenames = glob.glob("../data/MF*.csv")

    #filename = "../data/statsmin_data.csv"
    filename = "../data/MF_data.csv"
    print("Get data")
    df = get_df(filenames)
    #print("Start cleaning dates")
    #df = clean_dates(df)
    print("Save file")
    df.to_csv(filename, index=False)
    del df
    