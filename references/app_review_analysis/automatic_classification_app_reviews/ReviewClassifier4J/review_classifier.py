from __future__ import absolute_import
from __future__ import division

import collections
import csv
import io
import json
import random
import sys
from itertools import chain

import nltk
import pathlib
import time
from nltk.classify import NaiveBayesClassifier, MaxentClassifier, DecisionTreeClassifier
from textblob.classifiers import word_tokenize, strip_punc
from combinator import CLASSIFIER_TECHNIQUES

CUSTOM_STOPWORDS = ['i', 'me','up','my', 'myself', 'we', 'our', 'ours',
                    'ourselves', 'you', 'your', 'yours','yourself', 'yourselves',
                    'he', 'him', 'his', 'himself', 'she', 'her', 'hers' ,'herself',
                    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',
                    'themselves' ,'am', 'is', 'are','a', 'an', 'the', 'and','in',
                    'out', 'on','up','down', 's', 't']

NB_CLASSIFIER_CLASS_NAME = NaiveBayesClassifier.__name__
MAXENT_CLASSIFIER_CLASS_NAME = MaxentClassifier.__name__
MAXENT_CLASSIFIER_PARAMS = { "max_iter" : 3, "algorithm" : "GIS"}
DTREE_CLASSIFIER_CLASS_NAME = DecisionTreeClassifier.__name__
EMPTY_CLASSIFIER_PARAMS = { }

class_ = getattr(nltk.classify, NB_CLASSIFIER_CLASS_NAME)
class_params = EMPTY_CLASSIFIER_PARAMS

wn_lemmatizer = nltk.stem.WordNetLemmatizer()

def precision_recall_F_Measure(classifier, testfeats):
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)

    for i, (feats, label) in enumerate(testfeats):
        refsets[label].add(i)
        observed = classifier.classify(feats)
        testsets[observed].add(i)

    precisions = {}
    recalls = {}
    f = {}

    for label in classifier.labels():
        precisions[label] = nltk.metrics.precision(refsets[label], testsets[label])
        recalls[label] = nltk.metrics.recall(refsets[label], testsets[label])
        f[label] = nltk.metrics.f_measure(refsets[label], testsets[label])
    return precisions, recalls, f


def _get_words_from_dataset(dataset):
    """Return a set of all words in a dataset.

    :param dataset: A list of tuples of the form ``(words, label)`` where
        ``words`` is either a string of a list of tokens.
    """

    # Words may be either a string or a list of tokens. Return an iterator
    # of tokens accordingly
    def tokenize(words):
        if isinstance(words, basestring):
            return word_tokenize(words, include_punc=False)
        else:
            return words

    all_words = chain.from_iterable(tokenize(words) for words, _ in dataset)
    return set(all_words)


def _get_document_tokens(document):
    if isinstance(document, basestring):
        tokens = set((strip_punc(w, all=False)
                      for w in word_tokenize(document, include_punc=False)))
    else:
        tokens = set(strip_punc(w, all=False) for w in document)
    return tokens

