dataset=$1
type=$2

make prepare-folds dataset=${dataset}
mkdir -p cv-${dataset}
for fold in {0..9}
do
    cat cv-${dataset}/train${fold}.tsv | ./absa.py -s '\t' > cv-${dataset}/train${fold}.bin
    cat cv-${dataset}/test${fold}.tsv | ./absa.py -s '\t' > cv-${dataset}/test${fold}.bin
    cut -f 2- cv-${dataset}/train${fold}.bin > cv-${dataset}/train${fold}-bool.tmp
    cut -f 2- cv-${dataset}/test${fold}.bin > cv-${dataset}/test${fold}-bool.tmp
    paste cv-${dataset}/train${fold}.con cv-${dataset}/train${fold}-bool.tmp | sed 's/^\t$//g' > cv-${dataset}/train${fold}.bc
    paste cv-${dataset}/test${fold}.con cv-${dataset}/test${fold}-bool.tmp | sed 's/^\t$//g' >  cv-${dataset}/test${fold}.bc
    crfsuite learn -a l2sgd -p c2=2.0 -p feature.possible_transitions=1 -p feature.possible_states=1 -m cv-${dataset}/train${fold}-crfsuite.mdl cv-${dataset}/train${fold}.${type}
    crfsuite tag -r -m cv-${dataset}/train${fold}-crfsuite.mdl cv-${dataset}/test${fold}.${type} > cv-${dataset}/result${fold}.tsv
    paste cv-${dataset}/test${fold}.tsv cv-${dataset}/result${fold}.tsv > cv-${dataset}/combine${fold}.tsv
    cat cv-${dataset}/combine${fold}.tsv | cut -f1,2,4,5 | perl conlleval.pl -d "\t" > cv-${dataset}/crf_evaluation_test${fold}.txt
done





