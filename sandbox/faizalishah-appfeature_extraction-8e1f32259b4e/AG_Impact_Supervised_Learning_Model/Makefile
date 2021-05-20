APP_TRAIN=evaluation/${dataset}/${dataset}_TRAIN.xml
APP_TEST=evaluation/${dataset}/${dataset}_TEST.xml


ifeq (${lang}, en)
	EMBEDDIING_FILE=embeddings/senna
	embed=senna
else
	ifeq (${lang}, de)
		EMBEDDIING_FILE=embeddings/wikipedia_de/embeddings
		embed=wikipedia_de
	endif
endif
###################################################################################################
## Experiments for Conditional Random Field
###################################################################################################
prepare-dataset:
	mvn -q compile exec:java -Dexec.mainClass=edu.cuhk.hccl.AppCreateCRFVectorFile -Dexec.args="evaluation/${dataset}/${dataset}_TEST.xml ${EMBEDDIING_FILE} ${embed} cross-validation/${dataset}.tsv cross-validation/${dataset}.con"
###################################################################################################
## Experiments for Recurrent Neural Network
###################################################################################################	
app-json:
	mvn -q compile exec:java -Dexec.mainClass=edu.cuhk.hccl.AppPrepareRnnDataset \
	-Dexec.args="-t ${APP_TRAIN} -r 0.9 -s ${APP_TEST} -o ${dataset}/${dataset}-json-${embed}.txt -e ${EMBEDDIING_FILE} -p ${embed}"
	

# Example: make run-rnn dataset=laptop embed=Senna type=lstmfeat window=3 nhidden=100 dimension=50 init=true
run-rnn:
	python main.py ${dataset}-json-${embed}.txt ${type} ${dataset}-${type}-${embed}-${window}-${nhidden}-${dimension} ${window} ${nhidden} ${dimension} ${init}

###################################################################################################
## Experiments for CRFsuite on Word Embeddings
###################################################################################################	
run-word2vec:
	cd word2vec; ./word2vec -train ${datafile} -output vectors-${size}.txt -cbow 0 -size ${size} -window 5 -negative 0 -hs 1 -sample 1e-3 -threads 12 -binary 0
	@echo "[INFO] word2vec is finished."

app-features:
	mvn -q compile exec:java -Dexec.mainClass=edu.cuhk.hccl.AppCreateCRFVectorFile -Dexec.args="${APP_TRAIN} ${EMBEDDIING_FILE} ${embed} ${dataset}/${dataset}-train.tsv ${dataset}/${dataset}-train.con"
	mvn -q compile exec:java -Dexec.mainClass=edu.cuhk.hccl.AppCreateCRFVectorFile -Dexec.args="${APP_TEST} ${EMBEDDIING_FILE} ${embed} ${dataset}/${dataset}-test.tsv ${dataset}/${dataset}-test.con"
	cat ${dataset}/${dataset}-train.tsv | ./absa.py -s '\t' ${dataset} > ${dataset}/${dataset}-train.bin
	cat ${dataset}/${dataset}-test.tsv | ./absa.py -s '\t' ${dataset} > ${dataset}/${dataset}-test.bin
	cut -f 2- ${dataset}/${dataset}-train.bin > ${dataset}/${dataset}-train-bool.tmp
	cut -f 2- ${dataset}/${dataset}-test.bin > ${dataset}/${dataset}-test-bool.tmp
	paste ${dataset}/${dataset}-train.con ${dataset}/${dataset}-train-bool.tmp | sed 's/^\t$///g' > ${dataset}/${dataset}-train.bc
	paste ${dataset}/${dataset}-test.con ${dataset}/${dataset}-test-bool.tmp | sed 's/^\t$///g' > ${dataset}/${dataset}-test.bc
	

#type=bin(binary) or con(continuous) or bc (binary-continuous)
run-crfsuite:
	#crfsuite learn -m ${dataset}-crfsuite.mdl ${dataset}-train.${type}
	crfsuite learn -a l2sgd -p c2=1 -p feature.possible_transitions=1 -p feature.possible_states=1 -m ${dataset}/${dataset}-crfsuite.mdl ${dataset}/${dataset}-train.${type}
	#crfsuite learn -a lbfgs -p c2=1 -p feature.possible_transitions=1 -p feature.possible_states=1 -m ${dataset}-crfsuite.mdl ${dataset}-train.${type}
	crfsuite tag -r -m ${dataset}/${dataset}-crfsuite.mdl ${dataset}/${dataset}-test.${type} > ${dataset}/${dataset}-result.tsv
	paste ${dataset}/${dataset}-test.tsv ${dataset}/${dataset}-result.tsv > ${dataset}/${dataset}-combine.tsv
	cat ${dataset}/${dataset}-combine.tsv | cut -f1,2,4,5 | perl conlleval.pl -d "\t" > ${dataset}/CRF_EVALUATION_${dataset}.txt

###################################################################################################
## Experiments for Cross Validation
###################################################################################################
prepare-folds:
	mvn -q compile exec:java -Dexec.mainClass=edu.cuhk.hccl.AppPrepareDataFolds \
	-Dexec.args="-f cross-validation/${dataset}.tsv -c cross-validation/${dataset}.con -n 10 -d cv-${dataset}"

# example: make prepare-json dataset=dse fold=0 embed=senna
prepare-json:
	mvn -q compile exec:java -Dexec.mainClass=edu.cuhk.hccl.AppPrepareRnnJson \
	-Dexec.args="-t ${dataset}/train${fold}.tsv -r 0.9 -s ${dataset}/test${fold}.tsv -o ${dataset}-json-${embed}.txt -e ${EMBEDDIING_FILE} -p ${embed}"	
    
