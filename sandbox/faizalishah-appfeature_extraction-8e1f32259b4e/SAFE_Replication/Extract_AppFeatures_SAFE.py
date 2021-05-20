import spacy
import SAFE_Patterns
from Text_Preprocessing import TextProcessing
import SAFE_Evaluation
import ReadXMLData
from ReadXMLData import XML_REVIEW_DATASET
from SAFE_Evaluation import Evaluate
import Text_Preprocessing
import importlib
import json
from urllib.request import urlopen
import re
import requests
from nltk.stem.snowball import SnowballStemmer
import time
import nltk
import numpy as np
import pickle
import csv
from collections import Counter
from numpy import linalg as LA
import math
import re
import argparse

nltk.download('universal_tagset')

importlib.reload(SAFE_Evaluation)
importlib.reload(SAFE_Patterns)
importlib.reload(Text_Preprocessing)
importlib.reload(ReadXMLData)


stemmer = SnowballStemmer("english")
nlp = spacy.load('en_core_web_sm')

parser = argparse.ArgumentParser(description='Optional app description')

parser.add_argument('-r','--source', type=str, required = True,
                    help='app description or user reviews')

parser.add_argument('--dataset', type=str, required = False,
                    help='review dataset')

 
from enum import Enum
class ENGLISH_APPS(Enum):
    ANGRY_BIRD = 343200656
    DROP_BOX= 327630330
    EVERNOTE = 281796108
    TRIP_ADVISOR = 284876795
    PIC_ART= 587366035
    PINTEREST = 429047995
    WHATSAPP=310633997

class ENGLISH_APPCATS(Enum):
    ANGRY_BIRD = 1
    EVERNOTE= 2
    TRIP_ADVISOR = 3
    PIC_ART= 4
    PINTEREST = 5
    WHATSAPP= 6
    # GAME = 1
    # PRODUCTIVITY= 2
    # TRAVEL = 3
    # PHOTOGRAPHY= 4
    # SOCIAL = 5
    # COMMUNICATION= 6

class DATASETS(Enum):
    GUZMAN=1
    GUZMAN_PLUS=2
    SHAH_I = 3
    SHAH_II = 4
    SHAH_UNION=5
    SHAH_INTERSECTION=6
    LAPTOP  = 7
    RESTAURANT = 8
    
class CONFIGURATION(Enum):
    ALL_FEATURES=1
    TWO_TO_FOUR_WORDS=2

class EXTRACTION_MODE(Enum):
    APP_DESCRIPTION = 1
    USER_REVIEWS= 2

class EvaluationType(Enum):
    EXACT_TOKEN = 1
    PARTIAL_TOKEN = 2
    EXACT_TYPE = 3
    PARTIAL_TYPE = 4
    SUBSET_TOKEN = 5


