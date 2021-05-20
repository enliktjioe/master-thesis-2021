from __future__ import division
from xml.etree import ElementTree
from collections import Counter
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from nltk.stem.snowball import SnowballStemmer
import csv
import operator
import numpy as np

from enum import Enum
    
class GERMAN_APPS_CATEGORY(Enum):
    WEATHER_APPS = 1
    SPORT_NEWS= 2
    SOCIAL_NETWORKS = 3
    OFFICE_TOOLS = 4
    NEWS_APPS = 5
    NAVIGATION_APPS = 6
    MUSIC_PLAYERS = 7
    INSTANT_MESSENGERS = 8
    GAMES = 9
    FITNESS_TRACKER = 10
    ALARM_CLOCKS = 11
    
class ENGLISH_APPS_CATEGORY(Enum):
    GAME = 1
    PRODUCTIVITY= 2
    TRAVEL = 3
    PHOTOGRAPHY = 4
    SOCIAL = 5
    COMMUNICATION = 6

class CRFBIOTagEvaluation:
    def __init__(self,testSet_file,trainSet_file):
        with open(testSet_file, 'r') as infile:
            TestData = infile.read()  # Read the contents of the file into memory.
        
        with open(trainSet_file, 'r') as infile:
            TrainData = infile.read()  # Read the contents of the file into memory.
            # Return a list of the lines, breaking at line boundaries.
        self.list_TestSet_lines = TestData.splitlines()
        self.list_TrainSet_lines = TrainData.splitlines()

    
    def EvaluateAspects_Type_based_V1(self,true_aspects,predicted_aspects):
        
        unique_true_aspects = set(true_aspects)
        unique_predicted_aspects = set(predicted_aspects)

        tp = 0
        fp = 0
        fn = 0
        
        tp_aspects=[]
        
        if len(unique_true_aspects)>0 and len(unique_predicted_aspects)>0:
        
            for p_aspect in unique_predicted_aspects:
                
                match = False

                for t_aspect in unique_true_aspects:                

                    status = self.MatchFeatureWords(p_aspect,t_aspect)

                    if status == True:
                        match = True
                        break;

                if match == False:
                    fp = fp + 1
                

            # False Negative cases

            for t_aspect in unique_true_aspects:     

                match=False
                
                for p_aspect in unique_predicted_aspects:
                    status = self.MatchFeatureWords(p_aspect,t_aspect)

                    if status==True:
                        tp_aspects.append(t_aspect)
                        tp = tp  + 1
                        match = True
                        break


                if match == False:
                    fn = fn + 1
        
        try:
            precision = tp/(tp + fp)
        except ZeroDivisionError as err:
            precision=0
        
        try:
            recall = tp / (tp + fn)
        except ZeroDivisionError as err:
            recall = 0
        
        try:
            fscore = 2 * (precision * recall)/(precision + recall)
        except ZeroDivisionError as err:
            fscore = 0 
            
        return (tp,fp,fn,precision,recall,fscore,tp_aspects)
    
    
    def EvaluateAspects_Token_based_V1(self,true_aspects,predicted_aspects):

        tp = 0
        fp = 0
        fn = 0
        
        tp_aspects=[]
        
        if len(true_aspects)>0 and len(predicted_aspects)>0:
        
            for p_aspect in predicted_aspects:
                
                match = False

                for t_aspect in true_aspects:                

                    status = self.MatchFeatureWords(p_aspect,t_aspect)

                    if status == True:
                        match = True
                        break;

                if match == False:
                    fp = fp + 1
                

            # False Negative cases

            for t_aspect in true_aspects:     

                match=False
                
                for p_aspect in predicted_aspects:
                    status = self.MatchFeatureWords(p_aspect,t_aspect)

                    if status==True:
                        tp_aspects.append(t_aspect)
                        tp = tp  + 1
                        match = True
                        break


                if match == False:
                    fn = fn + 1
        
        try:
            precision = tp/(tp + fp)
        except ZeroDivisionError as err:
            precision=0
        
        try:
            recall = tp / (tp + fn)
        except ZeroDivisionError as err:
            recall = 0
        
        try:
            fscore = 2 * (precision * recall)/(precision + recall)
        except ZeroDivisionError as err:
            fscore = 0 
            
        return (tp,fp,fn,precision,recall,fscore,tp_aspects)
    
    def In_Out_Train_AspectTerms_Evaluation(self):
        AspectTerms_InTrain=[]
        AspectTerms_OutTrain=[]
        
        stemmer = SnowballStemmer("english")
        
        stemmed_train_aspects=[]
        stemmed_test_aspects=[]
        stemmed_p_aspects=[]
        
        for train_aspect in self.train_aspect_terms:
            train_aspect_words = train_aspect.strip().split()
            train_aspect_words = [stemmer.stem(w) for w in train_aspect_words]
            update_train_aspect_term = ' '.join(train_aspect_words)
            stemmed_train_aspects.append(update_train_aspect_term.strip())
        
        for test_aspect in self.CRF_true_aspects_list:
            test_aspect_words = test_aspect.strip().split()
            test_aspect_words = [stemmer.stem(w) for w in test_aspect_words]
            update_test_aspect_term = ' '.join(test_aspect_words)
            stemmed_test_aspects.append(update_test_aspect_term.strip())
            
        for p_aspect in self.predicted_aspects_list:
            p_aspect_words = p_aspect.strip().split()
            p_aspect_words = [stemmer.stem(w) for w in p_aspect_words]
            update_p_aspect_term = ' '.join(p_aspect_words)
            stemmed_p_aspects.append(update_p_aspect_term.strip())
    
        for test_aspect in stemmed_test_aspects:
            found = False
            for train_aspect in stemmed_train_aspects:
                match = self.MatchFeatureWords(train_aspect,test_aspect)
                
                if match == True:
                    found=True
                    AspectTerms_InTrain.append(test_aspect)
                    break
            
            if found==False:
                AspectTerms_OutTrain.append(test_aspect)
        
        tp_in,fp_in,fn_in,precision_in,recall_in,fscore_in,tp_aspects_in_train_ = self.EvaluateAspects_Token_based_V1(AspectTerms_InTrain,stemmed_p_aspects)
        tp_out,fp_out,fn_out,precision_out,recall_out,fscore_out,tp_aspects_out_train = self.EvaluateAspects_Token_based_V1(AspectTerms_OutTrain,stemmed_p_aspects)
        
        tp_in_type,fp_in_type,fn_in_type,precision_in_type,recall_in_type,fscore_in_type,tp_aspects_in_train_type = self.EvaluateAspects_Type_based_V1(AspectTerms_InTrain,stemmed_p_aspects)
        tp_out_type,fp_out_type,fn_out_type,precision_out_type,recall_out_type,fscore_out_type,tp_aspects_out_train_type = self.EvaluateAspects_Type_based_V1(AspectTerms_OutTrain,stemmed_p_aspects)
        
        InTrain_evaluation_token_exact = {'TP' : tp_in ,'FP': fp_in , 'FN':fn_in ,'precision' : '%.3f' % precision_in ,'recall' : '%.3f' % recall_in,'fscore' : '%.3f' % fscore_in}
        OutTrain_evaluation_token_exact = {'TP' : tp_out ,'FP': fp_out , 'FN':fn_out ,'precision' : '%.3f' % precision_out ,'recall' : '%.3f' % recall_out,'fscore' : '%.3f' % fscore_out}
        
        InTrain_evaluation_type_exact = {'TP' : tp_in_type ,'FP': fp_in_type , 'FN':fn_in_type ,'precision' : '%.3f' % precision_in ,'recall' : '%.3f' % recall_in_type,'fscore' : '%.3f' % fscore_in_type}
        OutTrain_evaluation_type_exact = {'TP' : tp_out_type ,'FP': fp_out_type , 'FN':fn_out_type ,'precision' : '%.3f' % precision_out ,'recall' : '%.3f' % recall_out_type,'fscore' : '%.3f' % fscore_out_type}
            
        return (InTrain_evaluation_token_exact,InTrain_evaluation_type_exact,OutTrain_evaluation_token_exact,OutTrain_evaluation_type_exact)
    
    def GetAspectTermsInTrainSet(self):
        lines  = self.list_TrainSet_lines
        
        start = False
        end = False
        
        counter=0
        self.train_aspect_terms = []
        
        begin=True
        
        for i in range(0,len(lines)):
            l = lines[i]
            info = l.split("\t")
            #print(info)
            #print(len(info))
            
            if len(info)==3:
            
                if begin==True:
                    start = True
                    true_added = False
                    true_aspects=[]
                    temp_true_aspect_term=[]
                    true_aspect_term=[]
                    true_aspect_started = False
                    sentence_has_true_aspect = False
                    counter = counter + 1
                    true_term_dist = 0
                    begin=False

                if start==True:
                    # when sentence labeled a true aspect
                    
                    if info[2]=="B-TERM":
                        true_aspect_term.append(info[0])
                        
                        true_term_dist = 0
                        true_aspect_started=True
                        
                    if info[2]=="I-TERM" and true_aspect_started==True and true_term_dist==0:
                        true_aspect_term.append(info[0])
                    elif info[2]=="I-TERM" and true_aspect_started==False and true_term_dist>0:
                        true_aspect_term.append(info[0])
                        true_term_dist = 0
                        true_aspect_started=True
                        
                    if info[2]=='O' and true_aspect_started==True:
                        true_aspects.append(true_aspect_term)            
                        true_term_dist = true_term_dist + 1
                        true_aspect_started = False
                        true_aspect_term=[]
    
            if len(info) == 1:
                if len(true_aspects)!=0:

                    sent_true_aspects=[]

                    for t_aspect in true_aspects:
                        str_t_aspect = ' '.join(t_aspect)
                        sent_true_aspects.append(str_t_aspect.lower().strip())
                    
                    if len(true_aspects)!=0:
                        for i in range(0,len(true_aspects)):
                            t_aspect = true_aspects[i]
                            str_true_aspect = ' '.join(t_aspect)
                            self.train_aspect_terms.append(str_true_aspect.lower().strip())

                    start = False
                    begin = True

    def MatchFeatureWords_Partial(self,p_aspect,t_aspect):
        
        t_aspect_words = t_aspect.split()
        t_aspect_size = len(t_aspect_words)
        
        p_aspect_words = p_aspect.split()
        p_aspect_size = len(p_aspect_words)
        
        greater=None
        diff = 0

        if t_aspect_size > p_aspect_size:
            diff = t_aspect_size - p_aspect_size
            greater='true'
        elif p_aspect_size > t_aspect_size:
            greater = 'predict'
            diff = p_aspect_size - t_aspect_size

        status = False

        if diff==1 and greater=='true':
            status = all([w in t_aspect_words for w in p_aspect_words])
        elif diff==1 and greater=='predict':
            status = all([w in p_aspect_words for w in t_aspect_words])
        elif diff==0 and p_aspect_size==t_aspect_size:
            status = all([p_word in t_aspect_words for p_word in p_aspect_words])

        return (status)
    
    def MatchFeatureWords(self,p_aspect,t_aspect):
        
        t_aspect_words = t_aspect.split()
        t_aspect_size = len(t_aspect_words)
        
        p_aspect_words = p_aspect.split()
        p_aspect_size = len(p_aspect_words)        
        
        if p_aspect_size==t_aspect_size:
                status = False
                status = all([p_word in t_aspect_words for p_word in p_aspect_words])

                return(status)
        
                    
        return (False)
    
    def EvaluateAspects_type_based(self,true_aspects,predicted_aspects):

        stemmer = SnowballStemmer("english")

        stemmed_true_aspects=[]
        stemmed_predicted_aspects=[]
        
        for t_aspect in true_aspects:
            t_aspect_words = t_aspect.strip().split()
            t_aspect_words = [stemmer.stem(w) for w in t_aspect_words]
            update_taspect_term = ' '.join(t_aspect_words)
            stemmed_true_aspects.append(update_taspect_term.strip())

        
        for p_aspect in predicted_aspects:
            p_aspect_words = p_aspect.strip().split()
            p_aspect_words = [stemmer.stem(w) for w in p_aspect_words]
            update_paspect_term = ' '.join(p_aspect_words)
            stemmed_predicted_aspects.append(update_paspect_term.strip())
        
        unique_true_aspects = set(stemmed_true_aspects)
        unique_predicted_aspects = set(stemmed_predicted_aspects)
        
