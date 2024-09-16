#!/bin/bash

# Activate the Conda environment
source /root/miniconda3/bin/activate dt_ecosense

# Log environment variables
env > /volume1/DT_Ecosense/logs/NVR/automated_data_transfer/automated_data_transfer.txt

# Append separators to the log file
echo "------------------------------------------------------------------------------------------" >> /volume1/DT_Ecosense/logs/NVR/automated_data_transfer/automated_data_transfer.txt
echo "------------------------------------------------------------------------------------------" >> /volume1/DT_Ecosense/logs/NVR/automated_data_transfer/automated_data_transfer.txt

# Delete unnecessary files from the NVR of the previous day
bash /volume1/DT_Ecosense/DT_Ecosense/utils/NVR/delete_files_previous_day.sh >> /volume1/DT_Ecosense/logs/NVR/automated_data_transfer/automated_data_transfer.txt 2>&1

# Run the Python script and log output and errors
python /volume1/DT_Ecosense/DT_Ecosense/NVR_main.py >> /volume1/DT_Ecosense/logs/NVR/automated_data_transfer/automated_data_transfer.txt 2>&1