class SAFE:
    def __init__(self,appName,review_sents,extract_mode,nlp):
        self.nlp = nlp
        self.data = review_sents
        self.appName= appName
        self.extract_mode = extract_mode
    
    def GetReviewsWithExtractedFeatures(self):
        self.PreprocessData()
        return self.data,self.extracted_app_features_reviews
    
   
    def PreprocessData(self):
        self.reviews_with_sents_n_features={}
        
        if self.extract_mode == EXTRACTION_MODE.APP_DESCRIPTION:
            sents_segmented= True
        else:
            sents_segmented = False
        
        count=0

        for review_id in self.data.keys():
            review_sent_text  = self.data[review_id]['review_sent']
        
            sents_with_features={}
            reviewSent_wise_features=[]
    
            textProcessor = TextProcessing(self.appName,review_sent_text)
            unclean_sents = textProcessor.SegmemtintoSentences(sents_segmented)
            review_clean_sentences = textProcessor.GetCleanSentences()
            SAFE_Patterns_Obj=SAFE_Patterns.SAFE_Patterns(self.appName,review_id,review_clean_sentences,unclean_sents)
            sents_with_features = SAFE_Patterns_Obj.ExtractFeatures_Analyzing_Sent_POSPatterns()

            for sid in sents_with_features.keys():
                reviewSent_wise_features.extend(sents_with_features[sid]['extracted_features'])

            self.reviews_with_sents_n_features[review_id] = sents_with_features
            self.data[review_id]['predicted_features'] = reviewSent_wise_features
        
            count = count + 1

        self.extracted_app_features_reviews = self.GetListOfExtractedAppFeatures()
        
    def CleanFeatures(self,true_features_dict):
     
        app_words= self.appName.lower().split('_')
        
        # remove noise
        for review_id in true_features_dict.keys():
            #found_index=-1
            review_level_features_info  = true_features_dict[review_id]
            review_text = review_level_features_info['review_sent']
            lst_extracted_feature = true_features_dict[review_id]['predicted_features']
            list_clean_feaures=[]
            for findex, feature_info in enumerate(lst_extracted_feature):
                regex = re.compile('[@_!#$%^&*()-<>?/\|}{~:]')
                contain_special_character=False
                if(regex.search(feature_info[0]) == None):
                    contain_special_character = False
                else:
                    contain_special_character = True
                    
                words = feature_info[0].split()
                parseFeature = nlp(feature_info[0])
                duplicate_words = all(stemmer.stem(x) == stemmer.stem(words[0]) for x in words)
                contain_pronoun = any([w.tag_=='PRP' for w in parseFeature])
                contain_punct =  any([w.tag_ =='LS' for w in parseFeature])
                lemma_app_words = [w.lemma_ for w in parseFeature]
                contain_app_words = all(w in lemma_app_words for w in app_words)
            
                if contain_pronoun!=True and duplicate_words!=True  and contain_punct!=True and contain_app_words!=True and contain_special_character!=True:
                    list_clean_feaures.append(feature_info)
            
            clean_features_list = list_clean_feaures.copy()
            
            # if shorter extracted app features are subsequence of a longer aspect term , remove shorter
        
            for feature_term1 in list_clean_feaures:
                status = any([feature_term1[0] in f[0] for f in list_clean_feaures if f[0]!=feature_term1[0]])
                if status==True:
                    clean_features_list.remove(feature_term1)
            
            true_features_dict[review_id]['predicted_features'] = list(set(clean_features_list))
        
        return true_features_dict
        
    
    def GetListOfExtractedAppFeatures(self):
        list_extracted_app_features=[]
        for sent_id in self.reviews_with_sents_n_features.keys():
            sents_with_app_features = self.reviews_with_sents_n_features[sent_id]
            for sent_id in sents_with_app_features.keys():
                app_features = sents_with_app_features[sent_id]['extracted_features']
                list_extracted_app_features.extend(app_features)
        
        return(list_extracted_app_features)


def ReadAppDescWithAspectTerms(app_data):
   
    sents_with_aspect_terms={}

    #app_id = app_data['id']
    app_name = app_data['app_name']
    app_true_features = app_data['app_features']
    app_description = app_data['app_description']

    true_features=[]

    for t_feature in app_true_features:
        comma_s_pattern = r'\'s'
        true_feature= re.sub(comma_s_pattern,"",t_feature)
        true_features.append(true_feature)

    sents_with_aspect_terms[app_name]={'review_sent':app_description,'true_features':true_features,'predicted_features':[], 'review-id':app_name} #,'sent_class': sent_class}


    return(sents_with_aspect_terms)


