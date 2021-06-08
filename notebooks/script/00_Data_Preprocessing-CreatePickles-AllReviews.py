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

# ## Combine All Reviews

# ### Read from Local Machine

df_merged = pd.Series()


for i in config['csv_input_local']:
    if 'apple' in i:
        print('apple')
        df = pd.read_csv(config['csv_input_local'][i], index_col=0)
        new = df.review.astype(str)
        total_reviews = len(new)
        print(f'Total {i} reviews: {total_reviews} \n')
    elif 'google' in i:
        print('google')
        df = pd.read_csv(config['csv_input_local'][i], index_col=0)
        new = df.content.astype(str)
        total_reviews = len(new)
        print(f'Total {i} reviews: {total_reviews} \n')
    else:
        print("Oops!  That was no valid input.  Try again...")
        
    df_merged = df_merged.append(new, ignore_index=True)


# ### Read from Google Drive
# 
# - Google Drive has limitation after multiple access in short time that cause **HTTPError: HTTP Error 403: Forbidden**

# for i in config['csv_input']:
#     if 'apple' in i:
#         print('apple')
#         df = read_csv_from_gdrive(config['csv_input'][i])
#         new = df.review.astype(str)
#         total_reviews = len(df_merged)
#         print(f'Total English reviews: {total_reviews} \n')
#     elif 'google' in i:
#         print('google')
#         df = read_csv_from_gdrive(config['csv_input'][i])
#         new = df.content.astype(str)
#     else:
#         print("Oops!  That was no valid input.  Try again...")
        
#     df_merged = df_merged.append(new, ignore_index=True)


df_merged


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

output_path = 'preprocessed_data/all/'


# ## data_lemmatized

with open(output_path + 'data_lemmatized.pkl', 'wb') as f:
    pickle.dump(data_lemmatized, f)


df = pd.read_pickle('preprocessed_data/data_lemmatized.pkl')
df


# ## dictionary

with open(output_path + 'dictionary.pkl', 'wb') as f:
    pickle.dump(id2word, f)


# ## term_doc

with open(output_path + 'term_doc.pkl', 'wb') as f:
    pickle.dump(term_doc, f)


# ## tf_idf

with open(output_path + 'tf_idf.pkl', 'wb') as f:
    pickle.dump(tf_idf, f)


# ## Save df_merged into CSV file

df_merged.to_csv(output_path + 'all_10_apps.csv')




