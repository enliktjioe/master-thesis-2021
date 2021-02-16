#!/usr/bin/env python
# coding: utf-8

# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/enliktjioe/master-thesis-2021/blob/main/notebooks/safe_feature_extraction.ipynb)

# # Preparation
# 
# - wget http://nlp.stanford.edu/software/stanford-postagger-full-2016-10-31.zip
# - put in `references/re_2017_johann_et-al` (private files, licensed by the author)
# - Update in `FE_Safe.py` variable `path_to_model` and `path_to_jar` with absolute path to its directory
# 
#  
# **Required libraries**:
# ```
# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
# ```

# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')

import nltk
nltk.download('wordnet')


# Python path referencing
import os
import sys

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path+"/references/re_2017_johann_et-al")
    
import FE_SAFE as fs
# print(sys.path)


# ## [Test] Manual Copy Paste Review 

# %%time


# example_review = """
#         I love bolt. I don’t use uber often because one ride even if it’s short is like £11. Whereas from my high street to my house is £3. Not only that but their drivers are SUPER friendly! I was sick one day (my first time using bolt) and the driver was so understanding and encouraged me throughout my journey. Bolt is 100% recommended by me. I don’t write reviews so that’s how you know I defiantly recommend it. My Instagram name is: TeeKezi if you wish to get in contact with me about bolt. I’m not an ambassador 😂 or anything like that. Just super happy with the service I have been receiving x,5,Love it
#     """

# #     feature_extractor = SAFE()
# feature_extractor = fs.SAFE()
# feature_extractor.extract_from_review(example_review)


# ## Data Pre-Processing

import pandas as pd


bolt_path = "../review_mining/csv_output/1_bolt/bolt_google_playstore_review.csv"
uber_path = "../review_mining/csv_output/2_uber/uber_google_playstore_review.csv"
blablacar_path = "../review_mining/csv_output/3_blablacar/blablacar_google_playstore_review.csv"
cabify_path = "../review_mining/csv_output/4_cabify/cabify_google_playstore_review.csv"
via_path = "../review_mining/csv_output/5_via/via_google_playstore_review.csv"

getaround_path = "../review_mining/csv_output/6_getaround/getaround_google_playstore_review.csv"
ola_path = "../review_mining/csv_output/7_olacabs/olacabs_google_playstore_review.csv"
taxieu_path = "../review_mining/csv_output/8_taxieu/taxieu_google_playstore_review.csv"
freenow_path = "../review_mining/csv_output/9_freenow/freenow_google_playstore_review.csv"
yandexgo_path = "../review_mining/csv_output/10_yandexgo/yandexgo_google_playstore_review.csv"

review_col = [4] # column that contains review text
number_of_rows = 100 # for testing, only used the first 100 rows of csv file


review_bolt = pd.read_csv(bolt_path, usecols=review_col, nrows = number_of_rows)
review_bolt = review_bolt.content.str.cat(sep='; ') # source = https://stackoverflow.com/a/33280080/2670476

review_uber = pd.read_csv(uber_path, usecols=review_col, nrows = number_of_rows)
review_uber = review_uber.content.str.cat(sep='; ') 

review_blablacar = pd.read_csv(blablacar_path, usecols=review_col, nrows = number_of_rows)
review_blablacar = review_blablacar.content.str.cat(sep='; ') 

review_cabify = pd.read_csv(cabify_path, usecols=review_col, nrows = number_of_rows)
review_cabify = review_cabify.content.str.cat(sep='; ') 

review_via = pd.read_csv(via_path, usecols=review_col, nrows = number_of_rows)
review_via = review_via.content.str.cat(sep='; ')

review_getaround = pd.read_csv(getaround_path, usecols=review_col, nrows = number_of_rows)
review_getaround = review_getaround.content.str.cat(sep='; ')

review_ola = pd.read_csv(ola_path, usecols=review_col, nrows = number_of_rows)
review_ola = review_ola.content.str.cat(sep='; ') 

review_taxieu = pd.read_csv(taxieu_path, usecols=review_col, nrows = number_of_rows)
review_taxieu = review_taxieu.content.str.cat(sep='; ') 

review_freenow = pd.read_csv(freenow_path, usecols=review_col, nrows = number_of_rows)
review_freenow = review_freenow.content.str.cat(sep='; ') 

review_yandexgo = pd.read_csv(yandexgo_path, usecols=review_col, nrows = number_of_rows)
review_yandexgo = review_yandexgo.content.str.cat(sep='; ')


review_yandexgo


# # Google Play Store Reviews

# ## Bolt

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_bolt)')


# ## Uber

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_uber)')


# ## Blablacar

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_blablacar)')


# ## Cabify

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_cabify)')


# ## Via

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_via)')


# ## Getaround

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_getaround)')


# ## Ola

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_ola)')


# ## Taxi.eu

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_taxieu)')


# ## Free Now

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_freenow)')


# ## Yandex Go

get_ipython().run_cell_magic('time', '', '\nfeature_extractor = fs.SAFE()\nfeature_extractor.extract_from_review(review_yandexgo)')




