#!/bin/bash

# Date
DATE="2024-09-23"

# Base directory
BASE_DIR="/volume1/videos"

# Cameras to remove files from

DIRS=(
    "G5Bullet_07"
    "G5Bullet_26"
    "G5Bullet_27"
    "G5Bullet_28"
    "G5Bullet_31"
    "G5Bullet_32"
    "G5Bullet_33"
    "G5Bullet_34"
    "G5Bullet_35"
    "G5Bullet_36"
    "G5Bullet_37"
    "G5Bullet_39"
    "G5Bullet_40"
    "G5Bullet_43"
    "G5Bullet_47"
    "G5Bullet_48"
)

# Loop through each camera and remove the files
for DIR in "${DIRS[@]}"; do
    for file in ${BASE_DIR}/${DATE}/${DIR}/*.mp4; do
        if [ -e "$file" ]; then
            rm -v "$file"
        else
            echo "No files found for pattern: ${BASE_DIR}/${DATE}/${DIR}/*.mp4"
        fi
    done
done