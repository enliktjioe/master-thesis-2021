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

result = senti.getSentiment('What a bad day')
print(result)


str_arr = ['What a lovely day', 'What a bad day']
result = senti.getSentiment(str_arr, score='binary')
print(result)


df_p1 = pd.read_csv(config['csv_input_local']['bolt_apple'], index_col=0)
df_p1 = df_p1.reset_index(drop=True)
total_reviews = len(df_p1)
unique_users  = len(df_p1['userName'].unique())
mean = df_p1['rating'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')

df_p1.review = df_p1.review.astype(str)

listOfRemovedIndex = []
for i in range(0, int(len(df_p1))):
# for i in range(0, 5): # testing purpose
    text_input = df_p1.review[i]
    star_rating = df_p1.rating[i]
    result = senti.getSentiment(text_input)
    
    # https://www.kite.com/python/answers/how-to-convert-a-list-of-integers-into-a-single-integer-in-python
    strings = [str(integer) for integer in result]
    a_string = "".join(strings)
    result_int = int(a_string)
    
    print(text_input)
    print(result_int)
    print(star_rating)
    print('\n')
    
    
    if star_rating < 3:
        if result_int <= -2 :
            isInconsistent = False
        else:
            isInconsistent = True
    elif star_rating > 3:
        if result_int >= 2:
            isInconsistent = False
        else:
            isInconsistent = True
    else:
        if result_int >= -1 and result_int <= 1:
            isInconsistent = False
        else:
            isInconsistent = True
    
    if isInconsistent == True:
        listOfRemovedIndex.append(i)
    
    

df_p2 = df_p1.drop(df_p1.index[listOfRemovedIndex])
total_reviews_before = len(df_p1)
total_reviews_after = len(df_p2)
total_removed_reviews = len(listOfRemovedIndex)

print(f'Total reviews (BEFORE): {total_reviews_before} \n')
print(f'Total reviews (AFTER): {total_reviews_after} \n')
print(f'Total Removed reviews: {total_removed_reviews} \n')