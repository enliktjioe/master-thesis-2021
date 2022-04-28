# from utils import *
from utils import *
import pandas as pd

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')

from sentistrength import PySentiStr
senti = PySentiStr()

# Rocket HPC
# senti.setSentiStrengthPath('/gpfs/space/home/enlik/GitRepo/master-thesis-2021/references/SentiStrengthCom.jar') # Note: Provide absolute path instead of relative path
# senti.setSentiStrengthLanguageFolderPath('/gpfs/space/home/enlik/GitRepo/master-thesis-2021/references/SentiStrengthData/') # Note: Provide absolute path instead of relative path

# Local
senti.setSentiStrengthPath('C:/GitRepo/master-thesis-2021/references/SentiStrengthCom.jar') # Note: Provide absolute path instead of relative path
senti.setSentiStrengthLanguageFolderPath('C:/GitRepo/master-thesis-2021/references/SentiStrengthData') # Note: Provide absolute path instead of relative path


df_topic = pd.read_csv(config['csv_input_local']['all_reviews_p3_topic'], index_col=0)
df_topic = df_topic.reset_index(drop=True)
total_reviews = len(df_topic)

print(f'Total English reviews: {total_reviews} /n')
df_topic.review = df_topic.review.astype(str)

# df_topic = df_topic.head(10) # testing purpose
listOfSentimentScores = []

for i in range(0, int(len(df_topic))):
    text_input = df_topic.review[i]
    # print(text_input)
    star_rating = df_topic.rating[i]
    # print(star_rating)
    result = senti.getSentiment(text_input)
    print(result)
    
    # https://www.kite.com/python/answers/how-to-convert-a-list-of-integers-into-a-single-integer-in-python
    strings = [str(integer) for integer in result]
    a_string = "".join(strings)
    result_int = int(a_string)
    
    listOfSentimentScores.append(result_int)

    print('index = ' + str(i))
    # print('result_int = ' + str(result_int))
    # print(listOfSentimentScores)
    
    
df_topic['sentiment_score'] = listOfSentimentScores
print(df_topic)
df_topic.to_csv(config['csv_input_local']['all_reviews_p3_topic_sentiment'])