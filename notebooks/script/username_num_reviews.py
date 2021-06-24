#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import re


def get_df_and_length(csvInput, columnToUsed):
    url='https://drive.google.com/uc?id=' + csvInput.split('/')[-2]
    df = pd.read_csv(url, usecols=columnToUsed)

    # preprocessing csv input 


    # decode all emoji characters
    # https://stackoverflow.com/a/57514515/2670476
    df = df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

    # Replace all non-letters with space
    df.content = df.apply(lambda row: " ".join(re.sub("[^a-zA-Z]+", " ", row.content).split()), 1)

    # remove all review with total characters less than 20 (such as only emoji)
    df = df[df.content.str.len()>=20]

#     df = df[0:200]

    length = len(df)
    return df, length


CSV_INPUT = 'https://drive.google.com/file/d/1qWuyf3UrpaU5xnxLmO3GMFa6zybSFYQh/view?usp=sharing'
USE_COLS = ['userName', 'content', 'score']
df, length = get_df_and_length(csvInput = CSV_INPUT, columnToUsed = USE_COLS)
print('length = ' + str(length))
print('\n')


df


df['score'] = df['score'].astype(int)


df_agg = df['score'].mean()
df_agg


df_agg = df.groupby(['userName']).size().reset_index(name='counts')
df_agg


df_agg[df_agg['counts']>2]


df_agg['userName'].to_list()




