import spacy
import re
import itertools
import pickle
import nltk
from Text_Preprocessing import TextProcessing
import Text_Preprocessing
import importlib
import requests
from langdetect import detect
import json

from enum import Enum
class EXTRACTION_MODE(Enum):
    APP_DESCRIPTION = 1
    USER_REVIEWS= 2


class SAFE_Patterns:
    def __init__(self,appName,sent_id,clean_sents,unclean_data):
        self.appName=appName
        self.sentid= sent_id
        self.clean_sentences = clean_sents
        self.unclean_sentences = unclean_data
    
    def ExtractFeatures_Analyzing_Sent_POSPatterns(self):
        raw_features_sent_patterns,remaining_sents,sent_with_features=self.Extract_AppFeatures_with_SentencePatterns()
        raw_features_pos_patterns,sents_features=self.Extract_AppFeatures_with_POSPatterns(sent_with_features)
        extracted_app_features = raw_features_sent_patterns + raw_features_pos_patterns
        
        return sents_features

    def SaveExtractedFeatures(self,extracted_features):
        file_path = self.appId.upper() + "_EXTRACTED_APP_FEATURES_"
        if self.extraction_mode.value == EXTRACTION_MODE.APP_DESCRIPTION.value:
            file_path = file_path + "DESC.pkl"
        elif self.extraction_mode.value == EXTRACTION_MODE.USER_REVIEWS.value:
            file_path = file_path + "REVIEWS.pkl"
        
        with open(file_path, 'wb') as fp:
            pickle.dump(extracted_features, fp)
    
    def Extract_Features_with_single_POSPattern(self,pattern_1,tag_text):
        match_list = re.finditer(pattern_1,tag_text)
        
        app_features=[]
            
        for match in match_list:
            app_feature = tag_text[match.start():match.end()]
            feature_words= [w.split("/")[0] for w in app_feature.split()]
            app_features.append(' '.join(feature_words))
        
        return(app_features)
    
    def Extract_AppFeatures_with_POSPatterns(self,sent_with_features):
        app_features_pos_patterns=[]
        
        pos_patterns=[r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 1
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)", # 2
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 3
                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # 4
                    r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 5
                    # r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN|VERB)", # 5 (old)
                    r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 6 
                     #r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN|ADJ|VERB)\s+[a-zA-Z-]+\/(NOUN)", # 6 (old)
                     r"[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/PRON\s+[a-zA-Z-]+\/(NOUN)", # 7 
                     #r"[a-zA-Z-]+\/(VERB|NOUN)\s+[a-zA-Z-]+\/PRON\s+[a-zA-Z-]+\/(NOUN)", # 7 (old)
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 8
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 9
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 10
                    r"[a-zA-Z-]+\/(NOUN)\s+(with|to)\/(ADP|PRT)\s+[a-zA-Z-]+\/(NOUN)", # 11  (restriction prepositions)
                    #r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # 11
                     #r"[a-zA-Z-]+\/(NOUN|ADJ)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # 11 (old)
                     r"[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/(DET)\s+[a-zA-Z-]+\/(NOUN)", # 12
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # 13
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 14
                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/ADJ", # 15
                    r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(PRON)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # 17
                    # r"[a-zA-Z-]+\/(VERB|NOUN)\s+[a-zA-Z-]+\/(PRON|DET)\s+[a-zA-Z-]+\/(ADJ|VERB|NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 17 (old)
                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(ADP)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # rule # 16 
                    #r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(ADP)\s+[a-zA-Z-]+\/(ADJ|NOUN)\s+[a-zA-Z-]+\/(NOUN)", # rule # 16 (old)
                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/DET\s+[a-zA-Z-]+\/(ADJ|NOUN)\s+[a-zA-Z-]+\/(NOUN)" # rule # 18  (RULE 18 IS REMOVED)
                     ]

        # list of all POS patterns
