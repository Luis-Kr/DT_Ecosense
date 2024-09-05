from pathlib import Path
from omegaconf import DictConfig
import logging
from typing import List, Tuple
import shutil

import os
import sys

import data_preprocessing as dp

def get_cameras(cfg: DictConfig) -> list:
    """Retrieve the list of cameras from the configuration."""
    return list(cfg.cams.items())


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


def rename_mp4_files(logger: logging.Logger, local_dir_mp4: Path) -> None:
    """Rename .mp4 files in the local directory."""
    logger.info("Renaming .mp4 files...")
    mp4_files = sorted(local_dir_mp4.glob('*.mp4'), key=lambda f: int(f.name.split('_')[-2]))
    
    for idx, mp4_file in enumerate(mp4_files):
        new_name = mp4_file.parent / f'File_{idx:03d}_{mp4_file.name}'
        mp4_file.rename(new_name)
        logger.info(f"Renamed {mp4_file} to {new_name}")
            

def group_and_move_files(logger: logging.Logger, local_dir_frames: Path, hq_frames_dir: Path, set_size: int, interval: int) -> None:
    """Group files and move the largest ones to the high-quality frames directory."""
    logger.info("Grouping files in sets...")
    largest_files = dp.find_largest_files_in_groups(dir_path=local_dir_frames, set_size=set_size)
    staging_frames_dir = local_dir_frames / 'staging'
    staging_frames_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Moving files to staging directory...")
    [shutil.move(str(file_path), str(staging_frames_dir / file_path.name)) for file_path in largest_files]
    all_files = sorted(staging_frames_dir.glob('*'))
    
    logger.info("Keeping every third file and removing the others...")
    [shutil.move(str(file), str(hq_frames_dir / file.name)) for idx, file in enumerate(all_files) if idx % interval == 0]
    [os.remove(file) for file in staging_frames_dir.glob('*.jpg')]
    [os.remove(file) for file in local_dir_frames.glob('*.jpg')]
    
    
def extract_number(file_name):
    """Extracts the first number found in the file name."""
    match = re.search(r'\d+', file_name)
    return int(match.group()) if match else float('inf')
