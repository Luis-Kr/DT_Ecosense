from datetime import datetime, timedelta
from pathlib import Path
import warnings
from typing import List, Tuple
import re
import shutil
import os
import logging
import sys
import concurrent.futures
import multiprocessing

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
    #yesterday = datetime.now() - timedelta(days=5)
    yesterday = datetime(2024, 9, 2)
    return yesterday.year, yesterday.month, yesterday.day


def process_camera(args):
    base_dir, logger, year, month, day, camera = args
    date_str = f"{year}-{month:02d}-{day:02d}"  
    camera_name, _ = camera  
    
    lgr.log_separator(logger)
    logger.info(f"::: Processing camera {camera_name} :::")
    lgr.log_separator(logger)
    
    raw_video_dir = Path(base_dir) / "raw_videos" / f"{camera_name}" / f"{year}" / f"{month:02d}" / f"{day:02d}" / f"{camera_name}_{date_str}_fr30.mp4"
    raw_frames_dir = Path(base_dir) / "raw_frames" / f"{camera_name}" / f"{year}" / f"{month:02d}" / f"{day:02d}"
    
    logger.info(f"Extracting frames from {raw_video_dir}...")
    _ = dp.extract_all_frames(logger=logger, 
                              video_path=raw_video_dir, 
                              output_dir=raw_frames_dir)
    
    # # Create a pool of worker processes
    # with multiprocessing.Pool(processes=1) as pool:
    #     # Prepare the arguments for each process
    #     args = [(cfg.pylos.base_dir, logger, year, month, day, cam) for cam in cams]
        
    #     # Map the process_camera function to the list of arguments
    #     pool.map(process_camera, args)
    
    #with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
    #     futures = [executor.submit(process_camera, cfg, logger, year, month, day, cam) for cam in cams]
    #     for future in concurrent.futures.as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             logger.error(f"Error processing camera: {e}")


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig) -> None:
    # Clear the hydra config cache
    lgr.clear_hydra_cache()
    
    date_yesterday = datetime(2024, 9, 2).strftime("%Y-%m-%d")
    logger = lgr.logger_setup('main', Path(cfg.pylos.log_dir) / f"{date_yesterday}.log")
    cams = cma.get_cameras(cfg)
    year, month, day = get_date_yesterday()
    
    # extract frames
    for i in range(len(cams)):
        try:
            # Set up the camera directories
            date_str = f"{year}-{month:02d}-{day:02d}"  
            camera_name, cam_mac_address = cams[i]  
            #remote_dir, local_dir_mp4, local_dir_frames, output_video, camera_name = cma.setup_camera_directories(cfg, cams, i, date_str)
            
            lgr.log_separator(logger)
            logger.info(f"::: Processing camera {camera_name} :::")
            lgr.log_separator(logger)
            
            raw_video_dir = Path(cfg.pylos.base_dir) / "raw_videos" / f"{camera_name}" / f"{year}" / f"{month:02d}" / f"{day:02d}" / f"{camera_name}_{date_str}_fr30.mp4"
            raw_frames_dir = Path(cfg.pylos.base_dir) / "raw_frames" / f"{camera_name}" / f"{year}" / f"{month:02d}" / f"{day:02d}"
            
            logger.info(f"Extracting frames from {raw_video_dir}...")
            _ = dp.extract_all_frames(logger=logger, 
                                    video_path=raw_video_dir, 
                                    output_dir=raw_frames_dir)
        except Exception as e:
            logger.error(f"Error processing camera: {e}")
            continue
    
#     # apply transformation matrix
    
    
#     sys.exit()
    
    
    
    
if __name__=='__main__':
    main()
    
    