from transformers import BertConfig, AutoTokenizer
from topicsentiment.model import BertForMultiLabel
import torch
import config
import pickle
import numpy as np
import os
import pandas as pd
import re

config = config.Settings()

# Load the model fro inference
model_config = BertConfig()
model = BertForMultiLabel(model_config)
model.load_state_dict(torch.load(os.path.join(config.MODEL_DIR, config.MODEL_NAME_COLAB), map_location=config.DEVICE))
tokenizer = AutoTokenizer.from_pretrained(config.PRE_TRAINED_MODEL)

with open(os.path.join(config.MODEL_DIR, 'label_encoder.pkl'), 'rb') as f:
    label_encoder = pickle.load(f)
    f.close()

def get_df_and_length(csvInput, columnToUsed):
    url='https://drive.google.com/uc?id=' + csvInput.split('/')[-2]
    df = pd.read_csv(url, usecols=columnToUsed)

    # preprocessing csv input 


    # decode all emoji characters
    # https://stackoverflow.com/a/57514515/2670476
    df = df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

    # Replace all non-letters with space
    df.content = df.apply(lambda row: " ".join(re.sub("[^a-zA-Z]+", " ", row.content).split()), 1)

    # remove all review with total characters less than 20 (such as only emoji)
    df = df[df.content.str.len()>=20]

    length = len(df)
    return df, length,

def get_input(df, row):
    inputText = df.iloc[row]
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
        # return {"prediction": label}
        return label
    except Exception as err:
        raise RuntimeError()

if __name__ == "__main__":
    df, length = get_df_and_length(csvInput = config.CSV_INPUT, columnToUsed = config.USE_COLS)
    print('length = ' + str(length))
    print('\n')
    # print(df)

    # df_result = pd.DataFrame(columns=['content', 'at', 'l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'l10'])
    # df_result = pd.DataFrame(columns=['content', 'at', 'labels'])
    df_result = pd.DataFrame(columns=['labels'])
    list_result = []

    for i in range(0,length+1):
        inputText = get_input(df.content, i)
        print(inputText)
        label = get_prediction(inputText)
        print('\n')
        print(label)
        
        list_result.append(label)
        # df_result = df_result.append
    
    print(list_result)

    df_list_result = pd.DataFrame(list_result)
    
    # df_result = df[0:3]
    df_result = pd.merge(df_result, df_list_result,  how='inner', left_index=True, right_index=True )

    print(df_list_result)
    print(df_result)

    # create csv output
    df_result.to_csv('test.csv', index=False)