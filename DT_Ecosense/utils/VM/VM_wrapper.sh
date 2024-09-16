#!/bin/bash

# Previous day's date
previous_day=$(date -d "yesterday" '+%Y-%m-%d')

# Create the log filename
log_file="/home/geosense/Documents/DT_Ecosense/logs/NVR/NVR_wrapper/NVR_wrapper_${previous_day}.txt"
log_file_main="/home/geosense/Documents/DT_Ecosense/logs/NVR/NVR_wrapper/NVR_wrapper_main_${previous_day}.txt"
echo "VM wrapper started at $(date)" >> "$log_file"

# Activate the Conda environment
source /home/geosense/miniconda3/etc/profile.d/conda.sh
source ~/.bashrc
conda activate dt_ecosense
echo "Conda environment activated: $(conda info --envs | grep '*' | awk '{print $1}')" >> "$log_file"

# Run the VM wrapper
python /home/geosense/Documents/DT_Ecosense/DT_Ecosense/utils/VM/VM_wrapper.py >> "$log_file_main"
echo "VM wrapper completed at $(date)" >> "$log_file"
