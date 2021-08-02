from utils import *
import pandas as pd

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')

from sentistrength import PySentiStr
senti = PySentiStr()

# Rocket HPC
senti.setSentiStrengthPath('/gpfs/space/home/enlik/GitRepo/master-thesis-2021/references/SentiStrengthCom.jar') # Note: Provide absolute path instead of relative path
senti.setSentiStrengthLanguageFolderPath('/gpfs/space/home/enlik/GitRepo/master-thesis-2021/references/SentiStrengthData/') # Note: Provide absolute path instead of relative path



df_freenow = pd.read_csv(config['csv_input_local']['freenow_apple_google_p1'], index_col=0)
df_freenow = df_freenow.reset_index(drop=True)
total_reviews = len(df_freenow)

print(f'Total English reviews: {total_reviews} \n')
df_freenow.review = df_freenow.review.astype(str)

# df_freenow = df_freenow.head(10) # testing purpose
listOfSentimentScores = []

for i in range(0, int(len(df_freenow))):
    text_input = df_freenow.review[i]
    star_rating = df_freenow.rating[i]
    result = senti.getSentiment(text_input)
    # print(result)
    
    # https://www.kite.com/python/answers/how-to-convert-a-list-of-integers-into-a-single-integer-in-python
    strings = [str(integer) for integer in result]
    a_string = "".join(strings)
    result_int = int(a_string)
    
    listOfSentimentScores.append(result_int)

    print(i)
    # print('index = ' + str(i))
    # print('result_int = ' + str(result_int))
    # print(listOfSentimentScores)
    
    
df_freenow['sentiment_score'] = listOfSentimentScores
print(df_freenow)
df_freenow.to_csv(config['csv_input_local']['freenow_apple_google_p1_sentiment'])