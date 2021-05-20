#!/bin/bash

if [ $1 == "en" ] ;
then
	echo "en"
	make app-features dataset=GAME lang=$1
	make app-features dataset=PRODUCTIVITY lang=$1
	make app-features dataset=TRAVEL lang=$1
	make app-features dataset=PHOTOGRAPHY lang=$1
	make app-features dataset=SOCIAL lang=$1
	make app-features dataset=COMMUNICATION lang=$1

	make run-crfsuite dataset=GAME type=bc 
	make run-crfsuite dataset=PRODUCTIVITY type=bc 
	make run-crfsuite dataset=TRAVEL type=bc 
	make run-crfsuite dataset=PHOTOGRAPHY type=bc 
	make run-crfsuite dataset=SOCIAL type=bc 
	make run-crfsuite dataset=COMMUNICATION type=bc
fi
	
if [ $1 == "de" ] ;
then
	echo "de"
	make app-features dataset=WEATHER_APPS lang=$1
	make app-features dataset=SPORT_NEWS lang=$1
	make app-features dataset=SOCIAL_NETWORKS lang=$1
	make app-features dataset=OFFICE_TOOLS lang=$1
	make app-features dataset=NEWS_APPS lang=$1
	make app-features dataset=NAVIGATION_APPS lang=$1
	make app-features dataset=MUSIC_PLAYERS lang=$1
	make app-features dataset=INSTANT_MESSENGERS lang=$1
	make app-features dataset=GAMES lang=$1
	make app-features dataset=FITNESS_TRACKER lang=$1
	make app-features dataset=ALARM_CLOCKS lang=$1

	make run-crfsuite dataset=WEATHER_APPS type=bc > WEATHER_APPS_EVALUATION_CRF.txt
	make run-crfsuite dataset=SPORT_NEWS type=bc > SPORT_NEWS_EVALUATION_CRF.txt
	make run-crfsuite dataset=SOCIAL_NETWORKS type=bc > SOCIAL_NETWORKS_EVALUATION_CRF.txt
	make run-crfsuite dataset=OFFICE_TOOLS type=bc > OFFICE_TOOLS_EVALUATION_CRF.txt
	make run-crfsuite dataset=NEWS_APPS type=bc > NEWS_APPS_EVALUATION_CRF.txt
	make run-crfsuite dataset=NAVIGATION_APPS type=bc > NAVIGATION_APPS_EVALUATION_CRF.txt
	make run-crfsuite dataset=MUSIC_PLAYERS type=bc > MUSIC_PLAYERS_EVALUATION_CRF.txt
	make run-crfsuite dataset=INSTANT_MESSENGERS type=bc > INSTANT_MESSENGERS_EVALUATION_CRF.txt
	make run-crfsuite dataset=GAMES type=bc > GAMES_EVALUATION_CRF.txt
	make run-crfsuite dataset=FITNESS_TRACKER type=bc > FITNESS_TRACKER_EVALUATION_CRF.txt
	make run-crfsuite dataset=ALARM_CLOCKS type=bc > ALARM_CLOCKS_EVALUATION_CRF.txt
fi




