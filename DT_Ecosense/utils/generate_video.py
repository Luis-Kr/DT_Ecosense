import cv2
import os

# Directory containing the PNG images
image_folder = '/Users/luiskremer/Documents/PhD/Code/AngleCam/Data/VM_processing/Data/Frames2/'

# Output video file name
video_name = '/Users/luiskremer/Documents/PhD/Code/AngleCam/Data/VM_processing/Data/Frames2/animation.mp4'

# Fetch all images from the folder
images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
images.sort()  # Ensure the images are in the correct order

# Read the first image to get dimensions
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'avc1')
video = cv2.VideoWriter(video_name, fourcc, 120, (width, height))

# Loop through all images and write them to the video
print(f"Creating video {video_name}...")
for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

# Release the video writer object
video.release()
cv2.destroyAllWindows()
