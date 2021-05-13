#!/usr/bin/env python

import pickle

import pathlib

from combinations import get_custom_cfgs_bow, get_combined_cfgs_journal_version
from review_classifier import ReviewClassifier, _get_review_data_custom
import combinator

SOURCE_ALL = "all"
SOURCE_PLAYSTORE = "PlayStore"
SOURCE_APPSTORE = "AppStore"

OUTPUT_FOLDER = "output_all/"

# 04: unpreprocessed text
# 11: lemmatized_comment
# 10: stopwords_removal
# 16: stopwords_removal_nltk
# 17: stopwords_removal_lemmatization

DEBUG = False
DEBUG_CFGS = None
DEBUG_LABELS = ["Bug","Feature","UserExperience","Rating"]

def get_all_classifier_cfgs():
    cfg_file = OUTPUT_FOLDER + 'all_technique_configurations.pkl'
    t_file = OUTPUT_FOLDER + 'all_techniques.pkl'
    p = pathlib.Path(cfg_file)

    if not p.exists():
        all_techniques = combinator.get_all_classifier_techniques()
        all_technique_configurations = combinator.get_all_classifier_technique_configs(all_techniques)

        with open(t_file, 'w') as outfile:
            pickle.dump(all_techniques, outfile)

        with open(cfg_file, 'w') as outfile:
            pickle.dump(all_technique_configurations, outfile)
    else:
        with open(cfg_file) as infile:
            all_technique_configurations = pickle.load(infile)

    return all_technique_configurations

def run_multiclass_ttdata(cfgs_dict, datafile_suffix):
    DEBUG_CFGS = cfgs_dict
    DEBUG_LABELS = ["Bug","Feature","UserExperience","Rating"]

    csv_prefix = OUTPUT_FOLDER + "multiclass_result_tt_"
    for (cfg_id, cfg) in DEBUG_CFGS.items():
            ReviewClassifier(csv_prefix, DEBUG_LABELS, "", "", cfg, cfg_id, [], old_traintest_set=False, datafile_suffix=datafile_suffix)

def run_bin_classifier(label, cfgs_dict, datafile_suffix):
    DEBUG_CFGS = cfgs_dict
    DEBUG_LABELS = [label]

    csv_prefix = OUTPUT_FOLDER + "nb_all_results_"
    for (cfg_id, cfg) in DEBUG_CFGS.items():
        ReviewClassifier(csv_prefix, DEBUG_LABELS, "", "", cfg, cfg_id, [], old_traintest_set=False, datafile_suffix=datafile_suffix)

if __name__ == '__main__':

    # cfgs = get_bow_cfg()
    cfgs = get_combined_cfgs_journal_version()

    # run_bin_classifier("Bug", cfgs, "_tt")
    run_bin_classifier("Bug", cfgs, "_tt_lite")

    # debug_run_all_data("Feature", cfgs, "_tt")
    # debug_run_all_data("UserExperience", cfgs, "_tt")
    # debug_run_all_data("Rating", cfgs, "_tt")

    # run_multiclass_ttdata(cfgs, "_tt")

