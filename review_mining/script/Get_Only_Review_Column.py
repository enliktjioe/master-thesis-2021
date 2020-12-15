#!/usr/bin/env python
# coding: utf-8

# for macOS 10.12.6 issue - urllib and “SSL: CERTIFICATE_VERIFY_FAILED” Error
# solution: https://stackoverflow.com/a/28052583/2670476
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import pandas as pd
import yaml


config_file = open('config.yaml')
config = yaml.load(config_file, Loader=yaml.FullLoader)


# review_colname = 'content'
review_colname = config['review_colname']

df = pd.read_csv('csv_output/3_blablacar/blablacar-carpooling-and-bus_de_apple_appstore_review.csv', usecols=review_colname)
df


df.to_excel('xls_output/test.xlsx')





df = pd.read_excel('xls_output/test_en_translation.xlsx')


df




