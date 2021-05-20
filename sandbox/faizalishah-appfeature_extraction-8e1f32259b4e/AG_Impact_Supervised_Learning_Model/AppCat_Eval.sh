#!/bin/bash

if [ $1 == "en" ] ;
then
	make prepare-dataset dataset=GAME lang=$1
	make prepare-dataset dataset=PRODUCTIVITY lang=$1
	make prepare-dataset dataset=TRAVEL lang=$1
	make prepare-dataset dataset=PHOTOGRAPHY lang=$1
	make prepare-dataset dataset=SOCIAL lang=$1
	make prepare-dataset dataset=COMMUNICATION lang=$1

	bash cv-batch_crf.sh GAME bc 
	bash cv-batch_crf.sh PRODUCTIVITY bc 
	bash cv-batch_crf.sh TRAVEL bc 
	bash cv-batch_crf.sh PHOTOGRAPHY bc 
	bash cv-batch_crf.sh SOCIAL bc 
	bash cv-batch_crf.sh COMMUNICATION bc
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

	bash cv-batch_crf.sh WEATHER_APPS bc 
	bash cv-batch_crf.sh SPORT_NEWS bc 
	bash cv-batch_crf.sh SOCIAL_NETWORKS bc
	bash cv-batch_crf.sh OFFICE_TOOLS bc
	bash cv-batch_crf.sh NEWS_APPS bc
	bash cv-batch_crf.sh NAVIGATION_APPS bc
	bash cv-batch_crf.sh MUSIC_PLAYERS bc
	bash cv-batch_crf.sh INSTANT_MESSENGERS bc
	bash cv-batch_crf.sh GAMES bc
	bash cv-batch_crf.sh FITNESS_TRACKER bc
	bash cv-batch_crf.sh ALARM_CLOCKS bc
fi

