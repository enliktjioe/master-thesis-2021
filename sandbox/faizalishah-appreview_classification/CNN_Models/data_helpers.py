import numpy as np
import re
import itertools
from collections import Counter
from os import listdir
from os.path import isfile, join
import pandas as pd
import operator
import csv
import nltk
from sklearn.model_selection import train_test_split


def clean_str(string):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    """
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

def LoadDataset(dataset_path):
    #dataset_path = "datasets/Gu"
        
    df_dataset= pd.DataFrame(columns=('class','sentence'))
        
    file_list = [f for f in listdir(dataset_path ) if isfile(join(dataset_path, f))]

    for file_path in file_list:
            # only one dataset
            #if file_path=="googlemap.csv":
        print(file_path)
        file_full_path = dataset_path + "/" + file_path
        df = pd.read_csv(file_full_path)
        class_type=[]
        for index, row in df.iterrows():
            if isinstance(row[1], str):
                clean_sent = CleanSentence(row[1])
                data_row= {'sentence': clean_sent, 'class': row[0]}    
                class_type.append(row[0])
        
            #print(Counter(class_type))
            #print('')
                
                df_dataset = df_dataset.append(data_row,ignore_index=True)  

    return df_dataset

def CleanSentence(sent):
    typos=[["im","i m","I m"],['Ill'],["cant","cnt"],["doesnt"],["dont"],["isnt"],["didnt"],["couldnt"],["Cud"],["wasnt"],["wont"],["wouldnt"],["ive"],["Ive"],["theres"]\
      ,["awsome", "awsum","awsm"],["Its"],["dis","diz"],["plzz","Plz ","plz","pls ","Pls","Pls "],[" U "," u "],["ur"],\
      ["b"],["r"],["nd ","n","&"],["bt"],["nt"],["coz","cuz"],["jus","jst"],["luv","Luv"],["gud"],["Gud"],["wel"],["gr8","Gr8","Grt","grt"],\
      ["Gr\\."],["pics"],["pic"],["hav"],["nic"],["nyc ","9ce"],["Nic"],["agn"],["thx","tks","thanx"],["Thx"],["thkq"],\
      ["Xcellent"],["vry"],["Vry"],["fav","favo"],["soo","sooo","soooo"],["ap"],["b4"],["ez"],["w8"],["msg"],["alot"],["lota"],["kinda"],["omg"],["gota"]]
    replacements=["I'm","i will","can't","doesn't","don't","isn't","didn't","couldn't","Could","wasn't","won't","wouldn't","I have","I have","there's","awesome",\
     "It's","this","please","you","your","be","are","and","but","not","because","just","love","good","Good","well","great","Great\\.",\
     "pictures","picture","have","nice","nice","Nice","again","thanks","Thanks","thank you","excellent","very","Very","favorite","so","app","before","easy","wait","message","a lot","lot of","kind of","oh, my god","going to"]


    sent_tokens = nltk.word_tokenize(sent)

    new_sent=""

    for i,token in enumerate(sent_tokens):
        found_type=False
        for index,lst in enumerate(typos):
            if token in lst:
                new_sent +=  replacements[index]
                if i<(len(sent_tokens)-1):
                    new_sent += " "
                    found_type=True
                    break

        if found_type == False:
            new_sent += token 
            if i<(len(sent_tokens)-1):
                new_sent += " "
        
    return(new_sent.strip())

def SplitDataIntoTrainTest(dataset_path):
    review_ds=LoadDataset(dataset_path)
    train, test = train_test_split(review_ds, test_size=0.2)
        
    X_TRAIN=[]
    TRAIN_LABELS = []
        
        #print("####APPS in Train-set########")
        
    for index,row in train.iterrows():
            #print(row['sentence'])
        if isinstance(row['sentence'], str):
            #sent_words = nltk.word_tokenize(row['sentence'])
            X_TRAIN.append(row['sentence'].strip().lower())
            TRAIN_LABELS.extend(row['class'])


    # ONE HOT ENCODING FOR Y LABEL IN THE TRAINING SET

    train_lables_fd = Counter(TRAIN_LABELS)
    #print(train_lables_fd)
    
    sorted_train_labels = sorted(train_lables_fd.items(), key=operator.itemgetter(1),reverse=True)
    train_label_names = [y for y, f in sorted_train_labels]
    
    train_labels_vocab = dict(zip(train_label_names, range(0, len(train_label_names))))
    #print(train_labels_vocab)
    Y_TRAIN=[]
    for y_train_label in TRAIN_LABELS:
        onehot = np.zeros(5)
        onehot[train_labels_vocab.get(y_train_label)] = 1
        Y_TRAIN.append(onehot)

        
#         print("# of examples in training-set are = %d" % (len(self.TRAIN_SENTENCES)))
#         print("Distribution of classes in training-set are ->")
#         print(Counter(self.TRAIN_LABELS))
        
        #self.BuildVocab(threshold=3)
        
    X_TEST=[]
    TEST_LABELS = []
        
#         print("")
#         print("#####Apps in Test-set#######")
    for index,row in test.iterrows():
        if isinstance(row['sentence'], str):
            #sent_words = nltk.word_tokenize(row['sentence'])
            X_TEST.append(row['sentence'].strip().lower())
            TEST_LABELS.extend(row['class'])

    # ONE HOT ENCODING FOR Y LABEL IN THE TEST SET

    Y_TEST=[]
    for y_test_label in TEST_LABELS:
        onehot = np.zeros(5)
        onehot[train_labels_vocab.get(y_test_label)] = 1
        Y_TEST.append(onehot)


    return(X_TRAIN,Y_TRAIN,X_TEST,Y_TEST)


def load_data_and_labels(dataset_path):
    """
    Loads MR polarity data from files, splits the data into words and generates labels.
    Returns split sentences and labels.
    """
    # Load data from files
    # What to do if the file is currently being edited by someone. A lock has been set on the file. So keep A backup that is swapped in and out.
    # file_list = [f for f in listdir(dataset_path ) if isfile(join(dataset_path, f))]
    class_type=[]
    review_sents=[]

    with open(dataset_path) as f_obj:
        reader = csv.reader(f_obj, delimiter=',')
        for line in reader:
            review_sents.append(line[0].strip())
            class_type.append(line[1])

    # for file_path in file_list:
    #         # only one dataset
    #     file_full_path = dataset_path + "/" + file_path
    #     df = pd.read_csv(file_full_path)

    #     for index, row in df.iterrows():
    #         #data_row= {'sentence': row[1], 'class': row[0]}    
    #         if isinstance(row[1], str):
    #             review_sents.append(row[1].strip())
    #             class_type.append(row[0])

    #Generate labels
    x_text = [clean_str(sent) for sent in review_sents]
    lables_fd = Counter(class_type)
    print(lables_fd)
    
    sorted_labels = sorted(lables_fd.items(), key=operator.itemgetter(1),reverse=True)
    label_names = [y for y, f in sorted_labels]
    
    labels_vocab = dict(zip(label_names, range(0, len(label_names))))
    print(labels_vocab)
    y=[]
    for y_label in class_type:
        onehot = np.zeros(5)
        onehot[labels_vocab.get(y_label)] = 1
        y.append(onehot)

    return [x_text, y]
   

def batch_iter(data, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    data = np.array(data)
    data_size = len(data)
    num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
    for epoch in range(num_epochs):
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            yield shuffled_data[start_index:end_index]
