# AR_Miner

Our implementation of the text miner for app reviews. Please see the original paper [AR_Miner](http://dl.acm.org/citation.cfm?id=2568263). 

## Video Link : https://youtu.be/bHjNEZsD5As

## Getting Started

These python packages are required to run our project

### sklearn

```
pip install sklearn
```

### lda
```
pip install lda
```

### scipy
```
pip install scipy
```

### nltk
```
pip install nltk
```

### nltk.corpus

Go to your python interactive model, type:

```
>>>nltk.download('all')
```

for install the nltk corpus to import stopwords

## Run the project

Make sure to git clone the entire repo into your local directory and install the required packages.

### Notebook structure

The notebook is used as a demo/report for our project. We import the code into the notebook. 

The main code flow of our notebook includes : 

1) NLP Based Preprocessing; 
2) Naive Bayes/SVM Based Filtering; 
3) LDA topic clustering; 
4) Ranking algorithms for importance

### Dataset

There are four considered apps to try: 

```
facebook
```

```
templerun2
```

```
swiftkey
```

```
tapfish
```
