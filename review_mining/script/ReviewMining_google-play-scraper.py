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


list_of_app_id = [
#     config['app_id']['bolt_google'],
    config['app_id']['uber_google'],
#     config['app_id']['blablacar_google'],
    config['app_id']['cabify_google'],
    config['app_id']['via_google'],
    config['app_id']['getaround_google'],
    config['app_id']['olacabs_google'],
    config['app_id']['taxieu_google'],
#     config['app_id']['freenow_google'],
#     config['app_id']['yandexgo_google']
]

output_path = config['output_path']


# ## App Reviews

for app_id in list_of_app_id:
    result = reviews_all(
        app_id,
        lang='en', # defaults to 'en'
        country='us', # defaults to 'us'
        sort=Sort.MOST_RELEVANT, # defaults to Sort.MOST_RELEVANT
        filter_score_with=None # defaults to None(means all score)
    )
    df = pd.json_normalize(result)
    
    csv_file_name = app_id + '_google_playstore_review.csv'
    df.to_csv(output_path + csv_file_name)