# data should be a dictionary
def _export_to_json(data, path, file_name):
    with open(path + "/" + file_name+'.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)

def _load_from_json(path, file_name):
    json_filename = path + "/" + file_name+'.json'
    with io.open(json_filename) as data_file:
        data = json.load(data_file)
    return data

def _get_review_data_old(label, pos_tblname, neg_tblname):
    data_file_json = "data/%s" % label + "_tt.json"
    data_file_json_p = pathlib.Path(data_file_json)

    if not data_file_json_p.exists():
        raise Exception("Missing data file.")
    else:
        print "Load json data from json"
        Data = _load_from_json("data/", label + "_tt")

    return Data

def _get_review_data(label, pos_tblname, neg_tblname, filename_suffix = ""):
    data_file_json = "data/%s" % label + filename_suffix + ".json"
    data_file_json_p = pathlib.Path(data_file_json)

    if not data_file_json_p.exists():
        raise Exception("Missing data file.")
    else:
        print "Load json data from json"
        Data = _load_from_json("data/", label + filename_suffix)

    return Data

def _get_review_data_custom(label, pos_tblname, neg_tblname, filename_suffix = "_custom"):
    data_file_json = "data/%s" % label + filename_suffix + ".json"
    print "looking for file %s " % data_file_json
    data_file_json_p = pathlib.Path(data_file_json)

    if not data_file_json_p.exists():
        raise Exception("Missing data file.")
    else:
        print "Load json data from json"
        Data = _load_from_json("data/", label + filename_suffix)

    return Data

class BaseReviewClassifier(object):

    def __init__(self, classifier_cfg):
        self.cfg = classifier_cfg

        self.rating_dict = {}
        self.senti_dict = {}
        self.senti_pos_dict = {}
        self.senti_neg_dict = {}
        self.present_simple_dict = {}
        self.present_con_dict = {}
        self.past_simple_dict = {}
        self.future_dict = {}

    def classifier_fetch_data_features(self, data, init_trainset, classifier_cfg):

        data_features = init_trainset

        for row in data:
            title = ""
            try:
                title = row["title"]
                # print "title:%s" % title
                review = row[classifier_cfg.db_comment_column_name] #.decode('utf-8',errors = 'ignore')
                if review is None or review =="":
                    review = ""

            except:
                print (sys.exc_info()[0])
                print ("!!!! ERROR: %s" % row[classifier_cfg.db_comment_column_name])
                continue

            if title is None or title =="":
                title = ""
            else:
                title_token_list = nltk.word_tokenize(title)
                if classifier_cfg.remove_stopwords:
                    title_token_list = [word.lower() for word in title_token_list]
                    title_token_list = [w for w in title_token_list if not w in CUSTOM_STOPWORDS]
                if classifier_cfg.lemmatize:
                    # print "Lemmatize title"
                    title_token_list = [wn_lemmatizer.lemmatize(w) for w in title_token_list]
                title = str(title_token_list)

            rating = row["rating"]

            sentiScore = row["sentiScore"]
            senti_pos = row["sentiScore_pos"]
            senti_neg = row["sentiScore_neg"]

            present_simple = row["present_simple"]
            present_con = row["present_con"]
            past_simple = row["past"]
            future = row["future"]

            if present_simple:
                present_simple = float(int(present_simple))
                self.present_simple_dict.update({review: present_simple})

            if present_con:
                present_con = float(int(present_con))
                self.present_con_dict.update({review: present_con})

            if past_simple:
                past_simple = float(int(past_simple))
                self.past_simple_dict.update({review: past_simple})

            if future:
                future = float(int(future))
                self.future_dict.update({review: future})

            if rating:
                rating = float(rating)
                rating = int(rating)
                self.rating_dict.update({review: rating})
                # self.rating_dict.update({title: rating})

            self.senti_dict.update({review: sentiScore})
            self.senti_pos_dict.update({review: senti_pos})
            self.senti_neg_dict.update({review: senti_neg})

            data_features.append((title, review, row["label"]))

        return data_features

    def get_featureset_label_list(self, review_label_list):

        self.word_features = _get_words_from_dataset(review_label_list)

        featureset_label_list = [(self.extractor(d), c) for d, c in review_label_list]

        return featureset_label_list

    def classifier_Train(self, train, test, labels):
        print('Training the Classifier (%s Classifier)' % labels)

        train_set_final = []
        test_set_final = []

        train_text = []
        for item in train:
            train_text.append((item[0] + item[1], item[2])) #review text,label
            train_set_final.append((item[0] + item[1], item[2]))

        for item in test:
            test_set_final.append((item[0] + item[1], item[2]))

        start_time = time.time()
        self.word_features = _get_words_from_dataset(train_set_final)

        train_features_labels = [(self.extractor(d), c) for d, c in train_set_final]

        cl = class_.train(train_features_labels, **class_params)
        end_time = time.time()

        P = collections.defaultdict(set)
        R = collections.defaultdict(set)
        F = collections.defaultdict(set)

        test_features_labels = [(self.extractor(d), c) for d, c in test_set_final]

        for label in labels:
            refsets = collections.defaultdict(set)
            testsets = collections.defaultdict(set)

            for i, (feats, lbl) in enumerate(test_features_labels):
                refsets[lbl].add(i)
                observed = cl.classify(feats)
                testsets[observed].add(i)

            p = nltk.precision(refsets[label], testsets[label])
            if p is None:
                p = 0

            r = nltk.recall(refsets[label], testsets[label])
            if r is None:
                r = 0

            f = nltk.f_measure(refsets[label], testsets[label])
            if f is None:
                f = 0
            print "label: %s" % label
            print("P:%s, R:%s, F:%s" % (p,r,f))
            P[label] = p
            R[label] = r
            F[label] = f

        cl.show_most_informative_features(10)
        return P,R,F, (end_time - start_time)

    # Feature Extraction
    def extractor(self, document):
        #print document
        feats = {}
        token_list = nltk.word_tokenize(document)
        token_list = [word.lower() for word in token_list]
        length_words = len(token_list)

        rating_dict = self.rating_dict
        senti_dict = self.senti_dict
        senti_pos_dict = self.senti_pos_dict
        senti_neg_dict = self.senti_neg_dict
        present_simple_dict = self.present_simple_dict
        present_con_dict = self.present_con_dict
        past_simple_dict = self.past_simple_dict
        future_dict = self.future_dict

        if self.cfg.bow:
            bow_features = dict(((u'contains({0})'.format(word), (word in token_list))
                             for word in self.word_features))

            feats = dict(feats.items() + bow_features.items())

        if self.cfg.bigram:
            bigrams = self.extract_bigram_words(token_list)
            bigram_features = dict()
            for (w1,w2) in bigrams:
                bigram_features[u'collocation({0},{1})'.format(w1,w2)] = True
            feats = dict(feats.items() + bigram_features.items())

        if self.cfg.rating:
            feats["rating({0})".format(rating_dict.get(document))] = True

        if self.cfg.length:
            feats["length({0})".format(length_words)] = True

        if self.cfg.sentiment1:
            feats["senti_Score({0})".format(senti_dict.get(document))] = True

        if self.cfg.tense:
            v1 = 0
            v2 = 0
            v3 = 0
            v4 = 0
            if present_simple_dict.get(document):
                v1 = int(float(present_simple_dict.get(document)))
            if present_con_dict.get(document):
                v2 = int(float(present_con_dict.get(document)))
            if past_simple_dict.get(document):
                v3 = int(float(past_simple_dict.get(document)))
            if future_dict.get(document):
                v4 = int(float(future_dict.get(document)))

            total_verbs = int(v1 + v2 + v3 + v4)
            if v1 > 0:
                feats["include_present_simple({0})".format(v1 / float(total_verbs))] = True
                v = 0
            if v2 > 0:
                feats["include_present_con({0})".format(v2 / float(total_verbs))] = True
                v = 0
            if v3 > 0:
                feats["include_past_simple({0})".format(v3 / float(total_verbs))] = True
                v = 0
            if v4 > 0:
                feats["include_future({0})".format(v4 / float(total_verbs))] = True
                v = 0

        if self.cfg.sentiment2:
            feats["senti_Score_pos({0})".format(senti_pos_dict.get(document))] = True
            feats["senti_Score_neg({0})".format(senti_neg_dict.get(document))] = True

        return feats

    def extract_bigram_words(self, input_data):
        return self.find_ngrams(input_data, 2)

    def find_ngrams(self, input_list, n):
        return zip(*[input_list[i:] for i in range(n)])

class ReviewClassifier (BaseReviewClassifier):
    def __init__(self, csv_prefix, labels, pos_tbl_prefix, neg_tbl_prefix, classifier_cfg, cfg_id, init_trainset, old_traintest_set = False, datafile_suffix="_all"):

        BaseReviewClassifier.__init__(self, classifier_cfg)

        Data = []

        for label in labels:
            data_file_json = "data/%s" % label + datafile_suffix + ".json"

            if old_traintest_set:
                print("read old data")
                d = _get_review_data_old(label, pos_tbl_prefix, neg_tbl_prefix)
            else:
                print("read data")
                d = _get_review_data_custom(label, pos_tbl_prefix, neg_tbl_prefix, datafile_suffix)

            Data = Data + d

        if len(labels) > 1:
            print "multiclass version..."
            print "filter Not_ Labels..."

            Data = [item for item in Data if item["label"] in labels]

        else:
            tmp_labels = labels + ["Not_" + l for l in labels]
            labels = tmp_labels

        # number of folds
        num_folds = 10

        # obtain the size of the data
        data_size = len(Data)

        #
        # calculate the train and test size
        train_size = int(round(data_size * 0.7))
        test_size = int(round(data_size * 0.3))

        # scores arrays
        self.precision = {}
        self.recall = {}
        self.f_measure = {}

        self.mean_precision = {}
        self.mean_recall = {}
        self.mean_f_measure = {}


        for label in labels:
            self.precision[label] = []
            self.recall[label] = []
            self.f_measure[label] = []

            self.mean_precision[label] = []
            self.mean_recall[label] = []
            self.mean_f_measure[label] = []

        self.time = []

        # feature dictionaries
        self.train = []
        self.test = []

        self.data_with_label = self.classifier_fetch_data_features(Data, init_trainset, classifier_cfg)

        test_counter = collections.Counter()
        train_counter = collections.Counter()

        #
        # test and train the classifier for each fold
        for i in range(num_folds):

            for label in labels:
                test_counter[label] = 0
                train_counter[label] = 0

            # randomize
            random.shuffle(self.data_with_label)

            # select test and training sets
            self.test = self.data_with_label[-test_size:]
            self.train = self.data_with_label[:train_size]

            for item in self.test:
                test_counter[item[2]] += 1

            for item in self.train:
                train_counter[item[2]] += 1

            for label in labels:
                if not label.startswith("Not") and not len(labels) > 1:
                    print("Test %s/%s ratio: %s/%s" % (label, "Not_" + label, test_counter[label], test_counter["Not_" + label]))
                    print("Train %s/%s ratio: %s/%s" % (label, "Not_" + label, train_counter[label], train_counter["Not_" + label]))

            # obtain metrics
            P, R, F, t = self.classifier_Train(self.train, self.test, labels)

            # print training/testing ratio
            print "ratio training/testing: %s" % len(self.train), len(self.test)

            for label in labels:
                self.precision[label].append(P[label])
                self.recall[label].append(R[label])
                self.f_measure[label].append(F[label])

                self.time.append(t)


        #
        # calculate mean scores
        for label in labels:
            self.mean_precision[label] = (sum(self.precision[label]) / len(self.precision[label]))
            self.mean_recall[label] = (sum(self.recall[label]) / len(self.recall[label]))
            self.mean_f_measure[label] = (sum(self.f_measure[label]) / len(self.f_measure[label]))

        self.mean_time = (sum(self.time) / len(self.time))

        row_dict_techniques = {"bow" : classifier_cfg.bow,
                    "bigram" : classifier_cfg.bigram,
                    "lemmatize" : classifier_cfg.lemmatize,       #depends on BoW
                    "remove_stopwords" : classifier_cfg.remove_stopwords, #depends on BoW
                    "rating" : classifier_cfg.rating,
                    "length" : classifier_cfg.length,
                    "tense" : classifier_cfg.tense,
                    "sentiment1" : classifier_cfg.sentiment1,
                    "sentiment2" : classifier_cfg.sentiment2,
                    "db_comment_column_name" : classifier_cfg.db_comment_column_name}

        for label in labels:
            csv_prefix_tmp = csv_prefix + label + "_"
            print "Means for %s" % label
            print "Mean_precision"
            print self.mean_precision[label]
            print "Mean_recall"
            print self.mean_recall[label]
            print "Mean_f_measure"
            print self.mean_f_measure[label]
            print "Mean_time"
            print self.mean_time

            filename = '%smeanscores_70_30.csv' % csv_prefix_tmp
            p = pathlib.Path(filename)
            writeheader = not p.exists()

            with open(filename, "a+") as csvfile:
                fieldnames = ["cfg_id"] + CLASSIFIER_TECHNIQUES + ["db_comment_column_name"]
                fieldnames = fieldnames + ['Mean_Precision', 'Mean_Recall', 'Mean_F1Score', 'Mean_Time']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONE)

                if writeheader:
                    writer.writeheader()

                row_dict_means = {'Mean_Precision': self.mean_precision[label], 'Mean_Recall': self.mean_recall[label], 'Mean_F1Score': self.mean_f_measure[label], 'Mean_Time' : self.mean_time}
                row_dict_final = dict ({"cfg_id" : cfg_id}.items() + row_dict_techniques.items() + row_dict_means.items())

                writer.writerow(row_dict_final)

            filename = '%sprecision_70_30.csv' % csv_prefix_tmp
            p = pathlib.Path(filename)
            writeheader = not p.exists()

            with open(filename, "a+") as csvfile:
                fieldnames = ["cfg_id"] + CLASSIFIER_TECHNIQUES + ["db_comment_column_name"]
                fieldnames = fieldnames + ['%s_fold'%i for i in range(1,num_folds+1)]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONE)
                if writeheader:
                    writer.writeheader()

                row_dict_folds = {'%s_fold'%i : self.precision[label][i-1] for i in range(1,num_folds+1)}

                row_dict_final = dict ({"cfg_id" : cfg_id}.items() +row_dict_techniques.items() + row_dict_folds.items())
                writer.writerow(row_dict_final)


            filename = '%srecall_70_30.csv' % csv_prefix_tmp
            p = pathlib.Path(filename)
            writeheader = not p.exists()

            with open(filename, "a+") as csvfile:
                fieldnames = ["cfg_id"] + CLASSIFIER_TECHNIQUES + ["db_comment_column_name"]
                fieldnames = fieldnames + ['%s_fold'%i for i in range(1,num_folds+1)]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONE)
                if writeheader:
                    writer.writeheader()

                row_dict_folds = {'%s_fold'%i : self.recall[label][i-1] for i in range(1,num_folds+1)}

                row_dict_final = dict ({"cfg_id" : cfg_id}.items() +row_dict_techniques.items() + row_dict_folds.items())
                writer.writerow(row_dict_final)

            filename = '%sf1score_70_30.csv' % csv_prefix_tmp
            p = pathlib.Path(filename)
            writeheader = not p.exists()

            with open(filename, "a+") as csvfile:
                fieldnames = ["cfg_id"] + CLASSIFIER_TECHNIQUES + ["db_comment_column_name"]
                fieldnames = fieldnames + ['%s_fold'%i for i in range(1,num_folds+1)]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONE)
                if writeheader:
                    writer.writeheader()

                row_dict_folds = {'%s_fold'%i : self.f_measure[label][i-1] for i in range(1,num_folds+1)}

                row_dict_final = dict ({"cfg_id" : cfg_id}.items() + row_dict_techniques.items() + row_dict_folds.items())
                writer.writerow(row_dict_final)


        filename = '%stime_70_30.csv' % csv_prefix
        p = pathlib.Path(filename)
        writeheader = not p.exists()

        with open(filename, "a+") as csvfile:
            fieldnames = ["cfg_id"] + CLASSIFIER_TECHNIQUES + ["db_comment_column_name"]
            fieldnames = fieldnames + ['%s_fold'%i for i in range(1,num_folds+1)]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_NONE)
            if writeheader:
                writer.writeheader()

            row_dict_folds = {'%s_fold'%i : self.time[i-1] for i in range(1,num_folds+1)}

            row_dict_final = dict ({"cfg_id" : cfg_id}.items() + row_dict_techniques.items() + row_dict_folds.items())
            writer.writerow(row_dict_final)

def probability(self, text, classifier, label):
    prob_dist = classifier.prob_classify(text)
    print "probaility of having a %s report review" % label
    print prob_dist.prob(label)
    print "classified as :"
    print prob_dist.max()

