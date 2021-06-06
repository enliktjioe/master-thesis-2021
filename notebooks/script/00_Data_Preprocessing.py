#!/usr/bin/env python
# coding: utf-8

# # References

# # Modified from KEFE's preprocess_review.py

get_ipython().system('python --version')
get_ipython().system('pwd')


from utils import *

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')


# # Let's Get Started

# ## Test

df = read_csv_from_gdrive(config['csv_input']['uber_google'])
total_reviews = len(df)
unique_users  = len(df['userName'].unique())
unknown_users = len(df[df['userName']=='A Google user'])
mean = df['score'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total unknown users: {unknown_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users - unknown_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


cleaned_docs = remove_things(df['content'])


lists_of_words = list(sentences_to_words(cleaned_docs))
lists_of_words_no_stops = remove_stopwords(lists_of_words)


ngrams = make_bigrams(lists_of_words_no_stops)


data_lemmatized = lemmatize(ngrams, allowed_postags=['NOUN'])
data_lemmatized


corpora.Dictionary(data_lemmatized)


# Create Dictionary
id2word = corpora.Dictionary(data_lemmatized)

# Create Corpus
texts = data_lemmatized

# Term Document Frequency
corpus = [id2word.doc2bow(text) for text in texts]

# View
print(corpus[:1])


id2word[0]




