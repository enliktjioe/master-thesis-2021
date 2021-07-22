## ktrain - Error - ValueError: model must be of instance Model

Happened when running
```
predictor = ktrain.load_predictor('bert_model')
```

Solution:
https://github.com/amaiya/ktrain/issues/21
Make sure you have TensorFlow 1.14. I had the same problem with different version of TensorFlow


## ktrain - Save/Load Predictor
https://github.com/amaiya/ktrain/issues?q=load+predictor
https://nbviewer.jupyter.org/github/amaiya/ktrain/blob/develop/examples/text/ArabicHotelReviews-BERT.ipynb

```
p = ktrain.get_predictor(learner.model, preproc)
p.predict("الغرفة كانت نظيفة ، الطعام ممتاز ، وأنا أحب المنظر من غرفتي.")

# save model for later use
p.save('/tmp/arabic_predictor')

# reload from disk
p = ktrain.load_predictor('/tmp/arabic_predictor')

# still works as expected after reloading from disk
p.predict("الغرفة كانت نظيفة ، الطعام ممتاز ، وأنا أحب المنظر من غرفتي.")
```