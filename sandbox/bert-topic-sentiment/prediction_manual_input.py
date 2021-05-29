from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import BertConfig, AutoTokenizer
from topicsentiment.model import BertForMultiLabel
import torch
import config
from typing import List
import pickle
import numpy as np
import os

config = config.Settings()

# Load the model fro inference
model_config = BertConfig()
model = BertForMultiLabel(model_config)
model.load_state_dict(torch.load(os.path.join(config.MODEL_DIR, config.MODEL_NAME_COLAB), map_location=config.DEVICE))
tokenizer = AutoTokenizer.from_pretrained(config.PRE_TRAINED_MODEL)

with open(os.path.join(config.MODEL_DIR, 'label_encoder.pkl'), 'rb') as f:
    label_encoder = pickle.load(f)
    f.close()

if __name__ == "__main__":
  # Encode the text to features
    encoded_text = tokenizer.encode_plus(
        "So annoyed with this app!! Definitely the worst of all of them. Sticking with Uber from now on. The driver arrival times are fake! It says the drivers have arrived when they are far away. Today the driver arrived and within a minute started driving away as if planning to do the route of my journey. I called customer support and was told that the driver was just around the corner of my house even though on the map it showed him miles away. Was told to look around the corner, which I did and the driver wasnâ€™t there. Customer support then contacted the driver who claims he waited for 6 minutes and customer support claims on their system it showed he waited for 6 minutes, which is funny because their system was showing that he was there even though he wasnâ€™t. With the time of me ordering the car, waiting the 2/3 minutes for him to get to me and my call to the driver and customer service there is no possible way the driver waiting 6 minutes. I even have the screenshots to prove it. Then customer support tells me Iâ€™ve not been charged and they are offering me Â£3 off the next journey. #%# %*^! This isnâ€™t the first time this has happened, the drivers do as they please! Stick with Uber, this app is trash! Deleting it immediately.",
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
    except Exception as err:
        raise HTTPException(status_code=666, detail="Error during prediction")
  
