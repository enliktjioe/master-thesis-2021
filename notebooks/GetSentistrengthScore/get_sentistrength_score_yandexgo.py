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



df_yandexgo = pd.read_csv(config['csv_input_local']['yandexgo_apple_google_p1'], index_col=0)
df_yandexgo = df_yandexgo.reset_index(drop=True)
total_reviews = len(df_yandexgo)

print(f'Total English reviews: {total_reviews} \n')
df_yandexgo.review = df_yandexgo.review.astype(str)

# df_yandexgo = df_yandexgo.head(10) # testing purpose
listOfSentimentScores = []

for i in range(0, int(len(df_yandexgo))):
    text_input = df_yandexgo.review[i]
    star_rating = df_yandexgo.rating[i]
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
    
    
df_yandexgo['sentiment_score'] = listOfSentimentScores
print(df_yandexgo)
df_yandexgo.to_csv(config['csv_input_local']['yandexgo_apple_google_p1_sentiment'])