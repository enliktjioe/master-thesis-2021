#!/bin/bash

if [ $1 == "en" ] ;
then
	make prepare-dataset dataset=GAME lang=$1
	make prepare-dataset dataset=PRODUCTIVITY lang=$1
	make prepare-dataset dataset=TRAVEL lang=$1
	make prepare-dataset dataset=PHOTOGRAPHY lang=$1
	make prepare-dataset dataset=SOCIAL lang=$1
	make prepare-dataset dataset=COMMUNICATION lang=$1
	make prepare-dataset dataset=SEMEVAL lang=$1

fi
	


