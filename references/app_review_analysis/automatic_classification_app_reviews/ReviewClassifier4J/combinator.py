import collections
from itertools import combinations

_basic_techniques = ["bow","bigram","lemmatize","remove_stopwords"]
_metadata_techniques = ["rating","length","tense"]
_sentiment_techniques = ["sentiment1","sentiment2"]

CLASSIFIER_TECHNIQUES = _basic_techniques + _metadata_techniques + _sentiment_techniques

classifier_technique_configurator = collections.namedtuple("classifier_technique_configurator",
                                                     [
                            "bow",
                            "bigram",
                            "lemmatize",       #depends on BoW
                            "remove_stopwords", #depends on BoW
                            "rating",
                            "length",
                            "tense",
                            "sentiment1",
                            "sentiment2",
                            "db_comment_column_name"]) #depends on lemmatization and stopwords
# global classifier_technique_configurator

def _get_combinations(dict):

    n = len(dict)
    out = []

    text_f = set(["bow", "bigram"])
    for i in range(1,n+1):
        combis = combinations(dict, i)
        for combi in combis:
            sentiment_in = False
            out_combi = []
            for c in combi:
                if "sentiment" in c:
                    if sentiment_in:
                        continue
                    sentiment_in=True

                # if "bow" in c:
                #     print "bow!!!!!!!!"
                out_combi.append(c)

            # lemmatize and remove_stopwords make only sense with bow
            if len(text_f.intersection(set(out_combi))) == 0 and ("lemmatize" in out_combi or "remove_stopwords" in out_combi):
                print "NO!!!: %s" % out_combi
                continue

            out.append(out_combi)


    return out

def get_all_classifier_techniques():
    out = _get_combinations(CLASSIFIER_TECHNIQUES)

    return out

def get_all_classifier_technique_configs(class_techniques_combis):

    out = []
    # 04: comment (unpreprocessed text)
    # 11: lemmatized_comment
    # 10: stopwords_removal
    # 16: stopwords_removal_nltk
    # 17: stopwords_removal_lemmatization

    for combis in class_techniques_combis:
        db_comment_column_name = "comment"

        #
        # the relevant db column for the comment
        if "remove_stopwords" in combis and "lemmatize" in combis:
            db_comment_column_name = "stopwords_removal_lemmatization"
        elif "remove_stopwords" in combis:
            db_comment_column_name = "stopwords_removal"
        elif "lemmatize" in combis:
            db_comment_column_name = "lemmatized_comment"

        classifier_technique_cfg = classifier_technique_configurator(
            bow = "bow" in combis,
            bigram = "bigram" in combis,
            lemmatize = "lemmatize" in combis,       #depends on BoW
            remove_stopwords = "remove_stopwords" in combis, #depends on BoW
            rating = "rating" in combis,
            length = "length" in combis,
            tense = "tense" in combis,
            sentiment1 = "sentiment1" in combis,
            sentiment2 = "sentiment2" in combis,
            db_comment_column_name = db_comment_column_name
        )

        out.append(classifier_technique_cfg)

    return out


def get_key_for_classifier_config(cfg):
    return "-".join([field for i,field in enumerate(cfg._fields) if not isinstance(cfg[i], basestring) and cfg[i]])

def get_classifier_technique_config(bow=False, bigram=False, lemmatize = False, remove_stopwords = False, rating = False, length = False, tense = False, sentiment1 = False, sentiment2 = False):

    db_comment_column_name = "comment"

    #
    # find the relevant db column for the comment
    if remove_stopwords and lemmatize:
        db_comment_column_name = "stopwords_removal_lemmatization"
    elif remove_stopwords:
        db_comment_column_name = "stopwords_removal"
    elif lemmatize:
        db_comment_column_name = "lemmatized_comment"

    classifier_technique_cfg = classifier_technique_configurator(
        bow = bow,
        bigram = bigram,
        lemmatize = lemmatize,       #depends on BoW
        remove_stopwords = remove_stopwords,
        rating = rating,
        length = length,
        tense = tense,
        sentiment1 = sentiment1,
        sentiment2 = sentiment2,
        db_comment_column_name = db_comment_column_name
    )

    return classifier_technique_cfg

DEBUG = False
if DEBUG:
    ct = get_all_classifier_techniques()
    ct_cfg = get_all_classifier_technique_configs(ct)

    print ct
