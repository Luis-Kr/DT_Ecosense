import cv2
import numpy as np
import easyocr
from datetime import datetime
from pathlib import Path

def group_files_in_sets(dir_path, set_size=30):
    try:
        # Define the directory path
        dir_path = Path(dir_path)

        # Get a list of all files in the directory
        files = sorted([f for f in dir_path.iterdir() if f.is_file()])

        # Group files into sets of `set_size`
        grouped_files = [files[i:i + set_size] for i in range(0, len(files), set_size)]

        return grouped_files
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    

def find_largest_files_in_groups(dir_path, set_size=60):
    try:
        # Group the files into sets
        file_groups = group_files_in_sets(dir_path, set_size)
        largest_files = [None] * len(file_groups)

        # Iterate over each group to find the largest file
        for i, group in enumerate(file_groups):
            if group:
                largest_file = max(group, key=lambda f: f.stat().st_size, default=None)
                if largest_file:
                    largest_files[i] = largest_file

        return largest_files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def extract_camera_metadata(output_dir, image_paths):
    # Initialize the EasyOCR reader model
    reader = easyocr.Reader(['en'])
    filenames = []

    for image_path in image_paths:
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Failed to read the image file: {image_path}")

            # Read the date and camera name from the image
            result = reader.readtext(image)
            
            # Extract and format the timestamp from the text
            timestamp_string = result[0][1].replace(' ', '').replace(':', '.')
            parsed_timestamp = datetime.strptime(timestamp_string, '%Y-%m-%d%I.%M.%S%p')
            timestamp_24h = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            filename_safe_timestamp = timestamp_24h.replace(' ', '_').replace(':', '-')

            # Extract the camera name from the text
            camera_name = result[1][1][-2:]
            camera_folder = output_dir / camera_name
            camera_folder.mkdir(parents=True, exist_ok=True)

            # Generate the new filename and move the image to the new location
            current_date = filename_safe_timestamp.split('_')[0]
            date_folder = camera_folder / current_date
            date_folder.mkdir(parents=True, exist_ok=True)

            new_filename = f"Camera{camera_name}_{filename_safe_timestamp}.jpg"
            new_file_path = date_folder / new_filename
            image_path.rename(new_file_path)
            filenames.append(new_filename)

            print(f"File '{image_path}' moved to '{new_file_path}'.")

        except Exception as e:
            print(f"An error occurred with file '{image_path}': {e}")
            filenames.append("File_with_name_error.jpg")

    return filenames