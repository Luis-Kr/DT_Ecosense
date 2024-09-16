from pathlib import Path
import subprocess
import logging
from omegaconf import DictConfig
from typing import Tuple, List, Dict
from multiprocessing import Pool

# Custom imports
import utils.logger as lgr


def convert_single_camera(args):
    # Unpack the arguments
    cfg, logger, year, month, day, camera_name, cam_mac_address = args
    #src_dir, dst_dir = get_camera_paths(cfg, year, month, day, camera_name)
    
    search_pattern = f"{cam_mac_address}_0_rotating*.ubv"
    src_dir = Path(cfg.NVR.src_dir) / str(year) / f"{month:02}" / f"{day:02}"
    dst_dir = Path(cfg.NVR.dst_dir) / f"{year}-{month:02}-{day:02}" / camera_name
    
    lgr.log_separator(logger)
    logger.info(f"::: Processing camera {camera_name} with MAC address {cam_mac_address} :::")
    logger.info(f"Source directory: {src_dir}")
    logger.info(f"Destination directory: {dst_dir}")
    lgr.log_separator(logger)
    
    # Initialize the prefix counter
    prefix_counter = 1
    
    if not dst_dir.exists():
        dst_dir.mkdir(parents=True)

    # Loop through each matching file in the source directory
    for file in sorted(Path(src_dir).glob(search_pattern)):
        
        # Define the destination directory with the incrementing prefix
        current_dst_dir = dst_dir / f"{camera_name}_{cam_mac_address}_{year}-{month:02d}-{day:02d}_{prefix_counter}"

        # Run the command for each file
        subprocess.run([
            "/usr/share/unifi-protect/app/node_modules/.bin/ubnt_ubvexport",
            "-s", str(file),
            "-d", str(current_dst_dir)
        ], capture_output=True)

        # Log success message
        logger.info(f"Successfully converted {file} to {current_dst_dir}")

        # Increment the prefix counter
        prefix_counter += 1


def convert_videos(cfg: DictConfig, logger: logging.Logger, year: int, month: int, day: int, cameras: list) -> None:
    with Pool(processes=1) as pool:
        pool.map(convert_single_camera, [(cfg, logger, year, month, day, camera_name, cam_mac_address) for camera_name, cam_mac_address in cameras])






#---------------------------------#
# Old code

# def convert_videos(logger: logging.Logger, src_dir: Path, dest_dir: Path, camera_name: str, cam_mac_address: str) -> None:
#     # Initialize the prefix counter
#     prefix_counter = 1
    
#     search_pattern = f"{cam_mac_address}_0_rotating*.ubv"

#     # Loop through each matching file in the source directory
#     for file in Path(src_dir).glob(search_pattern):
        
#         # Define the destination directory with the incrementing prefix
#         current_dest_dir = dest_dir / f"{camera_name}_{cam_mac_address}_{prefix_counter}"

#         # Run the command for each file
#         subprocess.run([
#             "/usr/share/unifi-protect/app/node_modules/.bin/ubnt_ubvexport",
#             "-s", str(file),
#             "-d", str(current_dest_dir)
#         ], capture_output=True)

#         # Log success message
#         logger.info(f"Successfully converted {file} to {current_dest_dir}")

#         # Increment the prefix counter
#         prefix_counter += 1


# def get_camera_paths(cfg: DictConfig, year: int, month: int, day: int, camera_name: str) -> Tuple[Path, Path]:
#     src_dir = Path(cfg.NVR.src_dir) / str(year) / f"{month:02}" / f"{day:02}"
#     dst_dir = Path(cfg.NVR.dst_dir) / camera_name
    
#     # Create the destination directory if it does not exist
#     if not dst_dir.exists():
#         dst_dir.mkdir(parents=True)
    
#     return src_dir, dst_dir


