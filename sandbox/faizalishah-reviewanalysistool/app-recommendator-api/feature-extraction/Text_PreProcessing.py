
# coding: utf-8

# In[1]:


import nltk
import re
from unidecode import unidecode


# In[2]:


class TextPreProcessing:
    def __init__(self,sent):
        self.sentence = sent
    
    def PreProcess(self):
        clean_sent = self.CleanReviewSentence(self.sentence)
        
        return clean_sent
    
    def CleanReviewSentence(self,review_sent):
        typos=[["im","i m","I m"],['Ill'],["cant","cnt"],["doesnt"],["dont"],["isnt"],["didnt"],["couldnt"],["Cud"],["wasnt"],["wont"],["wouldnt"],["ive"],["Ive"],["theres"]      ,["awsome", "awsum","awsm"],["Its"],["dis","diz"],["plzz","Plz ","plz","pls ","Pls","Pls "],[" U "," u "],["ur"],      ["b"],["r"],["nd ","n","&"],["bt"],["nt"],["coz","cuz"],["jus","jst"],["luv","Luv"],["gud"],["Gud"],["wel"],["gr8","Gr8","Grt","grt"],      ["Gr\\."],["pics"],["pic"],["hav"],["nic"],["nyc ","9ce"],["Nic"],["agn"],["thx","tks","thanx"],["Thx"],["thkq"],      ["Xcellent"],["vry"],["Vry"],["fav","favo"],["soo","sooo","soooo"],["ap"],["b4"],["ez"],["w8"],["msg"],["alot"],["lota"],["kinda"],["omg"],["gota"]]
        replace=["I'm","i will","can't","doesn't","don't","isn't","didn't","couldn't","Could","wasn't","won't","wouldn't","I have","I have","there's","awesome",             "It's","this","please","you","your","be","are","and","but","not","because","just","love","good","Good","well","great","Great\\.",             "pictures","picture","have","nice","nice","Nice","again","thanks","Thanks","thank you","excellent","very","Very","favorite","so","app","before","easy","wait","message","a lot","lot of","kind of","oh, my god","going to"]

        review_text = unidecode(review_sent)

        pattern1=r'[\?]{2,}'
        pattern2=r'[\.]{2,}'
        pattern3=r'[!]{2,}'
        regex1 = re.compile(pattern1)
        regex2 = re.compile(pattern2)
        regex3 = re.compile(pattern3)
        clean_review_sent = regex1.sub('?',review_sent)
        clean_review_sent = regex2.sub('.',clean_review_sent)
        clean_review_sent = regex3.sub('!',clean_review_sent)

        sentence = ' ' + clean_review_sent
        for i in range(0,len(typos)):
            list_typos = typos[i]
            correction = replace[i]
            for typo in list_typos:
                pattern1 = r"\s+" + typo + "(\s+|\.)"
                regex1 = re.compile(pattern1,re.IGNORECASE)
                line1 = regex1.sub(' ' + correction + ' ',sentence)
                sentence =  line1

        clean_review_sent = sentence.strip()

        return clean_review_sent

