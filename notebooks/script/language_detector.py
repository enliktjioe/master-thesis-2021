#!/usr/bin/env python
# coding: utf-8

# !pip install langdetect


from langdetect import detect, detect_langs
from utils import *

from utils import *

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

config = get_config('config.yaml')


def isEnglishReview(textInput):
#     check after and before string
#     https://stackoverflow.com/questions/12572362/how-to-get-a-string-after-a-specific-substring
#     https://stackoverflow.com/questions/27387415/how-would-i-get-everything-before-a-in-a-string-python
    try:
        a = detect_langs(textInput)
        listToStr = ','.join(map(str, a))
        english_score = float((listToStr.partition('en:')[2]).partition(',')[0])
    except:
        a = None
        listToStr = None
        english_score = 0
    
    if english_score > 0.1:
        isEnglish = True
    else:
        isEnglish = False
    
    return isEnglish, listToStr, english_score


detect("War doesn't show who's right, just who's left.")


detect('selamat pagi')


detect('armastus')


detect("Suurepärane, lihtne ja kiire äpp mida saab iga situatsioonis ja konditsioonis kasutada. Ainult kiidusõnad!")


detect_langs("Suurepärane, lihtne ja kiire äpp mida saab iga situatsioonis ja konditsioonis kasutada. Ainult kiidusõnad!")


detect_langs("Best bolt evveeerrr")


detect_langs("Very fast and affordable")


detect_langs("Impatient")


detect_langs("pourquoi ne pas afficher toutes les voitures disponibles autour du point de prise en charge ? faire des promos c’est bien mais si pas de voitures disponibles....des erreurs 7002 fréquentes, des indications de temps d’arrivée fantaisistes. Une fois le chauffeur sélectionné on s’aperçoit souvent qu’il finit une course et ça prend du temps ce qui fait que le compteur d’arrivée reste figé sur un temps d’attente « acceptable » pour bloquer l’usager mais qui peut facilement être le double de celui indiqué....")


detect_langs("I love it")


detect_langs("Amazing app")


detect_langs("J’ai pour ma part payé ma course beaucoup plus chère que prévue. Aucun moyen d’avoir des réponses sur ce sujet: le sav ne répond pas, que vous écriviez en français ou en anglais (d’ailleurs l’application supprime vos questions au SAV... comme ça ils doivent ne pas avoir l’impression qu’il y a un problème !). J’ai répondu à un questionnaire de satisfaction envoyé par mail : j’ai mis de mauvaises notes et un commentaire sur mon problème : aucune réponse Donc en synthèse : si tout se passe bien ils encaissent ! Et sinon ... ils encaissent ! Bref cela manque terriblement de professionnalisme !")


isEnglishReview("J’ai pour ma part payé ma course beaucoup plus chère que prévue. Aucun moyen d’avoir des réponses sur ce sujet: le sav ne répond pas, que vous écriviez en français ou en anglais (d’ailleurs l’application supprime vos questions au SAV... comme ça ils doivent ne pas avoir l’impression qu’il y a un problème !). J’ai répondu à un questionnaire de satisfaction envoyé par mail : j’ai mis de mauvaises notes et un commentaire sur mon problème : aucune réponse Donc en synthèse : si tout se passe bien ils encaissent ! Et sinon ... ils encaissent ! Bref cela manque terriblement de professionnalisme !")


# ## Bolt Apple App Store Review Test

df2 = read_csv_from_gdrive(config['csv_input']['bolt_apple'])
total_reviews = len(df2)
unique_users  = len(df2['userName'].unique())
mean = df2['rating'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


df2.review = df2.review.astype(str)


df2 = df2.reset_index()


df2['review'][2]


for i in range(0, len(df2)):
    reviewText = df2['review'][i]
    print(reviewText)
    
    
    print(isEnglishReview(reviewText))
    print('\n')


# ## Bolt Google Play Store Reviews

df = read_csv_from_gdrive(config['csv_input']['bolt_google'])
total_reviews = len(df)
unique_users  = len(df['userName'].unique())
unknown_users = len(df[df['userName']=='A Google user'])
mean = df['score'].mean()

print(f'Total English reviews: {total_reviews} \n')
print(f'Total unique users : {unique_users}')
print(f'Total unknown users: {unknown_users}')
print(f'Total users who gave multiple reviews: {total_reviews - unique_users - unknown_users}\n')
print(f'Average rating for this app based on the textual reviews: {round(mean,2)} \n')


df.content = df.content.astype(str)
df = df.reset_index()


for i in range(0, len(df)):
    reviewText = df['content'][i]
    print(reviewText)
    
    
    print(isEnglishReview(reviewText))
    print('\n')


detect_langs("Best App")




