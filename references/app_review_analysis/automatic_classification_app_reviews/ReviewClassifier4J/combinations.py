#!/usr/bin/env python
import combinator


def get_custom_cfgs_bow():
    toreturn = {}

    toreturn["bow"] = combinator.classifier_technique_configurator(
            bow = True,
            bigram = False,
            lemmatize = False,
            remove_stopwords = False,
            rating = False,
            length = False,
            tense = False,
            sentiment1 = False,
            sentiment2 = False,
            db_comment_column_name = "comment"
    )

    toreturn["bow_metadata"] = combinator.classifier_technique_configurator(
            bow = True,
            bigram = False,
            lemmatize = False,
            remove_stopwords = False,
            rating = True,
            length = True,
            tense = True,
            sentiment1 = True,
            sentiment2 = False,
            db_comment_column_name = "comment"
    )

    return toreturn

def get_combined_cfgs_journal_version():

    toreturn = {}
    cfg = combinator.get_classifier_technique_config(bow=True, lemmatize=True, rating=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, rating=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, rating=True, tense=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bigram=True, rating=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bigram=True, remove_stopwords=True, lemmatize=True, rating=True, tense=True, sentiment2=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, bigram=True, tense=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, lemmatize=True, bigram=True, rating=True, tense=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, remove_stopwords=True, bigram=True, rating=True, tense=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, remove_stopwords=True, lemmatize=True, rating=True, tense=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    cfg = combinator.get_classifier_technique_config(bow=True, remove_stopwords=True, lemmatize=True, rating=True, tense=True, sentiment2=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    return toreturn

def get_bow_rating_tense_sentiment1_cfg():
    toreturn = {}
    cfg = combinator.get_classifier_technique_config(bow=True, rating=True, tense=True, sentiment1=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    return toreturn

def get_bow_rating_lemmatize_cfg(key_prefix):
    toreturn = {}
    cfg = combinator.get_classifier_technique_config(bow=True, rating=True, lemmatize=True)
    key = key_prefix + "__" + combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    return toreturn

def get_bow_rating_sentiment1_cfg(key_prefix):
    toreturn = {}
    cfg = combinator.get_classifier_technique_config(bow=True, rating=True, sentiment1=True)
    key = key_prefix + "__" + combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    return toreturn

def get_bow_cfg():
    toreturn = {}
    cfg = combinator.get_classifier_technique_config(bow=True)
    key = combinator.get_key_for_classifier_config(cfg)
    toreturn[key] = cfg

    return toreturn