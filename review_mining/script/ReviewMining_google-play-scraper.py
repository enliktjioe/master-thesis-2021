#!/usr/bin/env python
# coding: utf-8

# Reference: https://github.com/JoMingyu/google-play-scraper

# ## Library Needed

# !pip install google-play-scraper


# for macOS 10.12.6 issue - urllib and “SSL: CERTIFICATE_VERIFY_FAILED” Error
# solution: https://stackoverflow.com/a/28052583/2670476
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import pandas as pd
import yaml
from google_play_scraper import Sort, reviews_all


# ## Setup Input (App ID and country) and Output (CSV file name)

config_file = open('config.yaml')
config = yaml.load(config_file, Loader=yaml.FullLoader)


app_id = config['app_id']['yandexgo_google']
# country_code = config['country_code']
country_code = 'us'
csv_file_name = app_id + '_' + country_code + '_google_playstore_review.csv'

# country_code = []
# csv_file_name = []
# for i in config['country_code']:
#     country_code.append(i)
#     csv_file_name.append(app_id + '_' + country_code + '_google_playstore_review.csv')


# ## App Reviews

result = reviews_all(
    app_id,
    sleep_milliseconds=0, # defaults to 0
    lang='en', # defaults to 'en'
    country=country_code, # defaults to 'us'
    sort=Sort.MOST_RELEVANT, # defaults to Sort.MOST_RELEVANT
    filter_score_with=None # defaults to None(means all score)
)


df = pd.json_normalize(result)
# print(df)


df.to_csv(csv_file_name)

