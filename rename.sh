#!/bin/bash

filetypes=(.en.vtt .jpg .mkv .mp4 .webm)

if [ ! $1 ];then
	echo -e "\n\nrename.sh"
	echo -e "\nPurpose: prepends all files with names starting with <filename-string> with the date given by <date>, so that they will be kept in proper date order."
	echo -e "\nUse: rename.sh <filename-string> <date>\n\n"
else

	NAM=$1
	if [ ! $2 ];then
		read -p "No date string provided. Please provide a date string:" DATE
	else
		DATE=$2
	fi

	for i in ${filetypes[*]};do
		if [ -e "$NAM$i" ];then
			echo "$NAM$i -> $DATE-$NAM$i"
			mv "$NAM$i" "$DATE-$NAM$i"
		fi
	done
fi
