###To evaluate the performance of MaxEnt and CNN models on Gu's dataset from command line

Install requirements 

	pip install -r requirements.txt

To see the performance of MaxEnt models, change project directory using the following command:

```
cd MaxEnt_Models
```

Run the following command to evaluate the performance of MaxEnt model using only unigram features:

```
python BoW_UNIGRAM_EVAL.py
```

Run the following command to evaluate the performance of MaxEnt model using 1 to 3 word gram features:

```
python Bow_TRIGRAM_EVAL.py
```

Perform the following steps to evaluate the performance of MaxEnt model using 2 to 4 char grams and linguistic features, as used in the study of Gu et al.:

-  Run the standford CoreNLP Server using the following command:

	```
	java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 
	```

- Run the following python script to extract char grams (i.e, 2 to 4) features and linguistic features

	```
	python Extract_BoC_n_LINGUISTIC_Features.py
	```

- Run the following python script to evaluate the peformance of MaxEnt model using both char grams and linguistic features.

	```
	python BoC_n_LINGUISTIC_EVAL.py
	```


To see the performance of CNN models (i.e., random, static, and non-static), change project directory using the following command:

```
cd ..
cd CNN_Models
```

Run the following command to evaluate the performance of CNN model initializing the embeddings randomly:

```
python CNN_RAND_EVAL.py
```

To evaluate the performance of CNN model with static and non-static word embeddings:

- Download the pre-trained Google News embeddings (i.e., GoogleNews-vectors-negative300.bin) and placed them at the root of the project.

- Run the following python script to evaluate the CNN model with static word embeddings.

	```
	python CNN_STATIC_EVAL.py
	```

- Run the following python script to evaluate the CNN model with non-static word embeddings.

	```
	python CNN_NON_STATIC_EVAL.py
	```
