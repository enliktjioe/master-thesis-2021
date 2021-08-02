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



df_taxieu = pd.read_csv(config['csv_input_local']['taxieu_apple_google_p1'], index_col=0)
df_taxieu = df_taxieu.reset_index(drop=True)
total_reviews = len(df_taxieu)

print(f'Total English reviews: {total_reviews} \n')
df_taxieu.review = df_taxieu.review.astype(str)

# df_taxieu = df_taxieu.head(10) # testing purpose
listOfSentimentScores = []

for i in range(0, int(len(df_taxieu))):
    text_input = df_taxieu.review[i]
    star_rating = df_taxieu.rating[i]
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
    
    
df_taxieu['sentiment_score'] = listOfSentimentScores
print(df_taxieu)
df_taxieu.to_csv(config['csv_input_local']['taxieu_apple_google_p1_sentiment'])