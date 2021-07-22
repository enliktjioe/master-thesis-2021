## Error - ValueError: model must be of instance Model

Happened when running
```
predictor = ktrain.load_predictor('bert_model')
```

Solution:
https://github.com/amaiya/ktrain/issues/21
Make sure you have TensorFlow 1.14. I had the same problem with different version of TensorFlow