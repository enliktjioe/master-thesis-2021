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



df_cabify = pd.read_csv(config['csv_input_local']['cabify_apple_google_p1'], index_col=0)
df_cabify = df_cabify.reset_index(drop=True)
total_reviews = len(df_cabify)

print(f'Total English reviews: {total_reviews} \n')
df_cabify.review = df_cabify.review.astype(str)

# df_cabify = df_cabify.head(10) # testing purpose
listOfSentimentScores = []

for i in range(0, int(len(df_cabify))):
    text_input = df_cabify.review[i]
    star_rating = df_cabify.rating[i]
    result = senti.getSentiment(text_input)
    # print(result)
    
    # https://www.kite.com/python/answers/how-to-convert-a-list-of-integers-into-a-single-integer-in-python
    strings = [str(integer) for integer in result]
    a_string = "".join(strings)
    result_int = int(a_string)
    
    listOfSentimentScores.append(result_int)

    print('index = ' + str(i))
    # print('result_int = ' + str(result_int))
    # print(listOfSentimentScores)
    
    
df_cabify['sentiment_score'] = listOfSentimentScores
print(df_cabify)
df_cabify.to_csv(config['csv_input_local']['cabify_apple_google_p1_sentiment'])