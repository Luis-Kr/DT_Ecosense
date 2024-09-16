from datetime import datetime, timedelta
from pathlib import Path
import warnings
from typing import List, Tuple
import re
import shutil
import os
import logging
import sys

# Custom imports
import utils.logger as lgr
import utils.camera as cma
import data_preprocessing as dp

# Hydra and OmegaConf imports
import hydra
from hydra import compose, initialize
from omegaconf import DictConfig

# Add the directory containing the shared library to sys.path
sys.path.append(str(Path(__file__).parent.absolute()))
import extract_frames_module

# Ignore warnings
warnings.filterwarnings("ignore")

# get the path of the current file
root_dir = Path(__file__).parent.parent.absolute()


def get_date_yesterday(cfg) -> Tuple[int, int, int]:
    """Get the date of yesterday."""
    #yesterday = datetime.now() - timedelta(days=5)
    yesterday = datetime(cfg.VM.year, cfg.VM.month, cfg.VM.day)
    return yesterday.year, yesterday.month, yesterday.day


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig) -> None:
    """Main function to orchestrate the data processing pipeline."""
    # Clear the hydra config cache
    lgr.clear_hydra_cache()
    
    #date_yesterday = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    camera_name = cfg.VM.camera_name   
    date_yesterday = datetime(cfg.VM.year, cfg.VM.month, cfg.VM.day).strftime("%Y-%m-%d")
    logger = lgr.setup_logger_VM(cfg, str(root_dir), date_yesterday, camera_name)
    year, month, day = get_date_yesterday(cfg)

    # Set up the camera directories
    date_str = f"{year}-{month:02d}-{day:02d}" 
    remote_dir, local_dir_mp4, local_dir_frames, output_video = cma.setup_camera_directories_VM(cfg, camera_name, date_str)
    
    lgr.log_separator(logger)
    logger.info(f"::: Processing camera {camera_name} :::")
    lgr.log_separator(logger)
    
    logger.info(f"Transfering data from NVR ({remote_dir}) to VM ({local_dir_mp4})...")
    dp.transfer_data_remote_local(remote_user="root", 
                                  remote_host="10.6.159.52", 
                                  remote_dir=str(remote_dir), 
                                  local_dir=str(local_dir_mp4))

    logger.info("Extract frames...")
    frame_number = 0
    cma.rename_mp4_files(logger, local_dir_mp4)
    
    # Loop through all .mp4 files in the local_dir_mp4
    for idx, mp4_file in enumerate(sorted(local_dir_mp4.glob('*.mp4'))):
        try:
            logger.info(f"Processing file {mp4_file}...")
            frame_number = dp.extract_frames(logger=logger, 
                                             video_path=mp4_file, 
                                             output_dir=local_dir_frames, 
                                             frame_number=frame_number)
            
            # # Define paths and parameters
            # video_path = str(mp4_file)
            # output_dir = str(local_dir_frames)
            
            # frame_number = extract_frames_module.extract_frames(logger, 
            #                                                     video_path, 
            #                                                     output_dir, 
            #                                                     frame_number)
            
            # Create the destination directory if it doesn't exist
            hq_frames_dir = Path(cfg.dst_dir) / camera_name / 'hq_frames'
            hq_frames_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Enhance frames...")
            cma.group_and_move_files(logger, local_dir_frames, hq_frames_dir, cfg.set_size, cfg.interval)
    
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.error("Could not process file.")
            continue
    
    logger.info("Generate video...")
    video_name_export = output_video / (str(camera_name) + '_' + str(date_yesterday) + '_fr30.mp4')
    
    logger.info(f"Exporting video to {video_name_export}...")
    
    dp.generate_video_from_images(image_folder=hq_frames_dir, 
                                  video_name=video_name_export, 
                                  codec='avc1', 
                                  frame_rate=30)
    
    # Generate the remote directory
    remote_dir = Path(cfg.ssh.pylos.remote_dir_base) / camera_name / f"{year}" / f"{month:02d}" / f"{day:02d}"
    logger.info(f"Transfering video to Pylos: {remote_dir}")
    
    # Transfer the video to Pylos
    dp.transfer_data_local_remote(remote_user=cfg.ssh.pylos.remote_user, 
                                  remote_host=cfg.ssh.pylos.remote_host, 
                                  remote_dir=str(remote_dir), 
                                  local_dir=str(video_name_export))
   
    # Clean up the high quality frames directory
    [os.remove(file) for file in hq_frames_dir.glob('*.jpg')]
    [os.remove(file) for file in local_dir_mp4.glob('*.mp4')]
    
    logger.info("::: Successful transfer of video to Pylos. :::")
    lgr.log_separator(logger)
    
if __name__=='__main__':
    main()