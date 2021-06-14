#!/usr/bin/env python
# coding: utf-8

from langdetect import detect, detect_langs
from utils import *

from utils import *

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')


df2 = read_csv_from_gdrive(config['csv_input']['bolt_apple'])
total_reviews = len(df2)
unique_users  = len(df2['userName'].unique())
mean = df2['rating'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


df_test = df2.head()
df_test


rowsToRemove = []


rowsToRemove.append(0)
rowsToRemove


rowsToRemove.append(1)
rowsToRemove


rowsToRemove.append(3)
rowsToRemove


len(rowsToRemove)


# df_test.drop([0, 1, 3])
df_test.drop(rowsToRemove)




