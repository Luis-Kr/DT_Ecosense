from datetime import datetime
from pathlib import Path
import warnings
from typing import List, Tuple
import re
import shutil
import os

# Custom imports
import utils.logger as lgr
import data_preprocessing as dp

# Hydra and OmegaConf imports
import hydra
from hydra import compose, initialize
from omegaconf import DictConfig

# Ignore warnings
warnings.filterwarnings("ignore")

# get the path of the current file
root_dir = Path(__file__).parent.parent.absolute()

def get_date_today():
    # Get the date of today
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    
    return year, month, day


def setup_camera_directories(cfg: DictConfig, cams: List[Tuple[str, str]], i: int) -> Tuple[Path, Path]:
    camera_name, cam_mac_address = cams[i]
    remote_dir = Path(cfg.remote_dir) / camera_name / '*0.mp4'
    local_dir_mp4 = Path(cfg.dst_dir) / camera_name / 'mp4'
    local_dir_frames = Path(cfg.dst_dir) / camera_name / 'frames'
    output_video = Path(cfg.dst_dir) / camera_name / 'video_timelapse_export'
    
    # Create the destination directories if they do not exist
    for directory in [local_dir_mp4, local_dir_frames, output_video]:
        directory.mkdir(parents=True, exist_ok=True)

    return remote_dir, local_dir_mp4, local_dir_frames, output_video, camera_name


def extract_number(file_name):
    """Extracts the first number found in the file name."""
    match = re.search(r'\d+', file_name)
    return int(match.group()) if match else float('inf')


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig):
    # Clear the hydra config cache
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    date_today = datetime.now().strftime("%Y-%m-%d")
    # Set up the logger
    logger = lgr.logger_setup('main', root_dir / cfg.paths.logger.dst_dir / f"{date_today}.log")
    
    # Get the list of cameras
    cams = list(cfg.cams.items())
    
    # Get the date of today
    year, month, day = get_date_today()
    
    # logger.info("Grouping files in sets...")
    # largest_files = dp.find_largest_files_in_groups(dir_path=cfg.raw_data, set_size=cfg.set_size)
    
    # logger.info("Extracting camera metadata and subsampling the data...")
    # filenames = dp.extract_camera_metadata(output_dir=root_dir / cfg.dst_dir, image_paths=largest_files)
    
    for i in range(len(cams)):
        # Set up the camera directories    
        remote_dir, local_dir_mp4, local_dir_frames, output_video, camera_name = setup_camera_directories(cfg, cams, i)
        
        logger.info("Transfering data...")
        # dp.transfer_data_remote_local(remote_user="root", 
                    #                  remote_host="10.6.159.52", 
                    #                  remote_dir=str(remote_dir), 
                    #                  local_dir=str(local_dir_mp4))
    
        logger.info("Extract frames...")
        
        # Initialize frame_number
        frame_number = -1
        
        # Get all .mp4 files and sort them
        mp4_files = sorted(local_dir_mp4.glob('*.mp4'), key=lambda f: int(f.name.split('_')[-2]))
        
        # # Loop through the sorted files and rename them
        # for idx, mp4_file in enumerate(mp4_files):
        #     # Construct the new filename
        #     new_name = mp4_file.parent / f'File_{idx:03d}_{mp4_file.name}'
            
        #     # Check if the new filename already exists
        #     if not new_name.exists():
        #         # Rename the file
        #         mp4_file.rename(new_name)
        #         logger.info(f"Renamed {mp4_file} to {new_name}")
        #     else:
        #         logger.warning(f"File {new_name} already exists. Skipping rename.")
        
        # Loop through all .mp4 files in the local_dir_mp4
        for idx, mp4_file in enumerate(sorted(local_dir_mp4.glob('*.mp4'))):
            logger.info(f"Processing file {mp4_file}...")
            frame_number = dp.extract_frames(logger=logger, 
                                             video_path=mp4_file, 
                                             output_dir=local_dir_frames, 
                                             frame_interval=10, 
                                             frame_number=frame_number)
            
            logger.info("Grouping files in sets...")
            largest_files = dp.find_largest_files_in_groups(dir_path=local_dir_frames, set_size=cfg.set_size)
            
            # Create the destination directory if it doesn't exist
            hq_frames_dir = Path(cfg.dst_dir) / camera_name / 'hq_frames'
            hq_frames_dir.mkdir(parents=True, exist_ok=True)
            
            staging_frames_dir = local_dir_frames / 'staging'
            staging_frames_dir.mkdir(parents=True, exist_ok=True)
            
            # Move the largest files to local_dir_frames/staging
            logger.info("Moving files to staging directory...")
            [shutil.move(str(file_path), str(staging_frames_dir / file_path.name)) or logger.info(f"Moved {file_path} to {staging_frames_dir / file_path.name}") for file_path in largest_files]
            
            # List all files in the destination directory
            logger.info("Listing all files in the staging directory...")
            all_files = sorted(staging_frames_dir.glob('*'))
            
            # Keep every third file and remove the others
            logger.info("Keeping every fifth file and removing the others...")
            [shutil.move(str(file), str(hq_frames_dir / file.name)) or logger.info(f"Moved {file} to {hq_frames_dir / file.name}") for idx, file in enumerate(all_files) if idx % 3 == 0]
            
            # Delete all files in the staging directory and in the local_dir_frames directory
            logger.info("Removing all files in the staging directory and in the local_dir_frames directory...")
            [os.remove(file) or logger.info(f"Removed {file}") for file in staging_frames_dir.glob('*.jpg')]
            [os.remove(file) or logger.info(f"Removed {file}") for file in local_dir_frames.glob('*.jpg')]
        
        
        logger.info("Generate video...")
        video_name_export = output_video / (str(camera_name) + '_' + str(date_today) + '_fr30.mp4')
        logger.info(f"Exporting video to {video_name_export}...")
        dp.generate_video_from_images(image_folder=hq_frames_dir, 
                                      video_name = video_name_export, 
                                      codec='avc1', 
                                      frame_rate=30)
        
        # Generate the remote directory
        remote_dir = Path(cfg.ssh.pylos.remote_dir_base) / camera_name / f"{year}" / f"{month:02d}" / f"{day:02d}"
        
        dp.transfer_data_local_remote(remote_user=cfg.ssh.pylos.remote_user, 
                                      remote_host=cfg.ssh.pylos.remote_host, 
                                      remote_dir=str(remote_dir), 
                                      local_dir=str(video_name_export))
    
    
if __name__=='__main__':
    main()