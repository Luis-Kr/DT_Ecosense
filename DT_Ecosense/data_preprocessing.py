import cv2
import numpy as np
import easyocr
from datetime import datetime
from pathlib import Path
import subprocess
import dask
from dask import delayed
from dask.diagnostics import ProgressBar
import dask.bag as db
import h5py
import time
import multiprocessing as mp
import os
import pprint

# Custom imports
import utils.logger as lgr

# Initialize the OCR reader with GPU disabled
reader = easyocr.Reader(['en'], gpu=True)

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


def extract_frames(logger, video_path, output_dir, frame_number=0):
    video_capture = cv2.VideoCapture(video_path)
    
    if not video_capture.isOpened():
        logger.info("Error: Could not open video.")
        return
    
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        logger.info("Error: Could not retrieve frame rate.")
        return
    
    logger.info(f"Frame rate: {fps}")
    logger.info(f"Extracting frames from video '{video_path}'...")
    
    # Calculate the frame number corresponding to 3min intervals
    frames_per_interval = int(fps * 120)
    frame_number_internal = 0
    
    # Record the start time
    start_time = time.time()
    
    while True:
        # Check if the elapsed time exceeds 5 minutes (300 seconds)
        elapsed_time = time.time() - start_time
        # if elapsed_time > 600:
        #     logger.info("Break: Processing time exceeds 10 minutes.")
        #     break
        
        # Get the total number of frames in the video
        total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        
        # Check if frame_number_internal exceeds the total number of frames
        if frame_number_internal >= total_frames:
            logger.info("Break: frame_number_internal exceeds total number of frames.")
            break
        
        # Set the video capture position to the next frame of interest
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number_internal)
        
        ret, frame = video_capture.read()
        if not ret:
            logger.info("Break: Could not read frame or video is fully processed.")
            break
        
        # Save one frame per interval
        if frame_number_internal % frames_per_interval == 0:
            frame_filename = f'{output_dir}/frame_{frame_number + frame_number_internal // frames_per_interval:06d}.jpg'
            cv2.imwrite(frame_filename, frame)
            logger.info(f"Extracting frame {frame_number + frame_number_internal // frames_per_interval}...")
        
        # Increment frame_number_internal by frames_per_interval to skip frames
        frame_number_internal += frames_per_interval
        logger.info(f"Frame number internal: {frame_number_internal}")
    
    video_capture.release()
    logger.info("All frames extracted.")
    logger.info(f"Frame number: {frame_number}")
    
    # Update the global frame_number to reflect the total frames processed
    frame_number += frame_number_internal // frames_per_interval
    
    return frame_number


def extract_all_frames(logger, video_path, output_dir):
    frame_timestamp_error = 0
    video_capture = cv2.VideoCapture(video_path)
    
    if not video_capture.isOpened():
        logger.info("Error: Could not open video.")
        return
    
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        logger.info("Error: Could not retrieve frame rate.")
        return
    
    logger.info(f"Frame rate: {fps}")
    logger.info(f"Extracting frames from video '{video_path}'...")
    
    # Calculate the frame number corresponding to 3min intervals
    frame_number_internal = 0
    
    # Record the start time
    start_time = time.time()
    
    while True:
        elapsed_time = (time.time() - start_time) / 60
        logger.info(f"Elapsed time: {elapsed_time} minutes")
        
        # Check if the elapsed time exceeds 5 minutes (300 seconds)
        # if elapsed_time > 600:
        #     logger.info("Break: Processing time exceeds 10 minutes.")
        #     break
        
        # Get the total number of frames in the video
        total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        
        # Check if frame_number_internal exceeds the total number of frames
        if frame_number_internal >= total_frames:
            logger.info("Break: frame_number_internal exceeds total number of frames.")
            break
        
        # Set the video capture position to the next frame of interest
        #video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number_internal)
        
        ret, frame = video_capture.read()
        if not ret:
            logger.info("Break: Could not read frame or video is fully processed.")
            break
        
        # Save every frame
        if frame_number_internal % 1 == 0:
            #camera_name, filename_safe_timestamp, frame_timestamp_error = extract_camera_name_and_date(logger, frame, reader, frame_timestamp_error)
            #frame_filename = f'{output_dir}/G5Bullet_{int(camera_name):02d}_{filename_safe_timestamp}.jpg'
            frame_filename = f'{output_dir}/frame_{frame_number_internal:05d}.jpg'
            logger.info(f"Frame filename: {frame_filename}")
            cv2.imwrite(frame_filename, frame)
            logger.info(f"Extracting frame {frame_number_internal}...")
        
        # Increment frame_number_internal by frames_per_interval to skip frames
        frame_number_internal += 1
        logger.info(f"Frame number internal: {frame_number_internal}")
    
    video_capture.release()
    logger.info("All frames extracted.")
    logger.info(f"Frame number: {frame_number_internal}")
    
    return None


