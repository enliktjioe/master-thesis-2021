#!/usr/bin/env python
# coding: utf-8

# # References

# # Modified from KEFE's preprocess_review.py

get_ipython().system('python --version')
get_ipython().system('pwd')


from utils import *
from pprint import pprint

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')


# # Let's Get Started

# ## Bolt (Both Apple App Store and Google Play Store

df = read_csv_from_gdrive(config['csv_input']['bolt_google'])
total_reviews = len(df)
unique_users  = len(df['userName'].unique())
unknown_users = len(df[df['userName']=='A Google user'])
mean = df['score'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total unknown users: {unknown_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users - unknown_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


df2 = read_csv_from_gdrive(config['csv_input']['bolt_apple'])
total_reviews = len(df2)
unique_users  = len(df2['userName'].unique())
mean = df2['rating'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


# merge both apple and google
google = df.content.astype(str)
apple = df2.review.astype(str)
df_merged = google.append(apple, ignore_index=True)
total_reviews = len(df_merged)

print(f'Total English reviews: {total_reviews} \n')


cleaned_docs = remove_things(df_merged)


lists_of_words = list(sentences_to_words(cleaned_docs))
lists_of_words_no_stops = remove_stopwords(lists_of_words)


ngrams = make_bigrams(lists_of_words_no_stops)


data_lemmatized = lemmatize(ngrams, allowed_postags=['NOUN'])


corpora.Dictionary(data_lemmatized)


# Create Dictionary
id2word = corpora.Dictionary(data_lemmatized)

# Create Corpus
texts = data_lemmatized

# Term Document Frequency
term_doc = [id2word.doc2bow(text) for text in texts]

# View
print(term_doc[:1])


id2word[0]


[[(id2word[id], freq) for id, freq in cp] for cp in term_doc[:1]]


tf_idf = models.TfidfModel(term_doc, smartirs='ntc')[term_doc]
tf_idf[0]


[[(id2word[id], freq) for id, freq in cp] for cp in tf_idf[:1]]


# # Save pre-processed data into binary Pickle file

import pickle

output_path = 'preprocessed_data/bolt/'


# ## data_lemmatized

with open(output_path + 'data_lemmatized.pkl', 'wb') as f:
    pickle.dump(data_lemmatized, f)


df = pd.read_pickle('preprocessed_data/data_lemmatized.pkl')
df


# ## dictionary

with open(output_path + 'dictionary.pkl', 'wb') as f:
    pickle.dump(id2word, f)


import pandas as pd
id2word = pd.read_pickle(output_path + 'dictionary.pkl')

[[(id2word[id], freq) for id, freq in cp] for cp in term_doc[:3]]


# ## term_doc

with open(output_path + 'term_doc.pkl', 'wb') as f:
    pickle.dump(term_doc, f)


import pandas as pd
term_doc = pd.read_pickle(output_path + 'term_doc.pkl')
term_doc


# ## tf_idf

with open(output_path + 'tf_idf.pkl', 'wb') as f:
    pickle.dump(tf_idf, f)


import pandas as pd
tf_idf = pd.read_pickle(output_path + 'tf_idf.pkl')
tf_idf


[[(id2word[id], freq) for id, freq in cp] for cp in tf_idf[:1]]


# ## Save DF Merged

df_merged.to_csv(output_path + 'bolt_apple_google.csv')