#         print("# of unique predicted aspects = %d" % (len(unique_predicted_aspects)))

        tp = 0
        fp = 0
        fn = 0
        
        tp_aspects=[]
        
        if len(unique_true_aspects)>0 and len(unique_predicted_aspects)>0:
        
            for p_aspect in unique_predicted_aspects:
                
                match = False

                for t_aspect in unique_true_aspects:                

                    status = self.MatchFeatureWords(p_aspect,t_aspect)

                    if status == True:
                        match = True
                        break;

                if match == False:
                    fp = fp + 1
                

            # False Negative cases

            for t_aspect in unique_true_aspects:     

                match=False


                for p_aspect in unique_predicted_aspects:
                    status = self.MatchFeatureWords(p_aspect,t_aspect)

                    if status==True:
                        tp_aspects.append(t_aspect)
                        tp = tp  + 1
                        match = True
                        break


                if match == False:
                    fn = fn + 1
        
        try:
            precision = tp/(tp + fp)
        except ZeroDivisionError as err:
            precision=0
        
        try:
            recall = tp / (tp + fn)
        except ZeroDivisionError as err:
            recall = 0
        
        try:
            fscore = 2 * (precision * recall)/(precision + recall)
        except ZeroDivisionError as err:
            fscore = 0 
            
        return (tp,fp,fn,precision,recall,fscore,tp_aspects)
    
    def EvaluateAspects_type_based_partial(self,true_aspects,predicted_aspects):

        stemmer = SnowballStemmer("english")

        stemmed_true_aspects=[]
        stemmed_predicted_aspects=[]
        
        for t_aspect in true_aspects:
            t_aspect_words = t_aspect.strip().split()
            t_aspect_words = [stemmer.stem(w) for w in t_aspect_words]
            update_taspect_term = ' '.join(t_aspect_words)
            stemmed_true_aspects.append(update_taspect_term.strip())

        
        for p_aspect in predicted_aspects:
            p_aspect_words = p_aspect.strip().split()
            p_aspect_words = [stemmer.stem(w) for w in p_aspect_words]
            update_paspect_term = ' '.join(p_aspect_words)
            stemmed_predicted_aspects.append(update_paspect_term.strip())    
        
        unique_true_aspects = set(stemmed_true_aspects)
        unique_predicted_aspects = set(stemmed_predicted_aspects)
        
        tp = 0
        fp = 0
        fn = 0
        
        tp_aspects=[]
        
        if len(unique_true_aspects)>0 and len(unique_predicted_aspects)>0:
        
            for p_aspect in unique_predicted_aspects:
                
                match = False

                for t_aspect in unique_true_aspects:                

                    status = self.MatchFeatureWords_Partial(p_aspect,t_aspect)

                    if status == True:
                        match = True
                        break;

                if match == False:
                    fp = fp + 1

            for t_aspect in unique_true_aspects:     

                match=False


                for p_aspect in unique_predicted_aspects:
                    status = self.MatchFeatureWords_Partial(p_aspect,t_aspect)

                    if status==True:
                        tp_aspects.append(t_aspect)
                        tp = tp  + 1
                        match = True
                        break


                if match == False:
                    fn = fn + 1
        try:
            precision = tp/(tp + fp)
        except ZeroDivisionError as err:
            precision=0
        
        try:
            recall = tp / (tp + fn)
        except ZeroDivisionError as err:
            recall = 0
        
        try:
            fscore = 2 * (precision * recall)/(precision + recall)
        except ZeroDivisionError as err:
            fscore = 0 

        return (tp,fp,fn,precision,recall,fscore,tp_aspects)
    
    
    def Perform_Evaluation_Token_based_Partial(self,true_aspects,predicted_aspects):
        
        tp = 0
        fp = 0
        fn = 0
        
        tp_aspects=[]
        
        for i in range(0,len(true_aspects)):
            t_aspect = true_aspects[i]
            p_aspect = predicted_aspects[i]
            
            if t_aspect == p_aspect and t_aspect!="" and p_aspect!="":
                #print("TP ->" , t_aspect,p_aspect)
                tp = tp  + 1
                tp_aspects.append(t_aspect)
            elif t_aspect!= p_aspect and t_aspect!="" and p_aspect!="":
                t_aspect_words = t_aspect.split()
                p_aspect_words = p_aspect.split()
                
                t_aspect_size = len(t_aspect_words)
                p_aspect_size = len(p_aspect_words)
                
                greater=None
                diff = 0
                
                if t_aspect_size > p_aspect_size:
                    diff = t_aspect_size - p_aspect_size
                    greater='true'
                elif p_aspect_size > t_aspect_size:
                    greater = 'predict'
                    diff = p_aspect_size - t_aspect_size
                
                status = False
                
                if diff==1 and greater=='true':
                    status = all([w in t_aspect_words for w in p_aspect_words])
                elif diff==1 and greater=='predict':
                    status = all([w in p_aspect_words for w in t_aspect_words])
                
                if status==True:
                    tp = tp + 1
                    tp_aspects.append(t_aspect)
                else:
                    fp = fp + 1
                    fn = fn + 1
            elif t_aspect == "" and p_aspect!="":
                #print("FP ->",t_aspect,p_aspect)
                fp = fp  + 1
            elif t_aspect !="" and p_aspect=="":
                #print("FN ->",t_aspect,p_aspect)
                fn = fn + 1
        
        return (tp,fp,fn,tp_aspects)
        
    
    def Perform_Evaluation_Token_based(self,true_aspects,predicted_aspects):
        
        tp = 0
        fp = 0
        fn = 0
        
        tp_aspects=[]
        
        for i in range(0,len(true_aspects)):
            t_aspect = true_aspects[i]
            p_aspect = predicted_aspects[i]
            
            if t_aspect == p_aspect and t_aspect!="" and p_aspect!="":
                #print("TP ->" , t_aspect,p_aspect)
                tp = tp  + 1
                tp_aspects.append(t_aspect)
            elif t_aspect!= p_aspect and t_aspect!="" and p_aspect!="":
                fp = fp + 1
                fn = fn + 1
            elif t_aspect == "" and p_aspect!="":
                #print("FP ->",t_aspect,p_aspect)
                fp = fp  + 1
            elif t_aspect !="" and p_aspect=="":
                #print("FN ->",t_aspect,p_aspect)
                fn = fn + 1
        
        return (tp,fp,fn,tp_aspects)
        
    def PerformEvaluation(self):
        
        lines  = self.list_TestSet_lines
        
        start = False
        end = False
        
        true_predictions = 0
        false_predictions = 0
        false_negatives = 0
        
        tp_partials = 0
        fp_partials = 0
        fn_partials = 0
        
        counter=0
        self.predicted_aspects_list=[]
        self.CRF_true_aspects_list = []
        
        all_tp_aspects_exact=[]
        all_tp_aspects_partial=[]
        
        begin=True
        
        for i in range(0,len(lines)):
            l = lines[i]
            info = l.split("\t")
            #print(info)
            
            if len(info)==5:
            
                if begin==True:
                    start = True
                    true_added = False
                    predicted_added = False
                    true_aspects=[]
                    predicted_aspects=[]
                    temp_predicted_aspect_term=[]
                    temp_true_aspect_term=[]
                    true_aspect_term=[]
                    predict_aspect_term=[]
                    true_aspect_started = False
                    predict_aspect_started = False
                    sentence_has_true_aspect = False
                    sentence_has_predicted_aspect = False
                    both_predictions = False
                    counter = counter + 1
                    true_term_dist = 0
                    predict_term_dist = 0
                    begin=False

                if start==True:
                    # when sentence labeled a true aspect
                    
                    if info[3]=="B-TERM":
                        true_aspect_term.append(info[0])
                        
                        if info[4]=="B-TERM":
                            predict_aspect_term.append(info[0])
                            predict_term_dist=0
                            predict_aspect_started = True
                            both_predictions = True
                        elif info[4]=="O":
                            predict_aspect_term.append("")
                            both_predictions = False
                            predict_term_dist=0
                        
                        true_term_dist = 0
                        true_aspect_started=True
                        
                        if true_aspect_started==True and predict_aspect_started==True and both_predictions==False:
                            both_predictions = True 
                    
                    elif info[4] == "B-TERM":
                        predict_aspect_term.append(info[0])
                        
                        if info[3]=="B-TERM":
                            true_aspect_term.append(info[0])
                            true_term_dist=0
                            true_aspect_started = True
                            both_predictions = True
                        elif info[3]=="O":
                            true_aspect_term.append("")
                            true_term_dist=0
                            both_predictions = False
                        
                        
                        predict_term_dist = 0
                        predict_aspect_started=True
                        
                        if true_aspect_started==True and predict_aspect_started==True and both_predictions==False:
                            both_predictions = True 
                        
                    
                    if info[3]=="I-TERM" and true_aspect_started==True and true_term_dist==0:
                        true_aspect_term.append(info[0])
                    
                        if info[4] == "I-TERM" and predict_aspect_started == True and predict_term_dist==0:
                            predict_aspect_term.append(info[0])
                        elif info[4] == "O":
                            predict_aspect_term.append("")
                    elif info[3]=="I-TERM" and true_aspect_started==False and true_term_dist>0:
                        true_aspect_term.append(info[0])
                        
                        if info[4]=="I-TERM" and predict_aspect_started==False:
                            predict_aspect_term.append(info[0])
                            predict_term_dist=0
                            predict_aspect_started = True
                            both_predictions = True
                        elif info[4]=="O":
                            predict_aspect_term.append("")
                            both_predictions = False
                            predict_term_dist=0
                        
                        true_term_dist = 0
                        true_aspect_started=True
                        
                        if true_aspect_started==True and predict_aspect_started==True and both_predictions==False:
                            both_predictions = True 
                            
                    elif info[4]=="I-TERM" and predict_aspect_started==True and predict_term_dist==0:
                        predict_aspect_term.append(info[0])
                        
                        if info[3] == "I-TERM" and true_aspect_started == True and true_term_dist==0:
                            true_aspect_term.append(info[0])
                        elif info[3] == "O":
                            true_aspect_term.append("")
                    elif info[4]=="I-TERM" and predict_aspect_started==False and predict_term_dist>0:
                        predict_aspect_term.append(info[0])
                        
                        if info[3]=="I-TERM" and true_aspect_started==False:
                            true_aspect_term.append(info[0])
                            true_term_dist=0
                            true_aspect_started = True
                            both_predictions = True
                        elif info[3]=="O":
                            true_aspect_term.append("")
                            both_predictions = False
                            true_term_dist=0
                        
                        predict_term_dist = 0
                        predict_aspect_started=True
                        
                        if true_aspect_started==True and predict_aspect_started==True and both_predictions==False:
                            both_predictions = True 
                        
                    if info[3]=='O' and true_aspect_started==True and predict_aspect_started==False and both_predictions==False:
                        true_aspects.append(true_aspect_term)
                        predicted_aspects.append(predict_aspect_term)
                        predict_aspect_term=[]
                        
                        true_term_dist = true_term_dist + 1
                        true_aspect_started = False
                        true_aspect_term=[]
                    
                    if info[4]=='O' and predict_aspect_started==True and true_aspect_started==False and both_predictions==False:
    
                        true_aspects.append(true_aspect_term)
                        predicted_aspects.append(predict_aspect_term)
                        true_aspect_term=[]
                       
                        predict_term_dist = predict_term_dist + 1
                        predict_aspect_started = False
                        predict_aspect_term=[]
                        

                    if both_predictions==True:
                        if info[3] == 'O' and true_added==False:
                            temp_true_aspect_term=true_aspect_term
                            true_aspect_started = False
                            true_aspect_term=[]
                            true_added = True
                        if info[4] == 'O' and predicted_added==False:
                            temp_predicted_aspect_term=predict_aspect_term
                            predict_aspect_term=[]
                            predict_aspect_started = False
                            predicted_added= True
                            
    
                    if true_added==True and predicted_added == True and both_predictions==True:
                        
                        true_aspects.append(temp_true_aspect_term)
                        predicted_aspects.append(temp_predicted_aspect_term)
                        
                        temp_true_aspect_term =[]
                        temp_predicted_aspect_term = []
                        true_added = False
                        predicted_added = False
                        both_predictions = False
                        
    
            if len(info) == 2:
                if len(predicted_aspects)!=0 or len(true_aspects)!=0:

                    sent_true_aspects=[]
                    sent_predicted_aspects=[]

                    for t_aspect in true_aspects:
                        str_t_aspect = ' '.join(t_aspect)
                        sent_true_aspects.append(str_t_aspect.lower().strip())

                    for p_aspect in predicted_aspects:
                        str_p_aspect = ' '.join(p_aspect)
                        sent_predicted_aspects.append(str_p_aspect.lower().strip())
                    
                    if len(true_aspects)!=0 :

                        for i in range(0,len(true_aspects)):
                            t_aspect = true_aspects[i]
                            str_true_aspect = ' '.join(t_aspect)

                            self.CRF_true_aspects_list.append(str_true_aspect.lower().strip())

                    if len(predicted_aspects)!=0 :

                        for i in range(0,len(predicted_aspects)):
                            p_aspect = predicted_aspects[i]
                            str_predicted_aspect = ' '.join(p_aspect)

                            self.predicted_aspects_list.append(str_predicted_aspect.lower().strip())

                    tp,fp,fn,tp_aspects_exact = self.Perform_Evaluation_Token_based(sent_true_aspects,sent_predicted_aspects)
                    tp_p,fp_p,fn_p,tp_aspects_partial  =  self.Perform_Evaluation_Token_based_Partial(sent_true_aspects,sent_predicted_aspects)

                    tp_partials = tp_partials + tp_p
                    fp_partials = fp_partials + fp_p
                    fn_partials = fn_partials + fn_p

                    true_predictions = true_predictions + tp
                    false_predictions = false_predictions + fp
                    false_negatives = false_negatives + fn
                    
                    all_tp_aspects_exact.extend(tp_aspects_exact)
                    all_tp_aspects_partial.extend(tp_aspects_partial)
                    
                    start = False
                    begin = True

        # exact and partial precision
        
        self.CRF_true_aspects_list = [aspect for aspect in self.CRF_true_aspects_list if aspect!='']
        self.predicted_aspects_list = [aspect for aspect in self.predicted_aspects_list if aspect!='']
        
        
        tp_type_exact,fp_type_exact,fn_type_exact,precision_type_exact,recall_type_exact,fscore_type_exact,tp_aspects_type_exact = self.EvaluateAspects_type_based(self.CRF_true_aspects_list,self.predicted_aspects_list)       
        tp_type_partial,fp_type_partial,fn_type_partial,precision_type_partial,recall_type_partial,fscore_type_partial,tp_aspects_type_partial = self.EvaluateAspects_type_based_partial(self.CRF_true_aspects_list,self.predicted_aspects_list)       
        
        #print(tp_aspects_type_partial)
        