#         pos_patterns=[r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 1
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)", # 2
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 3
#                      r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(CONJ)\s+[a-zA-Z-]+\/(NOUN)", # 4
#                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 5
#                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 6 
#                      r"[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/PRON\s+[a-zA-Z-]+\/(NOUN)", # 7 
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 8
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 9
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # 10
#                     r"[a-zA-Z-]+\/(NOUN)\s+(with|to)\/(ADP|PRT)\s+[a-zA-Z-]+\/(NOUN)", # 11 
#                      r"[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/(DET)\s+[a-zA-Z-]+\/(NOUN)", # 12
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # 13
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # 14
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/ADJ", # 15
#                       r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(ADP)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # rule # 16 
#                     r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(PRON)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # 17                    
#                      r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/DET\s+[a-zA-Z-]+\/(ADJ|NOUN)\s+[a-zA-Z-]+\/(NOUN)" # rule # 18  
#                      ] ''
        
         # list of all POS patterns
#         pos_patterns=[r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # Rule 1 
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)", #  Rule 2
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", #  Rule 3
#                      r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # Rule 4 
#                     r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # Rule 5
#                     r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # Rule 6
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/PRON\s+[a-zA-Z-]+\/(NOUN)", # Rule 7
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # Rule 8
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # Rule 9
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)", # Rule 10
#                      r"[a-zA-Z-]+\/(NOUN)\s+(with|to)\/(ADP|PRT)\s+[a-zA-Z-]+\/(NOUN)", # Rule 11 
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(DET)\s+[a-zA-Z-]+\/(NOUN)", # Rule 12
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/ADP\s+[a-zA-Z-]+\/(NOUN)", # Rule 13
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)", # Rule 14
#                      r"[a-zA-Z-]+\/ADJ\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/ADJ", # Rule 15                    
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(ADP)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # Rule 16 
#                      r"[a-zA-Z-]+\/(VERB)\s+[a-zA-Z-]+\/(PRON)\s+[a-zA-Z-]+\/(ADJ)\s+[a-zA-Z-]+\/(NOUN)", # Rule 17
#                      r"[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/CONJ\s+[a-zA-Z-]+\/(NOUN)\s+[a-zA-Z-]+\/(NOUN)" # Rule 18 
#                      ]
            
        for sentence_id in sent_with_features.keys():
            sent_info = sent_with_features[sentence_id]
            sent = sent_info['clean_sent']
            
            if len(sent_info['extracted_features'])==0:
                extracted_features=[]
                sent_tokens= nltk.word_tokenize(sent)
                tag_tokens = nltk.pos_tag(sent_tokens,tagset='universal')
                tag_text = ' '.join([word.lower() + "/" + tag for word,tag in tag_tokens])
          
                # extract app features through by iterating through list of all POS_patterns
                rule_counter=1
                for pattern in pos_patterns:
                    # store extracted features in list of app features
                    rule_name = 'POS_R%d' % (rule_counter)
                    raw_features = self.Extract_Features_with_single_POSPattern(pattern,tag_text)
                    if len(raw_features)!=0:
                        app_features_pos_patterns.extend(raw_features)
                        for extracted_feature in set(raw_features):
                            extracted_features.append((extracted_feature,rule_name))
                    
                    rule_counter = rule_counter + 1
                
                if len(extracted_features)>0:
                    sent_feature_info = sent_with_features[sentence_id]
                    sent_feature_info['extracted_features'] = list(set(extracted_features))
                    sent_with_features[sentence_id] = sent_feature_info
            
            
        return(app_features_pos_patterns,sent_with_features)
        
    
    def SentencePattern_Case1(self,tag_text):
        raw_features=[]
        regex_case1 = r"[a-zA-Z-]+\/(NOUN)(\s+,\/.)?\s+(and)\/CONJ\s+[a-zA-Z-]+\/(ADJ)(\s+[a-zA-Z-]+\/(NOUN))"
        match = re.search(regex_case1,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words= [w.split("/")[0] for w in matched_text.split() if w.split("/")[1] not in ['.','CONJ']]
            raw_features.append(words[0] + " " + ' '.join(words[2:]))
            raw_features.append(words[1] + " " + ' '.join(words[2:]))

        return(raw_features)
    
    def SentencePattern_Case2(self,tag_text):
        raw_features=[]
        
        #exact in the paper
        regex_case2 = r"[a-zA-Z-]+\/(ADJ|NOUN)(\s+[a-zA-Z-]+\/(NOUN)\s+,\/.)+(\s+[a-zA-Z-]+\/(NOUN))?\s+and\/CONJ\s+[a-zA-Z-]+\/(NOUN)"
        match=re.search(regex_case2,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]    
            words = matched_text.split()

            first_word = words[0].split("/")[0]
            last_word = words[len(words)-1].split("/")[0]

            enumeration_words = [w.split('/')[0] for index,w in enumerate(matched_text.split()) if index not in[0,len(words)-1] and w.split("/")[1] not in ['.','CONJ','PRON']]
            raw_features.append(first_word + " " + last_word)

            raw_features += [first_word + " " + w2 for w2 in enumeration_words]

        return(raw_features)
    
    def SentencePattern_Case3(self,tag_text):
        raw_features=[]
        regex_case3 = r"[a-zA-Z-]+\/(VERB|NOUN)\s+and\/CONJ\s+[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/(NOUN|VERB)\s+and\/CONJ\s+[a-zA-Z-]+\/(NOUN|VERB)"
        match = re.search(regex_case3,tag_text)
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words = matched_text.split()
            words = [w.split("/")[0] for w in words]
            l1 = [words[0],words[2]]
            l2 = [words[3],words[5]]
            list_raw_features =list(itertools.product(l1,l2))
            raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
            
        return(raw_features)
    
    def SentencePattern_Case4(self,tag_text):
        raw_features=[]
        regex_case4 = r"[a-zA-Z-]+\/(VERB|NOUN|ADJ)\s+and\/CONJ\s+[a-zA-Z-]+\/(VERB|NOUN|ADJ)\s+[a-zA-Z-]+\/ADP((\s+[a-zA-Z-]+\/(NOUN|VERB))(\s+[a-zA-Z-]+\/(ADP)))?\s+[a-zA-Z-]+\/(NOUN|VERB)"
        regex_case4 += "(\s+,\/.)?\s+(including\/[a-zA-Z-]+)((\s+[a-zA-Z-]+\/(VERB|NOUN))+\s+,\/.)+\s+[a-zA-Z-]+\/(NOUN|VERB)\s+(and\/CONJ)\s+[a-zA-Z-]+\/(NOUN|VERB)"

        match=re.search(regex_case4,tag_text)
    
        if match!=None:
            matched_text= tag_text[match.start():match.end()]
            words = matched_text.split()
            words = [w.split("/")[0] for w in words]

            #words attach with first conjunction
            feature_word1 = words[0]
            feature_word2 = words[2]

            feature_list1=[words[0],words[2]]

            #feature words attach with second conjection
            count=0
            feature_list2=[]
            fwords=[]
            for i in range(3,len(words)):
                if i<len(words)-1:
                    if words[i+1]=="," and count==0:
                        feature_list2.append(words[i])
                        count = count + 1
                    elif count==1:
                        if words[i]!="including" and words[i]!=',':
                            fwords.append(words[i])
                        if words[i] == ","  : 
                            if len(fwords)>0:
                                feature_list2.append(' '.join(fwords))
                            fwords=[]


            feature_list2.append(words[len(words)-1])
            feature_list2.append(words[len(words)-3])

            list_raw_features = list(itertools.product(feature_list1,feature_list2))

            raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
            
        return(raw_features)
    
    def SentencePattern_Case5(self,tag_text):
        raw_features=[]
        regex_case5 = r"[a-zA-Z-]+\/(VERB|NOUN|ADP)\s+,\/.\s+[a-zA-Z-]+\/(VERB|NOUN)\s+and\/CONJ\s+[a-zA-Z]+\/(VERB|NOUN|ADJ)\s+[a-zA-Z-]+\/(NOUN|VERB|ADJ)\s+(as\/ADP)\s+"
        regex_case5 += "[a-zA-Z-]+\/(ADJ|NOUN|VERB)(\s+[a-zA-Z-]+\/(NOUN|VERB)\s+,\/.)+\s+[a-zA-Z-]+\/(NOUN|VERB)\s+(and\/CONJ)"
        regex_case5 += "\s+[a-zA-Z-]+\/(NOUN|VERB)\s+[a-zA-Z-]+\/(NOUN|VERB)"
        match=re.search(regex_case5,tag_text)    
        if match!=None:
            match_text=tag_text[match.start():match.end()]
            words_with_tags = match_text.split()
            words = [w.split("/")[0] for w in words_with_tags]

            feature_list1=[words[0],words[2]]
            feature_list2=[words[4] + " "  + words[5],words[7] + " " + words[8]]
            feature_list3=[words[10],words[12],words[14] + " " + words[15]]
            list_raw_features=list(itertools.product(feature_list1,feature_list3))
            raw_features= [feature_words[0] + " " + feature_words[1] for feature_words in list_raw_features]
            raw_features = raw_features + feature_list2
        
        return(raw_features)
    
    def Extract_AppFeatures_with_SentencePatterns(self):
        raw_app_features_sent_patterns=[]
        clean_sents_wo_sent_patterns=[]
        sents_with_extracted_features={}
        
        sent_id=0
        
        for sent_index in range(0,len(self.clean_sentences)):
            sent = self.clean_sentences[sent_index]
            sent_features=[]
            try:
                sent_text = self.unclean_sentences[sent_index]
            except KeyError as ex:
                print(sent_id)
                
            
            sent_tokens= nltk.word_tokenize(sent)
            tag_tokens = nltk.pos_tag(sent_tokens,tagset='universal')
            tag_text = ' '.join([word.lower()  + "/" + tag for word,tag in tag_tokens])
            
            sent_pattern_found=False
    
            raw_features_case1 = self.SentencePattern_Case1(tag_text)

            if len(raw_features_case1)!=0:
                raw_app_features_sent_patterns.extend(raw_features_case1)
                
                for i in range(0,len(raw_features_case1)):
                    extracted_feature = raw_features_case1[i]
                    rule = 'SS_R1'
                    sent_features.append((extracted_feature,rule))

                sent_pattern_found=True
            
            raw_features_case2 = self.SentencePattern_Case2(tag_text)
            
            if len(raw_features_case2)!=0:
                raw_app_features_sent_patterns.extend(raw_features_case2)
                
                for i in range(0,len(raw_features_case2)):
                    extracted_feature = raw_features_case2[i]
                    rule = 'SS_R2'
                    sent_features.append((extracted_feature,rule))
                
                sent_pattern_found=True
            #case 3
            
            raw_features_case3 = self.SentencePattern_Case3(tag_text)
            if len(raw_features_case3)!=0:
                raw_app_features_sent_patterns.extend(raw_features_case3)
                
                for i in range(0,len(raw_features_case3)):
                    extracted_feature = raw_features_case3[i]
                    rule = 'SS_R3'
                    sent_features.append((extracted_feature,rule))
                
                sent_pattern_found=True
            
            raw_features_case4 = self.SentencePattern_Case4(tag_text)
            if len(raw_features_case4)!=0:                
                raw_app_features_sent_patterns.extend(raw_features_case4)
                sent_features.extend(raw_features_case4)
                
                for i in range(0,len(raw_features_case4)):
                    extracted_feature = raw_features_case4[i]
                    rule = 'SS_R4'
                    sent_features.append((extracted_feature,rule))

                sent_pattern_found=True

                
            raw_features_case5 = self.SentencePattern_Case5(tag_text)
            if len(raw_features_case5)!=0:
                raw_app_features_sent_patterns.extend(raw_features_case5)
                
                for i in range(0,len(raw_features_case5)):
                    extracted_feature = raw_features_case5[i]
                    rule = 'SS_R5'
                    sent_features.append((extracted_feature,rule))
                
                sent_pattern_found=True
            
            if sent_pattern_found==False:
                clean_sents_wo_sent_patterns.append(sent)
            
            sents_with_extracted_features[sent_index]={'sentence_text' : sent_text,'clean_sent':sent,'extracted_features':sent_features}
    
        
        return(raw_app_features_sent_patterns,clean_sents_wo_sent_patterns,sents_with_extracted_features)

