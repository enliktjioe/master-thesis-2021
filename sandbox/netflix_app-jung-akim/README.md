### Background
Amazon Appstore for Android opened on 3/22/2011 and was made available in nearly 200 countries. Developers are paid 70% of the list price of the app or in-app purchase.
### The goal of this project
To help developers find the needs of the customers and better adjust their direction of quality assurance, add/remove the functionalities, and debug promptly to maintain/increase customers. 
### What is done in this project?
The dataset is preprocessed into lemmatized corpus and the topics are modelled using LDA or other methods where the models are tuned based on coherence scores. Each topic will be assigned a human-interpretable label that can deliver information to developers. The topics can be interpreted using the keywords, their prevalence or weights, the reviews that are most representative within each topic, and the wordclouds.<br>
BERT is trained with these topic labels and it is compared with LDA topic models to see how their classifications are different. The comparison is based on the 2d-plots where representative embeddings are projected and the topic distributions of reviews that have different classification results.
### Dataset
The dataset is from "Amazon Customer Reviews Dataset" that are publicly available in S3 bucket in AWS US East Region. The dataset used for this project is the subset of "amazon_reviews_us_Mobile_Apps_v1_00.tsv" file which contains information of each review on different apps. Only the subset of the data is used for this project and the app used for this project is **"Netflix"** which has one of the most reviews between 2010-11-04 and 2015-08-31. 
A (shuffled) half of the reviews are used for the project and the other half is retained as hold-out set for future use. There are *12,566* reviews used for topic modeling in this project.
### Tools
gensim, spacy, NLTK for preprocessing<br>
gensim, pyLDAvis for LDA, NMF, LSA<br>
ktrain, transformers, bert_embedding for BERT<br>
PIL, wordcloud, sklearn, umap, gensim for visualization<br>
Jupyter lab for modeling<br>
PyCharm for Flask
### Notebooks
1. [grid_search.ipynb](grid_search.ipynb)<br>
Contains the coherence scores in each combination of 'Number of Topics' and $\alpha$ in heatmaps to help select the best model.
2. [LDA_netflix.ipynb](LDA_netflix.ipynb)<br>
Interprets each LDA model with the tuned hyperparameters.
3. [NMF_LSA_topic_modeling.ipynb](NMF_LSA_netflix.ipynb)<br>
Interprets NMF and LSA models with the tuned hyperparameters.
3. [LDA_topic_labelling.ipynb](LDA_topic_labelling.ipynb)<br>
Labels each topic in an interpretable way.
4. [LDA_classification.ipynb](LDA_classification.ipynb)<br>
Predicts topics with unseen data(hold-out data)
5. [BERT.ipynb](BERT.ipynb)<br>
Predicts topics with unseen data using BERT

### Directories
1. Datasets<br>
[raw_data](raw_data), [preprocessed_data](preprocessed_data)
2. Predictions<br>
[prediction](prediction)
3. pyLDAvis Visualization<br>
[mallet_lda_vis](mallet_lda_vis), [std_lda_vis](std_lda_vis)
4. Models<br>
[bert_model](bert_model), [lda_mallet_model](lda_mallet_model)
5. Coherence scores from grid search<br>
[coherence_scores](coherence_scores)
6. Images<br>
[images](images)