#         print("TYPE_BASED_EVALAUTION...............")
        evaluation_type_exact = {'TP' : tp_type_exact,'FP' : fp_type_exact, 'FN':fn_type_exact,'precision' : '%.3f' % precision_type_exact ,'recall' : '%.3f' % recall_type_exact,'fscore' : '%.3f' % fscore_type_exact}
#         print(evaluation_type_exact)
#         print("##########################")
        
#         print("TYPE_BASED_EVALAUTION (PARTIAL)...............")
        evaluation_type_partial = {'TP' : tp_type_partial,'FP' : fp_type_partial, 'FN':fn_type_partial,'precision' : '%.3f' % precision_type_partial ,'recall' : '%.3f' % recall_type_partial,'fscore' : '%.3f' % fscore_type_partial}
#         print(evaluation_type_partial)
#         print("##########################")
        
        try:
            precision_partial = tp_partials/(tp_partials + fp_partials)
        except ZeroDivisionError as err:
            precision_partial = 0
            
        try:
            precision_exact = true_predictions/(true_predictions + false_predictions)
        except ZeroDivisionError as err:
            precision_exact = 0
        
        try:
            precision_partial = tp_partials/(tp_partials + fp_partials)
        except ZeroDivisionError as err:
            precision_partial = 0
        
        # exact and partial recall
        
        try:
            recall_exact = true_predictions/(true_predictions + false_negatives)
        except ZeroDivisionError as err:
            recall_exact = 0
        
        try:
            recall_partial = tp_partials/(tp_partials + fn_partials)
        except ZeroDivisionError as err:
            recall_partial = 0
        
        # exact and partial fscore
        
        try:
            fscore_exact = 2*((precision_exact*recall_exact)/(precision_exact+recall_exact))
        except ZeroDivisionError as err:
            fscore_exact = 0
        
        try:
            fscore_partial = 2*((precision_partial*recall_partial)/(precision_partial+recall_partial))
        except ZeroDivisionError as err:
            fscore_partial = 0
        
        
        evaluation_exact = {'TP' : true_predictions,'FP' : false_predictions, 'FN':false_negatives,'precision' : '%.3f' % precision_exact ,'recall' : '%.3f' % recall_exact,'fscore' : '%.3f' % fscore_exact}
        evaluation_partial = {'TP' : tp_partials,'FP' : fp_partials, 'FN':fn_partials,'precision' : '%.3f' % precision_partial ,'recall' :  '%.3f' % recall_partial,'fscore' :  '%.3f' % fscore_partial}
        