def generate_video_from_images(image_folder, video_name, codec='avc1', frame_rate=120):
    # Convert image_folder to Path object
    image_folder = Path(image_folder)
    
    # Fetch all images from the folder and sort them
    images = sorted([img for img in image_folder.iterdir() if img.suffix == ".jpg"])

    # Read the first image to get dimensions
    frame = cv2.imread(str(images[0]))
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video = cv2.VideoWriter(video_name, fourcc, frame_rate, (width, height))

    # Loop through all images and write them to the video
    for image in images:
        video.write(cv2.imread(str(image)))

    # Release the video writer object
    video.release()
    cv2.destroyAllWindows()



    
def extract_camera_name_and_date(logger, image_path, frame_timestamp_error, reader):
    # Read the image
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
 
    # Read the date and camera name from the image
    result = reader.readtext(image, workers=1)

    # Extract and format the timestamp from the text
    try: 
        timestamp_string = result[0][1].replace(' ', '').replace(':', '.')
        parsed_timestamp = datetime.strptime(timestamp_string, '%Y-%m-%d%I.%M.%S%p')
        timestamp_24h = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        filename_safe_timestamp = timestamp_24h.replace(' ', '_').replace(':', '-')
    except Exception as e:
        logger.error(f"An error occurred with the timestamp: {e}")
        filename_safe_timestamp = f"frame_timestamp_error_{frame_timestamp_error:03d}"
        logger.info(f"Now saving as: {filename_safe_timestamp}")
        frame_timestamp_error += 1
        
    # Extract the camera name from the text
    camera_name = result[1][1][-2:]

    return camera_name, filename_safe_timestamp, image_path, frame_timestamp_error


def process_image(image_info):
    logger, image_path, frame_timestamp_error, reader = image_info
    return extract_camera_name_and_date(logger, image_path, frame_timestamp_error, reader)


def rename_images_with_date(logger, image_dir, output_dir):
    # Initialize the OCR reader
    logger.info("Initializing OCR reader...")
    reader = easyocr.Reader(['en'], gpu=True)
    
    frame_timestamp_error = 0
    
    # Get the list of images
    image_paths = sorted(list(Path(image_dir).glob("*.jpg"))) # Assuming .jpg files; adjust as necessary
    
    logger.info(f"Found {len(image_paths)} images in directory {image_dir}.")
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for _, image_path in enumerate(image_paths):
        try:
            camera_name, filename_safe_timestamp, image_path, frame_timestamp_error = process_image((logger, image_path, frame_timestamp_error, reader))
            frame_filename = f'{output_dir}/G5Bullet_{int(camera_name):02d}_{filename_safe_timestamp}.jpg'
            logger.info(f"Frame filename: {frame_filename}")
            
            # Rename the file
            os.rename(image_path, frame_filename)
            logger.info(f"Renamed {image_path} to {frame_filename}.")
        except Exception as e:
            logger.error(f"An error occurred with file '{image_path}': {e}")
            continue

    logger.info("All images processed.")
    
    return None




















# def read_image(image_path):
#     return cv2.imread(str(image_path))

# def generate_video_from_images_dask(image_folder, video_name, codec='avc1', frame_rate=120):
#     # Convert image_folder to Path object
#     image_folder = Path(image_folder)
    
#     # Fetch all images from the folder and sort them
#     images = sorted([img for img in image_folder.iterdir() if img.suffix == ".jpg"])

#     # Read the first image to get dimensions
#     frame = cv2.imread(str(images[0]))
#     height, width, layers = frame.shape

#     # Define the codec and create VideoWriter object
#     fourcc = cv2.VideoWriter_fourcc(*codec)
#     video = cv2.VideoWriter(video_name, fourcc, frame_rate, (width, height))

#     # Use Dask to parallelize the image reading process
#     print(f"Creating video {video_name}...")
#     tasks = [delayed(read_image)(image) for image in images]
    
#     with ProgressBar():
#         frames = dask.compute(*tasks)

#     # Write the frames to the video sequentially
#     for frame in frames:
#         video.write(frame)

