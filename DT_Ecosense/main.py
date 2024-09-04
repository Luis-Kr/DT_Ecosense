from datetime import datetime, timedelta
from pathlib import Path
import warnings
from typing import List, Tuple
import re
import shutil
import os
import logging

# Custom imports
import utils.logger as lgr
import utils.camera as cma
import data_preprocessing as dp

# Hydra and OmegaConf imports
import hydra
from hydra import compose, initialize
from omegaconf import DictConfig

# Ignore warnings
warnings.filterwarnings("ignore")

# get the path of the current file
root_dir = Path(__file__).parent.parent.absolute()


def get_date_yesterday() -> Tuple[int, int, int]:
    """Get the date of yesterday."""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.year, yesterday.month, yesterday.day


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig) -> None:
    """Main function to orchestrate the data processing pipeline."""
    # Clear the hydra config cache
    lgr.clear_hydra_cache()
    
    date_yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    logger = lgr.setup_logger(cfg, date_yesterday)
    cams = cma.get_cameras(cfg)
    year, month, day = get_date_yesterday()
    
    for i in range(len(cams)):
        # Set up the camera directories    
        remote_dir, local_dir_mp4, local_dir_frames, output_video, camera_name = cma.setup_camera_directories(cfg, cams, i)
        
        lgr.log_separator(logger)
        logger.info(f"::: Processing camera {camera_name} :::")
        lgr.log_separator(logger)
        
        break
        
        logger.info("Transfering data from NVR to VM...")
        dp.transfer_data_remote_local(remote_user="root", 
                                      remote_host="10.6.159.52", 
                                      remote_dir=str(remote_dir), 
                                      local_dir=str(local_dir_mp4))
    
        logger.info("Extract frames...")
        frame_number = -1
        cma.rename_mp4_files(logger, local_dir_mp4)
        
        # Loop through all .mp4 files in the local_dir_mp4
        for idx, mp4_file in enumerate(sorted(local_dir_mp4.glob('*.mp4'))):
            logger.info(f"Processing file {mp4_file}...")
            frame_number = dp.extract_frames(logger=logger, 
                                             video_path=mp4_file, 
                                             output_dir=local_dir_frames, 
                                             frame_interval=10, 
                                             frame_number=frame_number)
            
            # Create the destination directory if it doesn't exist
            hq_frames_dir = Path(cfg.dst_dir) / camera_name / 'hq_frames'
            hq_frames_dir.mkdir(parents=True, exist_ok=True)
            
            cma.group_and_move_files(logger, local_dir_frames, hq_frames_dir, cfg.set_size, cfg.interval)
        
        
        logger.info("Generate video...")
        video_name_export = output_video / (str(camera_name) + '_' + str(date_yesterday) + '_fr30.mp4')
        
        logger.info(f"Exporting video to {video_name_export}...")
        dp.generate_video_from_images(image_folder=hq_frames_dir, 
                                      video_name = video_name_export, 
                                      codec='avc1', 
                                      frame_rate=30)
        
        # Generate the remote directory
        logger.info("Transfering video to Pylos...")
        remote_dir = Path(cfg.ssh.pylos.remote_dir_base) / camera_name / f"{year}" / f"{month:02d}" / f"{day:02d}"
        dp.transfer_data_local_remote(remote_user=cfg.ssh.pylos.remote_user, 
                                      remote_host=cfg.ssh.pylos.remote_host, 
                                      remote_dir=str(remote_dir), 
                                      local_dir=str(video_name_export))
        
        logger.info("::: Successfull transfer of video to Pylos. :::")
        log_separator(logger)
    
if __name__=='__main__':
    main()