## Source
https://bitbucket.org/faizalishah/appfeature_extraction/downloads/

###The package contains the source code of the following two studies: 
- Evaluating the performance of rule-based approach SAFE on different app review datasets for extracting app features from app reviews. 
- Simulating the impact of annotated data and annotation guidelines on supervised learning model performance when extracting app features from user reviews

---

## Prerequisite

To run the scripts, following tools and review datasets need to be downloaded:

1. Install python 3.5, and run the command ''' pip install requirements.txt''' to install the necessary python packages.u
2. Install the tool **CRFsuite**, please refer to http://www.chokkan.org/software/crfsuite/
3. Download annotated app reviews in German called **SANGER** from http://www.romanklinger.de/scare/ and put them in the folder Proprocessing_Scrpts/SANGER_ANNOTATED_REVIEW DATA/. 
4. Download annotated app reviews in English called **GUZMAN** from https://www.dropbox.com/s/xu0w0tcuq6xgezc/user_feedback_public.sql?dl=0 and put them in the folder Proprocessing_Scrpts/GUZMAN_ANNOTATED_REVIEW DATA/
5. Download datasets (**LAPTOPS** and **RESTAURANT**) from SemEval-2014 Task 4: http://alt.qcri.org/semeval2014/task4/index.php?id=data-and-tools and put in the evaluation folder.
6. Download SENNA Embeddings available at http://ronan.collobert.com/senna/ and put in the embeddings folder.
7. Download Wikipedia Embeddings for German language available at http://ronan.collobert.com/senna/ and put in the embeddings folder.
---

## Step 1: Convert all app review datasets into SemEval format 

- Use the following commands to convert annotated app review dataset in .csv format (e.g., GUZMAN) to SemEval format (i.e., xml format)

	```
		cd Preprocessing_Scripts
	```

	```
		python Transform_review_dataset_to_SemEval_format.py --dataset=GUZMAN
	```

- Use the same python script for converting app reviews datasets **SHAH_I**, **SHAH_II**, and **SANGER** into SemEval format.

## Step 2: SAFE evaluation on different app review datasets

- Change directory to SAFE_Replication using the following command:


	```
		cd SAFE_Replication
	```

- Run the following python script to validate the SAFE performance on app description dataset used in the  original paper, place the annotated app description dataset in the folder APP_DESCRIPTION :

	```
		python Extract_AppFeatures_SAFE.py --source=app_description 
	```

- Put the annotated review datasets in the folder USER_REVIEWS, and then using the same python script but by setting the --source to "user_reviews" and --dataset to one of the annotated review dataset (**GUZMAN**, **SHAH_I**, **SHAH**, **LAPTOP**, and **RESTAURANT**), you can see SAFE performance on that user review dataset. For example, the following command evaluates SAFE performance on **SHAH_I** annotated review datset.

	```
		python Extract_AppFeatures_SAFE.py --source=user_reviews --dataset=SHAH_I
	``` 

## Step 3: Simulating changes (Preprocessing, Simulation I, Simulation II, Simulation III-3) in app review annotations  

- For simulating the step "preprocessing" (step 0) on app review dataset (e.g., **SHAH_1**), execute the python script with the following arguments. 

	```
		python Modify_dataset.py --dataset=SHAH_I  --lang=en --step=0 
	```

- For simulating changes: Simulation I, Simulation II, and Simulation III-3, set argument --step to value 1, 2, and 3, respectively.

- Use the same python script to simulate changes in other English review datasets (i.e., **GUZMAN**, **SHAH_II**) or German review dataset (i.e., **SANGER**), but when performing the simulation steps on German review dataset **SANGER**, set argument --lang=de instead of --lang=en.
 
## Step 4: Evaluating the performance of CRF model performance on modified review datasets using the training procedures CCV, CCV-EXT, APPCAT, SCV, and SCV-EXT.

- Depending on after which simulation step and review dataset you want to evaluate the peformance of CRF model, copy the appropriate category-wise review dataset files generated under one of the folder (Processing, Simulation-I, Simulation II , or Simulation III-3) into the folder: AG_Imapct_Supervised_Leanring_Model/evaluation/.

- On command line, change directory to AG_Impact_Supervised_Learning_Model.
- To run **CCV** training procedure on the app reviews in English language. Execute the following bash script:

	```
		bash Evaluate_CRF_Model CCV en
	```

	if the review dataset is **SANGER** (i.e., German), first change the tagger and parser to German language in the java source code files under the Standford CoreNLP library folder -> main/java/edu/cuhk/hccl/NLP/

	``` 
		bash Evaluate_CRF_Model CCV de
	```

- In order to evaluate model performance with CCV-EXT, APPCAT, SCV, SCV-EXT training procedures, change the first parameter to CCV_EXT, APPCAT, SCV, SCV_EXT, accordingly. Depending on the review language, pass 'en' (for English) or 'de' (for German) as a second parameter to this script.


## Credit

1. We adopted the source code published by Liu et al. for the evaluation of CRF baseline on SemEval datasets at https://github.com/pdsujnow/opinion-target


