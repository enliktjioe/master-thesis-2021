type=$1
for fold in {0..9}
do
    cat cv-data/train${fold}.tsv | ./absa.py -s '\t' > cv-data/train${fold}.bin
    cat cv-data/test${fold}.tsv | ./absa.py -s '\t' > cv-data/test${fold}.bin
    cut -f 2- cv-data/train${fold}.bin > cv-data/train${fold}-bool.tmp
    cut -f 2- cv-data/test${fold}.bin > cv-data/test${fold}-bool.tmp
    paste cv-data/train${fold}.con cv-data/train${fold}-bool.tmp | sed 's/^\t$//g' > cv-data/train${fold}.bc
    paste cv-data/test${fold}.con cv-data/test${fold}-bool.tmp | sed 's/^\t$//g' >  cv-data/test${fold}.bc
    crfsuite learn -a l2sgd -p c2=2.0 -p feature.possible_transitions=1 -p feature.possible_states=1 -m cv-data/train${fold}-crfsuite.mdl cv-data/train${fold}.${type}
    crfsuite tag -r -m cv-data/train${fold}-crfsuite.mdl cv-data/test${fold}.${type} > cv-data/result${fold}.tsv
    paste cv-data/test${fold}.tsv cv-data/result${fold}.tsv > cv-data/combine${fold}.tsv
    cat cv-data/combine${fold}.tsv | cut -f1,2,4,5 | perl conlleval.pl -d "\t" > cv-data/crf_evaluation_test${fold}.txt
done





