#!/bin/bash

# Get the date of yesterday
YESTERDAY=$(date -d "yesterday" +"%Y/%m/%d")

# Date
YEAR=$(echo $YESTERDAY | cut -d'/' -f1)
MONTH=$(echo $YESTERDAY | cut -d'/' -f2)
DAY=$(echo $YESTERDAY | cut -d'/' -f3)

# Base directory
BASE_DIR="/srv/unifi-protect/video"

# Loop through each camera and remove the files
for file in ${BASE_DIR}/${YEAR}/${MONTH}/${DAY}/*.ubv; do
    if [ -e "$file" ]; then
        rm -v "$file"
    else
        echo "No files found for pattern: ${BASE_DIR}/${YEAR}/${MONTH}/${DAY}/*.ubv"
    fi
done
