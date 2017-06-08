# coding: utf-8

import os
import pandas as pd
from datetime import datetime
from timer import date_to_date, time_to_delta


def get_data(period, path, cont_mark=False, sort=True, time_conversion=True, save_file=False):
    # Load data from files
    dfs = []
    for p in period:
        n_log = 0
        print("Loading files from period %s" % p)
        files = os.listdir(path % p)
        for file in files:
            temp_df = pd.read_csv(os.path.join(path % p, file), delimiter='^', dtype='str', encoding='euc-kr', header=None)
            temp_df['기간'] = p
            n_log += temp_df.shape[0]
            dfs.append(temp_df)
        print("    %s files : %s" % (len(files), n_log))

    # Set columns for data frame
    cols = "일자	패널가구ID  개인ID    가중치 성별  연령  직업  학력  소득  채널  시청시작시간  시청종료시간  프로그램시청시간    프로그램명   프로그램편성시작시간  프로그램편성종료시간  프로그램장르 기간"
    cols = cols.split()
    raw_df = pd.concat(dfs, ignore_index=True)
    raw_df.columns = cols

    # Replace channel and genre code to string
    channel = pd.read_csv('channel.txt', delimiter='\t', header=0, dtype='str')
    genre = pd.read_csv('genre.txt', delimiter='\t', header=0, dtype='str')
    merged = pd.merge(raw_df, genre, how='left', on='프로그램장르')
    merged = pd.merge(merged, channel, how='left', on='채널')

    merged['ID'] = merged.패널가구ID + merged.개인ID

    sub_df = merged.ix[:, ['기간', '일자', 'ID', '성별', '연령', '직업', '학력', '소득', '가중치', '방송사', '시청시작시간', '시청종료시간', '프로그램시청시간', '프로그램명', '프로그램편성시작시간', '프로그램편성종료시간', '대분류']].dropna(axis=0)

    # Check if duplicated viewing and add as a column
    if cont_mark:
        sub_df['반복'] = sub_df.groupby(['일자', 'ID']).시청시작시간.apply(lambda t: (t == t.shift(1)) | (t == t.shift(-1)))

    # Sort rows
    if sort:
        tidy_df = sub_df.sort_values(['일자', 'ID', '시청시작시간'])
    else:
        tidy_df = sub_df.copy()

    tidy_df.방송사 = tidy_df.방송사.str.strip()
    tidy_df.일자 = tidy_df.일자.astype('str')
    weekday_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    tidy_df['요일'] = tidy_df.일자.apply(date_to_date).apply(datetime.weekday).apply(lambda d: weekday_name[d])

    # Convert time related columns to datetime object
    if time_conversion:
        target_columns = ['시청시작시간', '시청종료시간', '프로그램편성시작시간', '프로그램편성종료시간']
        convert_time(tidy_df, target_columns)

    if save_file:
        tidy_df.to_pickle('output/tidy_data.pkl')

    return tidy_df

    # tidy_df['시청시간'] = tidy_df.loc[:, ['시청종료시간', '프로그램편성종료시간']].min(axis=1) - tidy_df.loc[:, ['시청시작시간', '프로그램편성시작시간']].max(axis=1) + timedelta(seconds=1)


def convert_time(dataframe, target_columns):
    cnv = lambda col: dataframe['일자'].apply(date_to_date) + dataframe[col].apply(time_to_delta)
    for col in target_columns:
        print('Converting String to Timestamp: %s' % col)
        dataframe[col] = cnv(col)
    # dataframe['시청시작시간'] = dataframe.일자.apply(date_to_date) + dataframe.시청시작시간.apply(time_to_delta)
    # dataframe['시청종료시간'] = dataframe.일자.apply(date_to_date) + dataframe.시청종료시간.apply(time_to_delta)
    # dataframe['프로그램편성시작시간'] = dataframe.일자.apply(date_to_date) + dataframe.프로그램편성시작시간.apply(time_to_delta)
    # dataframe['프로그램편성종료시간'] = dataframe.일자.apply(date_to_date) + dataframe.프로그램편성종료시간.apply(time_to_delta)


if __name__ == '__main__':
    timer_start = datetime.now()
    columns = ['시청종료시간', '시청시작시간', '프로그램편성시작시간', '프로그램편성종료시간']
    default_period = ['T2', 'T3', 'T4']
    default_path = 'nielsen_data_new_20170328/%s'
    dataframe = get_data(period=default_period, path=default_path)
    print(dataframe)
    timer_end = datetime.now()
    print(timer_end - timer_start)
