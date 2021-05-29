from transformers import BertConfig, AutoTokenizer
from topicsentiment.model import BertForMultiLabel
import torch
import config
import pickle
import numpy as np
import os
import pandas as pd

config = config.Settings()

# Load the model fro inference
model_config = BertConfig()
model = BertForMultiLabel(model_config)
model.load_state_dict(torch.load(os.path.join(config.MODEL_DIR, config.MODEL_NAME_COLAB), map_location=config.DEVICE))
tokenizer = AutoTokenizer.from_pretrained(config.PRE_TRAINED_MODEL)

with open(os.path.join(config.MODEL_DIR, 'label_encoder.pkl'), 'rb') as f:
    label_encoder = pickle.load(f)
    f.close()

def get_input(csvInput):
    df = pd.read_csv(csvInput)
    df = df['review']
    # inputText = df[0]
    inputText = df.iloc[1]
    return inputText

def get_prediction(inputText):
    # Encode the text to features
    encoded_text = tokenizer.encode_plus(
        inputText,
        # max_length=req_body.max_len,
        max_length=64,
        add_special_tokens=True,
        return_token_type_ids=True,
        pad_to_max_length=True,
        return_attention_mask=True,
        truncation=True,
        return_tensors='pt',
    )

    try:
        # Generate the output and pass through sigmoid
        output = model(encoded_text["input_ids"], encoded_text["attention_mask"],
                       encoded_text["token_type_ids"]).sigmoid()

        # Filter out predictions less than the threshold
        # prediction = [1 if i > req_body.threshold else 0 for i in output[0]]
        prediction = [1 if i > 0.3 else 0 for i in output[0]]

        label = label_encoder.inverse_transform(np.array([prediction]))[0]

        print("prediction = ")
        print(label)
        return {"prediction": label}
    except Exception as err:
        raise RuntimeError()

if __name__ == "__main__":
    inputText = get_input(csvInput = config.CSV_INPUT)
    print(inputText)

    get_prediction(inputText)