#     # Release the video writer object
#     video.release()
#     cv2.destroyAllWindows()
    
    

# def generate_video_from_images_dask(image_folder, video_name, codec='avc1', frame_rate=120):
#     # Convert image_folder to Path object
#     image_folder = Path(image_folder)
    
#     # Fetch all images from the folder and sort them
#     images = sorted([img for img in image_folder.iterdir() if img.suffix == ".jpg"])

#     # Read the first image to get dimensions
#     frame = cv2.imread(str(images[0]))
#     height, width, layers = frame.shape

#     # Define the codec and create VideoWriter object
#     fourcc = cv2.VideoWriter_fourcc(*codec)
#     video = cv2.VideoWriter(video_name, fourcc, frame_rate, (width, height))

#     # Use a generator to process images one by one
#     print(f"Creating video {video_name}...")
    
#     def image_generator(images):
#         for image in images:
#             yield read_image(image)
    
#     with ProgressBar():
#         for frame in image_generator(images):
#             video.write(frame)

#     # Release the video writer object
#     video.release()
#     cv2.destroyAllWindows()
    


# def save_images_as_numpy(image_folder, output_folder):
#     # Convert image_folder and output_folder to Path objects
#     image_folder = Path(image_folder)
#     output_folder = Path(output_folder)
#     output_folder.mkdir(parents=True, exist_ok=True)
    
#     # Fetch all images from the folder and sort them
#     images = sorted([img for img in image_folder.iterdir() if img.suffix == ".jpg"])

#     # Loop through all images and save them as compressed numpy arrays
#     print(f"Saving images from {image_folder} to {output_folder} as compressed numpy arrays...")
#     for idx, image in enumerate(images):
#         img_array = cv2.imread(str(image))
#         output_file = output_folder / f"image_{idx:03d}.npz"
#         np.savez_compressed(output_file, img_array)
#         print(f"Saved {output_file}")
        

# def save_images_as_numpy_and_hdf5(image_folder, output_folder):
#     # Convert image_folder and output_folder to Path objects
#     image_folder = Path(image_folder)
#     output_folder = Path(output_folder)
#     output_folder.mkdir(parents=True, exist_ok=True)
    
#     # Fetch all images from the folder and sort them
#     images = sorted([img for img in image_folder.iterdir() if img.suffix == ".jpg"])

#     # Loop through all images and save them as compressed numpy arrays and HDF5 files
#     print(f"Saving images from {image_folder} to {output_folder} as compressed numpy arrays and HDF5 files...")
#     for idx, image in enumerate(images):
#         img_array = cv2.imread(str(image), cv2.IMREAD_UNCHANGED)
        
#         # Save as compressed numpy array
#         npz_output_file = output_folder / f"image_{idx:03d}.npy"
#         np.save(npz_output_file, img_array)
#         print(f"Saved {npz_output_file}")
        
#         # Save as HDF5 file
#         hdf5_output_file = output_folder / f"image_{idx:03d}.h5"
#         with h5py.File(hdf5_output_file, 'w') as hdf5_file:
#             hdf5_file.create_dataset('image', data=img_array, compression='gzip')
#         print(f"Saved {hdf5_output_file}")
    


def transfer_data_remote_local(remote_user, remote_host, remote_dir, local_dir):
    # Construct the rsync command
    rsync_command = [
        'rsync',
        '-avz',  # Options: archive mode, verbose, compress file data during the transfer
        '--progress',
        '-e', 'ssh',  # Use SSH for the transfer
        f'{remote_user}@{remote_host}:{remote_dir}',
        local_dir
    ]

    # Execute the rsync command
    try:
        subprocess.run(rsync_command, check=True)
        print(f"Data transferred successfully from {remote_user}@{remote_host}:{remote_dir} to {local_dir}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while transferring data: {e}")

   
def transfer_data_local_remote(remote_user, remote_host, remote_dir, local_dir):
    # Construct the rsync command
    rsync_command = [
        'rsync',
        '-avz',  # Options: archive mode, verbose, compress file data during the transfer
        '--progress',
        '-e', 'ssh',  # Use SSH for the transfer
        local_dir,
        f'{remote_user}@{remote_host}:{remote_dir}',
    ]

    # Execute the rsync command
    try:
        subprocess.run(rsync_command, check=True)
        print(f"Data transferred successfully from {local_dir} to {remote_user}@{remote_host}:{remote_dir}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while transferring data: {e}")