#         print("Token BASED EVALUATION...............")
#         print(evaluation_exact)
#         print("##########################")
        
#         print("TOKEN BASED EVALUATION (PARTIAL)..............")
#         print(evaluation_partial)
#         print("##########################")
        
        return (evaluation_exact,evaluation_partial,evaluation_type_exact,evaluation_type_partial,all_tp_aspects_exact)


# In[4]:

def AspectTermLengthDistribution(aspect_list,aspect_status,appCategory):
    sizes = [len(w.split()) for w in aspect_list]

    size_distribution = Counter(sizes)

    aspect_words_freq = sorted(size_distribution.items(), key=operator.itemgetter(1),reverse=True)

    filepath= appCategory + "/" +  appCategory + "_" +  aspect_status +  "_aspect_words_freq.csv"

    with open(filepath, 'w') as csvfile:
        fieldnames = ['aspect_words',"frequency"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for key,value in aspect_words_freq:
            key = key
            value = '%d' % (value)
            writer.writerow({'aspect_words': key,'frequency':value})

    print("Aspects words by frquency in %s have been saved sucessfully!!!" % (appCategory))
        
    
def AspectFreqDistribution(aspect_list,aspect_status,appCategory):
        
    stemmer = SnowballStemmer("english")
    true_aspects=[]

    for aspect_term in aspect_list:
        AspectTermWords = aspect_term.lower().strip().split()
        AspectTermWords = [stemmer.stem(w) for w in AspectTermWords]
        AspectTerm_stemmed = ' '.join(AspectTermWords)
        true_aspects.append(AspectTerm_stemmed)

    freqDist=Counter(true_aspects)
    aspects_ranked_by_freq = sorted(freqDist.items(), key=operator.itemgetter(1),reverse=True)

    filepath= appCategory + "/" + appCategory + "_"  + aspect_status +  "_ranked_aspects.csv"

    with open(filepath, 'w') as csvfile:
        fieldnames = ['aspect_term',"frequency"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for key,value in aspects_ranked_by_freq:
            key = key
            value = '%d' % (value)
            writer.writerow({'aspect_term': key,'frequency':value})

    print("Aspects terms in %s are ranked by frquency have been saved sucessfully!!!" % (appCategory))


# In[5]:

if __name__ == "__main__":
    
    #for appCategory in ENGLISH_APPS_CATEGORY:
        #print("App Category -> %s" % (appCategory.name))
        # maintain list of exact token-based evaluation
    lst_precision_exact_token,lst_recall_exact_token,lst_fscore_exact_token =[],[],[]
    # maintain list of partial token-based evaluation
    lst_precision_partial_token,lst_recall_partial_token,lst_fscore_partial_token=[],[],[]
    # maintain list of exact type-based evaluation
    lst_precision_exact_type,lst_recall_exact_type,lst_fscore_exact_type=[],[],[]
    # maintain list of partial type-based evaluation
    lst_precision_partial_type,lst_recall_partial_type,lst_fscore_partial_type=[],[],[]

    # maintain list of token and type-based evaluation (In Train)
    lst_precision_inTrain_Token,lst_recall_inTrain_Token,lst_fscore_inTrain_Token=[],[],[]
    lst_precision_inTrain_Type,lst_recall_inTrain_Type,lst_fscore_inTrain_Type=[],[],[]

    # maintain list of token and type-based evaluation (Out of Train)
    lst_precision_outTrain_Token,lst_recall_outTrain_Token,lst_fscore_outTrain_Token=[],[],[]
    lst_precision_outTrain_Type,lst_recall_outTrain_Type,lst_fscore_outTrain_Type=[],[],[]
    
    for fold in range(0,10):
        Test_dataset= "cv-data" + "/" + "combine" + str(fold) + ".tsv"
        Train_dataset= "cv-data""/" + "train" + str(fold) + ".tsv"

        evaluation = CRFBIOTagEvaluation(Test_dataset,Train_dataset)
        token_exact,token_partial,type_exact,type_partial,tp_aspects_exact = evaluation.PerformEvaluation()

        #exact token-based evaluation
        lst_precision_exact_token.append(float(token_exact['precision']))
        lst_recall_exact_token.append(float(token_exact['recall']))
        lst_fscore_exact_token.append(float(token_exact['fscore']))

        #partial token-based evaluation
        lst_precision_partial_token.append(float(token_partial['precision']))
        lst_recall_partial_token.append(float(token_partial['recall']))
        lst_fscore_partial_token.append(float(token_partial['fscore']))

        #exact type-based evaluation
        lst_precision_exact_type.append(float(type_exact['precision']))
        lst_recall_exact_type.append(float(type_exact['recall']))
        lst_fscore_exact_type.append(float(type_exact['fscore']))

        #partial type-based evaluation
        lst_precision_partial_type.append(float(type_partial['precision']))
        lst_recall_partial_type.append(float(type_partial['recall']))
        lst_fscore_partial_type.append(float(type_partial['fscore']))

        evaluation.GetAspectTermsInTrainSet()
        InTrain_evaluation_token_exact,InTrain_evaluation_type_exact,OutTrain_evaluation_token_exact,OutTrain_evaluation_type_exact=evaluation.In_Out_Train_AspectTerms_Evaluation()

        #exact token-based evaluation (in Train)
        lst_precision_inTrain_Token.append(float(InTrain_evaluation_token_exact['precision']))
        lst_recall_inTrain_Token.append(float(InTrain_evaluation_token_exact['recall']))
        lst_fscore_inTrain_Token.append(float(InTrain_evaluation_token_exact['fscore']))

        #type token-based evaluation (in Train)
        lst_precision_inTrain_Type.append(float(InTrain_evaluation_type_exact['precision']))
        lst_recall_inTrain_Type.append(float(InTrain_evaluation_type_exact['recall']))
        lst_fscore_inTrain_Type.append(float(InTrain_evaluation_type_exact['fscore']))

        #exact token-based evaluation (Out of train)
        lst_precision_outTrain_Token.append(float(OutTrain_evaluation_token_exact['precision']))
        lst_recall_outTrain_Token.append(float(OutTrain_evaluation_token_exact['recall']))
        lst_fscore_outTrain_Token.append(float(OutTrain_evaluation_token_exact['fscore']))

        #type token-based evaluation (Out of train)
        lst_precision_outTrain_Type.append(float(OutTrain_evaluation_type_exact['precision']))
        lst_recall_outTrain_Type.append(float(OutTrain_evaluation_type_exact['recall']))
        lst_fscore_outTrain_Type.append(float(OutTrain_evaluation_type_exact['fscore']))

    print("#########Token-based Evaluation (Exact)################")
    avg_precision_exact_token = np.mean(lst_precision_exact_token)
    avg_recall_exact_token = np.mean(lst_recall_exact_token)
    avg_fscore_exact_token = 2*((avg_precision_exact_token*avg_recall_exact_token)/(avg_precision_exact_token+avg_recall_exact_token))
    print('Precision = %.3f, Recall = %.3f, FScore = %.3f'% (avg_precision_exact_token,avg_recall_exact_token,avg_fscore_exact_token))
    print("")

    print("#########Token-based Evaluation (Partial)################")
    avg_precision_partial_token = np.mean(lst_precision_partial_token)
    avg_recall_partial_token = np.mean(lst_recall_partial_token)
    avg_fscore_partial_token = 2*((avg_precision_partial_token*avg_recall_partial_token)/(avg_precision_partial_token+avg_recall_partial_token))
    print('Precision = %.3f, Recall = %.3f, FScore = %.3f'% (avg_precision_partial_token,avg_recall_partial_token,avg_fscore_partial_token))
    print("")

    print("#########Type-based Evaluation (Exact)################")
    avg_precision_exact_type = np.mean(lst_precision_exact_type)
    avg_recall_exact_type = np.mean(lst_recall_exact_type)
    avg_fscore_exact_type = 2*((avg_precision_exact_type*avg_recall_exact_type)/(avg_precision_exact_type+avg_recall_exact_type))
    print('Precision = %.3f, Recall = %.3f, FScore = %.3f'% (avg_precision_exact_type,avg_recall_exact_type,avg_fscore_exact_type))
    print("")

    print("#########Type-based Evaluation (Partial)################")
    avg_precision_partial_type = np.mean(lst_precision_partial_type)
    avg_recall_partial_type = np.mean(lst_recall_partial_type)
    avg_fscore_partial_type = 2*((avg_precision_partial_type*avg_recall_partial_type)/(avg_precision_partial_type+avg_recall_partial_type))
    print('Precision = %.3f, Recall = %.3f, FScore = %.3f'% (avg_precision_partial_type,avg_recall_partial_type,avg_fscore_partial_type))
    print("")

