from math import sqrt
from pandas import read_excel
import pandas as pd


def normalize(data_frame, type):
    if type == "standaryzacja":
        return standardize(data_frame)
    elif type == "unitaryzacja":
        return unitarize(data_frame)
    else:
        print "Nie znam typu"


def standardize(data_frame):
    return (data_frame - data_frame.mean()) / (data_frame.std())


def unitarize(data_frame):
    return (data_frame - data_frame.min()) / (data_frame.max() - data_frame.min())


def change_character(data_frame, description):
    for col in data_frame.columns:
        if description[col][2] == 'd':
            data_frame[col] = 1 / data_frame[col]
    return data_frame


def apply_weights(data_frame, description):
    for col in data_frame.columns:
        data_frame[col] *= float(description[col][3])
    return data_frame


def add_summary_max_row(data_frame):
    return pd.concat([data_frame, pd.DataFrame(data_frame.max(axis=0), columns=['Max']).T])


def dzero(data_frame):
    table = []
    for i in range(0, len(data_frame) - 1):
        s = 0
        for col in data_frame.columns:
            s += (data_frame[col][i] - data_frame[col][-1]) ** 2
        table.append(sqrt(s))
    data_frame = data_frame.drop('Max', axis=0)
    data_frame['dzero'] = table
    return data_frame


def run_measurer(df, des):
    col_list = ['M1', 'Z1', 'B1', 'S1', 'IT1', 'R1']
    zadaniowa = df[col_list]
    zadaniowa = change_character(zadaniowa, des)
    zadaniowa_std = normalize(zadaniowa, "standaryzacja")
    zadaniowa_std = apply_weights(zadaniowa_std, des)
    zadaniowa_std['srednia'] = zadaniowa_std.mean(axis=1)
    miernik = zadaniowa_std['srednia'].copy()
    miernik.sort(['srednia'], ascending=False)
    print(miernik)
    return miernik


def run_helwig(df, des, what_kind):
    df = change_character(df, des)
    df_std = dzero(add_summary_max_row(normalize(df, what_kind)))
    m = df_std['dzero'].mean()
    standard_dev = df_std['dzero'].std()
    ar = []
    
    for i in range(0, len(df_std['dzero'])):
        z = 1 - (df_std['dzero'][i]) / (m + 2 * standard_dev)
        ar.append(z)
    df_std['miernik'] = ar
    miernik = df_std['miernik'].copy()
    miernik.sort(['miernik'], ascending=False)
    print(miernik)
    return miernik


if __name__ == "__main__":
    framka = read_excel('C:/Users/Tomasz Hinc/Desktop/DaneHelwig.xlsx', sheetname='Dane')
    opisy = read_excel('C:/Users/Tomasz Hinc/Desktop/DaneHelwig.xlsx', sheetname='OpisZmiennych')
    run_helwig(framka, opisy, "unitaryzacja")
