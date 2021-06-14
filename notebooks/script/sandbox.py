#!/usr/bin/env python
# coding: utf-8

# # Removing Rows in Dataframe

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


# # Understanding Preprocessing

import re
import string

remove_digits_lower = lambda x: re.sub('\w*\d\w*', ' ', x.lower())
remove_punc = lambda x: re.sub('[%s]' % re.escape(string.punctuation), ' ', x)
remove_repeats = lambda x: re.sub(r'(.)\1+', r'\1\1', x)

# def remove_things(text):
#     """
#     Lowercase, remove punctuation, and remove repeats of more than 2.
#     """
#     remove_digits_lower = lambda x: re.sub('\w*\d\w*', ' ', x.lower())
#     remove_punc = lambda x: re.sub('[%s]' % re.escape(string.punctuation), ' ', x)
#     remove_repeats = lambda x: re.sub(r'(.)\1+', r'\1\1', x)
#     return text.map(remove_digits_lower).map(remove_punc).map(remove_repeats)


# input_text = """I’ve been using bolt for a month now. I had a few good journeys but 2 horrendous ones recently. 
#     The first occasion I was told to not cross my legs in the car because it “might” touch his chair. 
#     So apparently bolt encourages people to sit still and not move in the car, 
#     which was the response I got from customer service and no refund. The second time, 
#     I had a dental appointment and ordered a cab, the driver came and then he said where are you going? 
#     As soon as he found out what the location was, he got frustrated and swore and said “this is too far man I’m tired”. 
#     I asked why he had accepted it in the first place if he didn’t want to go too far. 
#     I didn’t get any proper explanation and no apology. I was in pain because of my dental extraction too. 
#     So I had to cancel from my end because he said he couldn’t do it. He said he would text bolt and let them know. 
#     And I messaged Bolt 3 days ago and still no reply. They have charged me £3 for this trip that didn’t happen. 
#     Terrible terrible drivers and very bad customer service. When incidents like this happened with Uber, 
#     they would always refund and apologise."""


# input_text


input_text = df2.review.reset_index(drop=True)
input_text


x = input_text[2]
x


re.sub('\w*\d\w*', ' ', x.lower())


re.sub('[%s]' % re.escape(string.punctuation), ' ', x)


y = "hhhappy birthhhhhhdayyyuuu"


re.sub(r'(.)\1+', r'\1\1', y)


# # Using SentiStrength

from sentistrength import PySentiStr
senti = PySentiStr()
senti.setSentiStrengthPath('/Users/enlik/GitRepo/master-thesis-2021/references/SentiStrengthCom.jar') # Note: Provide absolute path instead of relative path
senti.setSentiStrengthLanguageFolderPath('/Users/enlik/GitRepo/master-thesis-2021/references/SentiStrengthData/') # Note: Provide absolute path instead of relative path


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




