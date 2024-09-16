#!/bin/bash

# Date
CAMERA="07"

# Base directory
BASE_DIR="/mnt/geosense/cameras"

# Dates to remove files from
# DATES=(
#     23
#     24
#     25
#     26
#     27
#     28
# )

DATES=(
    23
    #24
    25
    26
    #27
    01
    #02
    #03
    04
    05
    06
    07
    08
    #09
    10
)

# Loop through each camera and remove the files
for DATE in "${DATES[@]}"; do
    for file in "${BASE_DIR}/G5Bullet_${CAMERA}/video_timelapse_export/"*${DATE}_fr30.mp4; do
        if [ -e "$file" ]; then
            filesize=$(stat -c%s "$file")
            if [ "$filesize" -gt $((100 * 1024 * 1024)) ]; then #
                rm -v "$file"
            else
                echo "File $file is less than 100MB, not deleting."
            fi
        else
            echo "No files found for pattern: ${BASE_DIR}/G5Bullet_${CAMERA}/video_timelapse_export/*${DATE}_fr30.mp4"
        fi
    done
done