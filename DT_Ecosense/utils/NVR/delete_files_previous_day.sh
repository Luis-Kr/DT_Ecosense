#!/bin/bash

# Base directory
base_dir="/srv/unifi-protect/video"
#base_dir="/srv/unifi-protect/video/2024/09/06"

# Get the date of the previous day
prev_date=$(date -d "yesterday" +"%Y/%m/%d")
#prev_date="2024/09/04"

# Construct the full path to the previous day's directory
full_path="$base_dir/$prev_date"

# Define the file patterns to delete
file_patterns=("F4E2C679DA65_0_rotating*.ubv" "F4E2C678CC98_0_rotating*.ubv" "F4E2C678D13E_0_rotating*.ubv" "F4E2C678CCF6_0_rotating*.ubv" "F4E2C678CCF8_0_rotating*.ubv" "F4E2C679D7C1_0_rotating*.ubv" "F4E2C679D691_0_rotating*.ubv" "F4E2C679E075_0_rotating*.ubv" "F4E2C679D667_0_rotating*.ubv" "F4E2C679DB67_0_rotating*.ubv")
file_patterns2=("F4E2C679DA65_2_rotating*.ubv" "F4E2C678CC98_2_rotating*.ubv" "F4E2C678D13E_2_rotating*.ubv" "F4E2C678CCF6_2_rotating*.ubv" "F4E2C678CCF8_2_rotating*.ubv" "F4E2C679D7C1_2_rotating*.ubv" "F4E2C679D691_2_rotating*.ubv" "F4E2C679E075_2_rotating*.ubv" "F4E2C679D667_2_rotating*.ubv" "F4E2C679DB67_2_rotating*.ubv")

# Log file
log_file="/volume1/scripts/delete_files_log.txt"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$log_file"
}

# Check if the directory exists
if [ -d "$full_path" ]; then
    # Loop through each file pattern and delete matching files
    for pattern in "${file_patterns[@]}"; do
        if rm -v "$full_path"/$pattern >> "$log_file" 2>&1; then
            log_message "Successfully deleted files matching pattern '$pattern' in directory '$full_path'."
        else
            log_message "Failed to delete files matching pattern '$pattern' in directory '$full_path'."
        fi
    done

    # Loop through each file pattern in file_patterns2 and delete matching files
    for pattern in "${file_patterns2[@]}"; do
        if rm -v "$full_path"/$pattern >> "$log_file" 2>&1; then
            log_message "Successfully deleted files matching pattern '$pattern' in directory '$full_path'."
        else
            log_message "Failed to delete files matching pattern '$pattern' in directory '$full_path'."
        fi
    done
else
    log_message "Directory $full_path does not exist. No files to delete."
fi








#Old version
#------------------------


# # Base directory
# base_dir="/srv/unifi-protect/video"

# # Get the date of the previous day
# prev_date=$(date -d "5 days ago" +"%Y/%m/%d") #prev_date=$(date -d "yesterday" +"%Y/%m/%d")

# # Construct the full path to the previous day's directory
# full_path="$base_dir/$prev_date"

# # Define the file patterns to delete
# file_patterns=("F4E2C679DA65_0_rotating*.ubv" "F4E2C678D5F6_0_rotating*.ubv" "F4E2C678CC98_0_rotating*.ubv" "F4E2C678D13E_0_rotating*.ubv" "F4E2C679D8FC_0_rotating*.ubv" "F4E2C678CBCD_0_rotating*.ubv" "F4E2C678CBC5_0_rotating*.ubv" "F4E2C678CCF6_0_rotating*.ubv" "F4E2C678CCF8_0_rotating*.ubv" "F4E2C679D7C1_0_rotating*.ubv" "F4E2C679D691_0_rotating*.ubv" "F4E2C679E075_0_rotating*.ubv" "F4E2C679D6B7_0_rotating*.ubv" "F4E2C679D63B_0_rotating*.ubv" "F4E2C679D667_0_rotating*.ubv" "F4E2C679DB67_0_rotating*.ubv")
# file_patterns2=("F4E2C679DA65_2_rotating*.ubv" "F4E2C678D5F6_2_rotating*.ubv" "F4E2C678CC98_2_rotating*.ubv" "F4E2C678D13E_2_rotating*.ubv" "F4E2C679D8FC_2_rotating*.ubv" "F4E2C678CBCD_2_rotating*.ubv" "F4E2C678CBC5_2_rotating*.ubv" "F4E2C678CCF6_2_rotating*.ubv" "F4E2C678CCF8_2_rotating*.ubv" "F4E2C679D7C1_2_rotating*.ubv" "F4E2C679D691_2_rotating*.ubv" "F4E2C679E075_2_rotating*.ubv" "F4E2C679D6B7_2_rotating*.ubv" "F4E2C679D63B_2_rotating*.ubv" "F4E2C679D667_2_rotating*.ubv" "F4E2C679DB67_2_rotating*.ubv")

# # Log file
# log_file="/volume1/scripts/delete_files_log.txt"

# # Function to log messages
# log_message() {
#     echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$log_file"
# }

# # Check if the directory exists
# if [ -d "$full_path" ]; then
#     # Loop through each file pattern and delete matching files
#     for pattern in "${file_patterns[@]}"; do
#         if rm -v "$full_path"/$pattern >> "$log_file" 2>&1; then
#             log_message "Successfully deleted files matching pattern '$pattern' in directory '$full_path'."
#         else
#             log_message "Failed to delete files matching pattern '$pattern' in directory '$full_path'."
#         fi
#     done
# else
#     log_message "Directory $full_path does not exist. No files to delete."
# fi
