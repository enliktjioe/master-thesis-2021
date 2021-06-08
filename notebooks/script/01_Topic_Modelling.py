#!/usr/bin/env python
# coding: utf-8

from utils import * 

import numpy as np
import pandas as pd
from pprint import pprint
import os
import matplotlib.pyplot as plt
from collections import defaultdict

# Gensim
from gensim.test.utils import datapath
from gensim.test.utils import common_texts, get_tmpfile

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.option_context('display.max_colwidth', 500);

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)


config = get_config('config.yaml')


# Import dataset
# df = pd.read_pickle('raw_data/netflix.pkl')
df = read_csv_from_gdrive(config['csv_input']['uber_google'])
reviews = df.content


term_doc = pd.read_pickle('preprocessed_data/term_doc.pkl')
data_lemmatized = pd.read_pickle('preprocessed_data/data_lemmatized.pkl')
dictionary = pd.read_pickle('preprocessed_data/dictionary.pkl')
tf_idf = pd.read_pickle('preprocessed_data/tf_idf.pkl')


lda_model = gensim.models.ldamodel.LdaModel(corpus=term_doc,
                                           id2word=dictionary,
                                           num_topics= 6, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=2000,
                                           passes=10,
                                           alpha= 1.5,
                                           per_word_topics=True)


vis_data = pyLDAvis.gensim.prepare(lda_model, term_doc, dictionary, sort_topics=False)
pyLDAvis.save_html(vis_data, 'std_lda_vis/std_lda_topics=6&a=1.5&batchsize=1.html')


lda_model_100 = gensim.models.ldamodel.LdaModel(corpus=term_doc,
                                           id2word=dictionary,
                                           num_topics= 15, 
                                           random_state=100,
                                           update_every=100,
                                           chunksize=2000,
                                           passes=10,
                                           alpha= 1.5,
                                           per_word_topics=True)

vis_data = pyLDAvis.gensim.prepare(lda_model_100, term_doc, dictionary, sort_topics=False)
pyLDAvis.save_html(vis_data, 'std_lda_vis/std_lda_topics=15&a=1.5&batchsize=100.html')


coherence_model = CoherenceModel(model=lda_model_100, texts=data_lemmatized, dictionary=dictionary, coherence='c_npmi')
np.mean(coherence_model.get_coherence_per_topic())




