#!/usr/bin/env python
# coding: utf-8

from utils import *

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')

from sentistrength import PySentiStr
senti = PySentiStr()
senti.setSentiStrengthPath('/Users/enlik/GitRepo/master-thesis-2021/references/SentiStrengthCom.jar') # Note: Provide absolute path instead of relative path
senti.setSentiStrengthLanguageFolderPath('/Users/enlik/GitRepo/master-thesis-2021/references/SentiStrengthData/') # Note: Provide absolute path instead of relative path


# # Sample use case of SentiStrength

result = senti.getSentiment('What a bad day')
print(result)


str_arr = ['What a lovely day', 'What a bad day']
result = senti.getSentiment(str_arr, score='scale')
print(result)


str_arr = ['What a lovely day', 'What a bad day']
result = senti.getSentiment(str_arr, score='dual')
print(result)


str_arr = ['What a lovely day', 'What a bad day']
result = senti.getSentiment(str_arr, score='binary')
print(result)


str_arr = ['What a lovely day', 'What a bad day']
result = senti.getSentiment(str_arr, score='trinary')
print(result)


# # Test with Bolt Apple

df2 = read_csv_from_gdrive(config['csv_input']['bolt_apple'])
total_reviews = len(df2)
unique_users  = len(df2['userName'].unique())
mean = df2['rating'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


df2


df2.review = df2.review.astype(str)
df2 = df2.reset_index(drop=True)
df2.review


df2.review[1]


for i in range(0, int(len(df2) / 100)):
    text_input = df2.review[i]
    star_rating = df2.rating[i]
    result = senti.getSentiment(text_input)
    
    print(text_input)
    print(result)
    print(star_rating)
    print('\n')




