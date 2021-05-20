#!/bin/bash

if [ $1 == "en" ] ;
then
	make prepare-dataset dataset=GAME lang=$1
	make prepare-dataset dataset=PRODUCTIVITY lang=$1
	make prepare-dataset dataset=TRAVEL lang=$1
	make prepare-dataset dataset=PHOTOGRAPHY lang=$1
	make prepare-dataset dataset=SOCIAL lang=$1
	make prepare-dataset dataset=COMMUNICATION lang=$1

fi
	
if [ $1 == "de" ] ;
then
	make prepare-dataset dataset=WEATHER_APPS lang=$1
	make prepare-dataset dataset=SPORT_NEWS lang=$1
	make prepare-dataset dataset=SOCIAL_NETWORKS lang=$1
	make prepare-dataset dataset=OFFICE_TOOLS lang=$1
	make prepare-dataset dataset=NEWS_APPS lang=$1
	make prepare-dataset dataset=NAVIGATION_APPS lang=$1
	make prepare-dataset dataset=MUSIC_PLAYERS lang=$1
	make prepare-dataset dataset=INSTANT_MESSENGERS lang=$1
	make prepare-dataset dataset=GAMES lang=$1
	make prepare-dataset dataset=FITNESS_TRACKER lang=$1
	make prepare-dataset dataset=ALARM_CLOCKS lang=$1
fi
