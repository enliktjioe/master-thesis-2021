#!/usr/bin/env python
# coding: utf-8

# Reference: https://github.com/cowboy-bebug/app-store-scraper

# !pip install app-store-scraper


import pandas as pd
import yaml
from app_store_scraper import AppStore
from pprint import pprint


# ## Setup Input (App ID and country) and Output (CSV file name)

config_file = open('config.yaml')
config = yaml.load(config_file, Loader=yaml.FullLoader)


# app_id = config['app_id']['uber_apple']
list_of_app_id = [
#     config['app_id']['bolt_apple'],
    config['app_id']['uber_apple'],
    config['app_id']['blablacar_apple'],
    config['app_id']['cabify_apple'],
    config['app_id']['via_apple'],
    config['app_id']['getaround_apple'],
    config['app_id']['olacabs_apple'],
    config['app_id']['taxieu_apple'],
    config['app_id']['freenow_apple'],
    config['app_id']['yandexgo_apple']
]
    
list_of_country_code = config['country_code']
output_path = config['output_path']


for app_id in list_of_app_id:
    df_merged = None
    
    for country_code in list_of_country_code:
        appstore = AppStore(country=country_code, app_name=app_id)
        appstore.review(how_many=100000)

        if df_merged is not None:
            df = pd.json_normalize(appstore.reviews)
            df_merged = df_merged.append(df)
        else:
            df_merged = pd.json_normalize(appstore.reviews)


        csv_file_name = app_id + '_apple_appstore_review.csv'

    df_merged.to_csv(output_path + csv_file_name)

