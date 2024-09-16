from datetime import datetime, timedelta
from pathlib import Path
import warnings
from typing import List, Tuple
import re
import shutil
import os
import logging
import sys
import multiprocessing as mp
import numpy as np
import cv2
from pprint import pprint

# get the path of the current file
sys.path.append(str(Path(__file__).parent.parent.absolute()))
root_dir = Path(__file__).parent.parent.parent.absolute()

import utils.logger as lgr

# Hydra and OmegaConf imports
import hydra
from hydra import compose, initialize
from omegaconf import DictConfig

# Ignore warnings
warnings.filterwarnings("ignore")


def calibration(logger, img_path, mtx, dist, output_dir):
    logger.info(f"::: Calibration :::")
    logger.info(f"Loading image {img_path}...")
    img = cv2.imread(img_path)
    
    # Calibrate the image
    calibrated_image = cv2.undistort(img, mtx, dist, None, mtx)
    
    # Save the calibrated image
    filename = img_path.stem + "_calibrated.jpg"
    
    # Check if the output filename already exists
    if (output_dir / filename).exists():
        logger.info(f"Calibrated image {filename} already exists. Skipping...")
        return
    
    logger.info(f"Saving calibrated image to {output_dir / filename}...")
    cv2.imwrite(output_dir / filename, calibrated_image)
    
    logger.info("Calibration complete.")


def get_images(camera_id, year, month, day):
    # Get the image directory and output directory
    image_dir = Path(f"/mnt/gsdata/projects/ecosense/AngleCam2_0/data/raw_frames/G5Bullet_{camera_id}/{year}/{month:02d}/{day:02d}")
    output_dir = Path(f"/mnt/gsdata/projects/ecosense/AngleCam2_0/data/corrected_frames/G5Bullet_{camera_id}/{year}/{month:02d}/{day:02d}")
    
    # Get the images
    pattern = re.compile(r'G5Bullet_\d{2}_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.jpg')
    images = [f for f in image_dir.glob('*.jpg') if pattern.match(f.name)]
    
    return images, output_dir

@hydra.main(version_base=None, config_path="../../config", config_name="main")
def main(cfg) -> None:
    # Clear the hydra config cache
    lgr.clear_hydra_cache()
    
    date = datetime(cfg.calibration.year, cfg.calibration.month, cfg.calibration.day).strftime("%Y-%m-%d")
    logger = lgr.logger_setup('main', Path(cfg.calibration.log_dir) / str(cfg.calibration.camera_name) / f"{date}.log")
    
    lgr.log_separator(logger)
    logger.info(f"::: Processing camera {cfg.calibration.camera_name} :::")
    lgr.log_separator(logger)
    
    logger.info("Getting images...")
    mtx = np.load(root_dir / "data" / "calibration_matrix" / "mtx.npy")
    dist = np.load(root_dir / "data" / "calibration_matrix" / "dist.npy")
    images, output_dir = get_images(cfg.calibration.camera_name, cfg.calibration.year, cfg.calibration.month, cfg.calibration.day)
    
    args = [(logger, img, mtx, dist, output_dir) for img in images]
    
    with mp.Pool(cfg.calibration.num_workers) as pool:
        result = pool.starmap_async(calibration, args)
        result.wait()
    

if __name__ == "__main__":
    main()