#!/bin/bash

CAM_Number="48"

# Define the main folders
main_folders=(
    "/mnt/gsdata/projects/ecosense/AngleCam2_0/data/corrected_frames/G5Bullet_${CAM_Number}/2024/"
    "/mnt/gsdata/projects/ecosense/AngleCam2_0/data/raw_frames/G5Bullet_${CAM_Number}/2024/"
    "/mnt/gsdata/projects/ecosense/AngleCam2_0/data/raw_videos/G5Bullet_${CAM_Number}/2024/"
)

# Create the main folders if they don't exist
for main_folder in "${main_folders[@]}"; do
    mkdir -p "$main_folder"
done

# Define the number of days in each month
declare -A days_in_month=(
    ["01"]=31 ["02"]=28 ["03"]=31 ["04"]=30 ["05"]=31 ["06"]=30
    ["07"]=31 ["08"]=31 ["09"]=30 ["10"]=31 ["11"]=30 ["12"]=31
)

# Check if the year is a leap year
is_leap_year() {
    year=$1
    if (( (year % 4 == 0 && year % 100 != 0) || year % 400 == 0 )); then
        return 0
    else
        return 1
    fi
}

# Adjust February for leap year
year=2024
if is_leap_year $year; then
    days_in_month["02"]=29
fi

# Loop through the months
for month in 08 09 10 11 12; do
    # Loop through the main folders
    for main_folder in "${main_folders[@]}"; do
        # Create the month folder if it doesn't exist
        month_folder="$main_folder/$month"
        if [ ! -d "$month_folder" ]; then
            mkdir -p "$month_folder"
        fi

        # Loop through the days
        for day in $(seq -w 1 ${days_in_month[$month]}); do
            # Create the day folder if it doesn't exist
            day_folder="$month_folder/$day"
            if [ ! -d "$day_folder" ]; then
                mkdir -p "$day_folder"
            fi
        done
    done
done

echo "Folder structure created successfully."



# CAM_Number="28"

# # Define the main folder
# main_folder1="/mnt/gsdata/projects/ecosense/AngleCam2_0/data/corrected_frames/G5Bullet_${CAM_Number}/2024/"
# main_folder2="/mnt/gsdata/projects/ecosense/AngleCam2_0/data/raw_frames/G5Bullet_${CAM_Number}/2024/"
# main_folder3="/mnt/gsdata/projects/ecosense/AngleCam2_0/data/raw_videos/G5Bullet_${CAM_Number}/2024/"

# # Create the main folder if it doesn't exist
# mkdir -p "$main_folder1"
# mkdir -p "$main_folder2"
# mkdir -p "$main_folder3"

# # Loop through the months
# for month in 08 09 10 11 12; do
#     # Create the month folder
#     month_folder="$main_folder1/$month"
#     mkdir -p "$month_folder"

#     # Loop through the days
#     for day in {01..31}; do
#         # Create the day folder
#         day_folder="$month_folder/$day"
#         mkdir -p "$day_folder"
#     done

#     month_folder="$main_folder2/$month"
#     mkdir -p "$month_folder"

#     # Loop through the days
#     for day in {01..31}; do
#         # Create the day folder
#         day_folder="$month_folder/$day"
#         mkdir -p "$day_folder"
#     done

#     month_folder="$main_folder3/$month"
#     mkdir -p "$month_folder"
    
#     # Loop through the days
#     for day in {01..31}; do
#         # Create the day folder
#         day_folder="$month_folder/$day"
#         mkdir -p "$day_folder"
#     done
# done

# echo "Folder structure created successfully."