### Python scripts
1. [utils.py](utils.py)<br>
Inlcudes NLPpipe class for pipelining and helper functions for interpretation
2. [predictor_api.py](predictor_api.py), [predictor_app.py](predictor_app.py), [templates/predictor.py](predictor.py) are for Flask app. Accredited to [link](https://github.com/thisismetis/sf20_ds19/tree/master/curriculum/project-03/flask-web-apps)

### Resources
#### Dataset
- Amazon Customer Reviews Dataset, URL: https://s3.amazonaws.com/amazon-reviews-pds/readme.html

#### Python Packages
##### gensim
Radim Rehurek and Petr Sojka, Software Framework for Topic Modelling with Large Corpora, *Proceedings of the LREC 2010 Workshop on New Challenges for NLP Frameworks*, 45--50, 2010, May 22, ELRA, Valletta, Malta, URL: http://is.muni.cz/publication/884893/en

##### spacy
Honnibal, M., & Montani, I. (2017). spaCy 2: *Natural language understanding with Bloom embeddings, convolutional neural networks and incremental parsing.*

##### pyLDAvis
Sievert, Shirley, LDAvis: A method for visualizing and interpreting topics, 2014, https://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf

##### BERT
Devlin, Jacob, et al. “Bert: Pre-training of deep bidirectional transformers for language understanding.” arXiv preprint arXiv:1810.04805 (2018).

##### bert_embedding
License: Apache Software License (ALv2)

##### ktrain
ktrain: A Low-Code Library for Augmented Machine Learning, Arun S. Maiya, 2020, arXiv:2004.10703 [cs.LG]

##### PIL
https://pillow.readthedocs.io/en/stable/
Copyright © 1997-2011 by Secret Labs AB
Copyright © 1995-2011 by Fredrik Lundh

##### wordcloud
https://pypi.org/project/wordcloud/

##### nltk
Bird, Steven, Edward Loper and Ewan Klein (2009).
Natural Language Processing with Python.  O'Reilly Media Inc.

##### umap
https://umap-learn.readthedocs.io/en/latest/

##### adjustText
https://github.com/Phlya/adjustText

##### pandas
Wes McKinney. Data Structures for Statistical Computing in Python, Proceedings of the 9th Python in Science Conference, 51-56 (2010)

##### numpy
* Travis E. Oliphant. A guide to NumPy, USA: Trelgol Publishing, (2006).
* Stéfan van der Walt, S. Chris Colbert and Gaël Varoquaux. The NumPy Array: A Structure for Efficient Numerical Computation, Computing in Science & Engineering, 13, 22-30 (2011), DOI:10.1109/MCSE.2011.37

##### sklearn
Fabian Pedregosa, Gaël Varoquaux, Alexandre Gramfort, Vincent Michel, Bertrand Thirion, Olivier Grisel, Mathieu Blondel, Peter Prettenhofer, Ron Weiss, Vincent Dubourg, Jake Vanderplas, Alexandre Passos, David Cournapeau, Matthieu Brucher, Matthieu Perrot, Édouard Duchesnay. Scikit-learn: Machine Learning in Python, Journal of Machine Learning Research, 12, 2825-2830 (2011)

##### matplotlib
John D. Hunter. Matplotlib: A 2D Graphics Environment, Computing in Science & Engineering, 9, 90-95 (2007), DOI:10.1109/MCSE.2007.55

##### seaborn
Waskom, M., Botvinnik, Olga, O&#39;Kane, Drew, Hobson, Paul, Lukauskas, Saulius, Gemperline, David C, … Qalieh, Adel. (2017). mwaskom/seaborn: v0.8.1 (September 2017). Zenodo. https://doi.org/10.5281/zenodo.883859

##### ipython
Fernando Pérez and Brian E. Granger. IPython: A System for Interactive Scientific Computing, Computing in Science & Engineering, 9, 21-29 (2007), DOI:10.1109/MCSE.2007.53

##### Pycharm
JetBrains, 2017. Pycharm. [online] JetBrains. Available at: <https://www.jetbrains.com/pycharm/> [Accessed 11 April 2017].

#### References
- Topic Modeling with Gensim (Python) by Selva Prabhakaran, URL: https://www.machinelearningplus.com/nlp/topic-modeling-gensim-python/#11createthedictionaryandcorpusneededfortopicmodeling
- Topic modeling visualization – How to present the results of LDA models? by Selva Prabhakaran, URL: https://www.machinelearningplus.com/nlp/topic-modeling-visualization-how-to-present-results-lda-models/
- Your Guide to Latent Dirichlet Allocation, Lettier, Feb 23, 2018, URL: https://medium.com/@lettier/how-does-lda-work-ill-explain-using-emoji-108abf40fa7d
- Topic Coherence To Evaluate Topic Models, URL: http://qpleple.com/topic-coherence-to-evaluate-topic-models/
- Visualising topics as distributions over words, URL: http://bl.ocks.org/AlessandraSozzi/raw/ce1ace56e4aed6f2d614ae2243aab5a5/#topic=0&lambda=1&term=
- Wordcloud, URL: https://github.com/amueller/word_cloud
- BERT, URL: https://github.com/amaiya/ktrain/blob/master/examples/text/20newsgroups-BERT.ipynb
- LDA, URL: https://radimrehurek.com/gensim/models/wrappers/ldamallet.html