#!/bin/bash

evaluation=$1
lang=$2

python Generate_train_test_dataset.py $evaluation $lang

if [ $evaluation == "CCV" ] ;
then
	echo "Evaluating CRF model using CCV training procedure..."
	bash CCV.sh $lang
	python CCV_Token_Type_Eval_Results.py $lang
fi

if [ $evaluation == "CCV_EXT" ] ;
then
	echo "Evaluating CRF model using CCV-EXT training procedure..."
	bash CCV.sh $lang
	python CCV_Token_Type_Eval_Results.py $lang
fi

if [ $evaluation == "APPCAT" ] ;
then
	echo "Evaluating CRF model using AppCat training procedure..."
	bash AppCat_Eval.sh $lang
	python AppCat_Token_Type_Eval_Results.py $lang
fi

if [ $evaluation == "SCV" ] ;
then
	echo "Evaluating CRF model using SCV training procedure..."
	bash SCV_Annotate.sh $lang
	python Perform_10_fold_stratified_sampling.py $evaluation
	bash cv-batch_crf_v1.sh bc
	python SCV_Token_Type_Eval_Results.py $lang
fi

if [ $evaluation == "SCV_EXT" ] ;
then
	echo "Evaluating CRF model using SCV EXT training procedure..."
	bash SCV_EXT_Annotate.sh $lang
	python Perform_10_fold_stratified_sampling.py $evaluation
	bash cv-batch_crf_v1.sh bc
	python SCV_Token_Type_Eval_Results.py $lang
fi