if __name__ == '__main__':
    
    lst_precision=[]
    lst_recall=[]
    lst_fscore=[]

    args = parser.parse_args()

    text_source = args.source
    
    if text_source == "user_reviews":

        review_dataset = args.dataset

        extraction_mode = EXTRACTION_MODE.USER_REVIEWS
        
        # user review data for the evaluation
        user_review_dataset = review_dataset
        
        # 2-4 words aspect terms evaluation model or all aspect terms evaluation mode
        evaluation_mode = CONFIGURATION.TWO_TO_FOUR_WORDS
        
        if review_dataset not in [DATASETS.GUZMAN_PLUS.name, DATASETS.LAPTOP.name, DATASETS.RESTAURANT.name]:
        
            
            for app in ENGLISH_APPCATS:
                print('*' * 5, app.name,'*' * 5)
                objXML_DS = XML_REVIEW_DATASET(user_review_dataset,app.name)
                reviewSents_with_true_features = objXML_DS.ReadReviewSentsWithAspectTerms()

                obj_safe = SAFE(app.name,reviewSents_with_true_features,extraction_mode,nlp)
                true_features_dict,extracted_features = obj_safe.GetReviewsWithExtractedFeatures()
                dict_true_features = obj_safe.CleanFeatures(true_features_dict)
                obj_Evaluation = Evaluate(app,dict_true_features,extracted_features,evaluation_mode,EvaluationType.SUBSET_TOKEN)
                dict_features_evaluated,token_eval_results= obj_Evaluation.PerformEvaluation()

                lst_precision.append(float(token_eval_results['precision']))
                lst_recall.append(float(token_eval_results['recall']))
                lst_fscore.append(float(token_eval_results['fscore']))
                print("")

            print('----------------------------------------------------------------------------------------------')
            avg_precision = '%.3f' % np.average(lst_precision)
            avg_recall= '%.3f' % np.average(lst_recall)
            avg_fscore = '%.3f' % np.average(lst_fscore)
            print('Precision : %.3f , Recall , %.3f , F1-score : %.3f' % (np.average(lst_precision),np.average(lst_recall),np.average(lst_fscore)))        
            print('----------------------------------------------------------------------------------------------')    
        else:
            print('*' * 5, user_review_dataset,'*' * 5)
            
            objXML_DS = XML_REVIEW_DATASET(user_review_dataset,user_review_dataset)
            reviewSents_with_true_features = objXML_DS.ReadReviewSentsWithAspectTerms()

            obj_safe = SAFE(user_review_dataset,reviewSents_with_true_features,extraction_mode,nlp)
            true_features_dict,extracted_features = obj_safe.GetReviewsWithExtractedFeatures()
            dict_true_features = obj_safe.CleanFeatures(true_features_dict)
            obj_Evaluation = Evaluate(user_review_dataset,dict_true_features,extracted_features,evaluation_mode,EvaluationType.SUBSET_TOKEN)
            dict_features_evaluated,token_eval_results= obj_Evaluation.PerformEvaluation()
           
            print('----------------------------------------------------------------------------------------------')
    elif text_source == "app_description":
        extraction_mode = EXTRACTION_MODE.APP_DESCRIPTION
        data_path = 'APP_DESCRIPTION/app_descriptions_with_manual_feature_extraction.json'
        with open(data_path) as json_data:
            data = json.load(json_data)
            evaluation_mode = CONFIGURATION.ALL_FEATURES
            for app_data in data:
                #if app_data["id"] == "507874739":
                print('*' * 5, app_data['app_name'],'*' * 5)
                AppDesc_with_true_features = ReadAppDescWithAspectTerms(app_data)
                obj_safe = SAFE(app_data['app_name'],AppDesc_with_true_features,extraction_mode,nlp)
                true_features_dict,extracted_features = obj_safe.GetReviewsWithExtractedFeatures()
                #print(extracted_features)
                dict_true_features = obj_safe.CleanFeatures(true_features_dict)
                #print(dict_true_features)
                obj_Evaluation = Evaluate(app_data['app_name'],dict_true_features,extracted_features,evaluation_mode)
                dict_features_evaluated,token_eval_results= obj_Evaluation.PerformEvaluation()
                
                lst_precision.append(float(token_eval_results['precision']))
                lst_recall.append(float(token_eval_results['recall']))
                lst_fscore.append(float(token_eval_results['fscore']))
        
        print('----------------------------------------------------------------------------------------------')
        avg_precision = '%.3f' % np.average(lst_precision)
        avg_recall= '%.3f' % np.average(lst_recall)
        avg_fscore = '%.3f' % np.average(lst_fscore)
        print('Precision : %.3f , Recall , %.3f , F1-score : %.3f' % (np.average(lst_precision),np.average(lst_recall),np.average(lst_fscore)))        
        print('----------------------------------------------------------------------------------------------')

