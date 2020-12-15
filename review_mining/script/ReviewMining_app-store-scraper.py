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


app_id = config['app_id']['uber_apple']
country_code = config['country_code']
csv_file_name = app_id + '_' + country_code + '_apple_appstore_review.csv'


appstore = AppStore(country=country_code, app_name=app_id)
appstore.review(how_many=100000)


df = pd.json_normalize(appstore.reviews)


df.to_csv(csv_file_name)

