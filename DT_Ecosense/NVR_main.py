from datetime import datetime
from pathlib import Path
import warnings
from typing import Tuple, List, Dict

# Custom imports
import utils.logger as lgr
import utils.convert_video as cvv
#import data_preprocessing as dp

# Hydra and OmegaConf imports
import hydra
from hydra import compose, initialize
from omegaconf import DictConfig

# Ignore warnings
warnings.filterwarnings("ignore")

# get the path of the current file
root_dir = Path(__file__).parent.parent.absolute()


def get_camera_paths(cfg: DictConfig, cam: Tuple[str, str], year: int, month: int, day: int) -> Tuple[Path, Path, str, str]:
    camera_name, cam_mac_address = cam
    src_dir = Path(cfg.NVR.src_dir) / str(year) / f"{month:02}" / f"{day:02}"
    dst_dir = Path(cfg.NVR.dst_dir) / camera_name
    
    # Create the destination directory if it does not exist
    if not dst_dir.exists():
        dst_dir.mkdir(parents=True)
    
    return src_dir, dst_dir, camera_name, cam_mac_address


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig):
    # Clear the hydra config cache
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    
    # Get the list of cameras
    cams = list(cfg.cams.items())
    
    # Get the date of today
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    
    # Set up the logger
    logger = lgr.logger_setup('main', root_dir / cfg.paths.logger.dst_dir_NVR / f"NVR_{year}_{month:02}_{day:02}.log")
    
    cvv.convert_videos(cfg=cfg, logger=logger, year=year, month=month, day=day, cameras=cams)
    
    
    # for i in range(len(cams)):
    #     # Get the source and destination directories
    #     src_dir, dst_dir, camera_name, cam_mac_address = get_camera_paths(cfg, cams[i], year, month, day)
        
    #     logger.info("-----------------------------------")
    #     logger.info(f"Processing camera {camera_name} with MAC address {cam_mac_address}")
    #     logger.info(f"Source directory: {src_dir}")
    #     logger.info(f"Destination directory: {dst_dir}")
    #     logger.info("-----------------------------------")
        
    #     # print(f"Processing camera {camera_name} with MAC address {cam_mac_address}")
    #     # print(f"Source directory: {src_dir}")
    #     # print(f"Destination directory: {dst_dir}")
        
    #     cvv.convert_videos(logger=logger,
    #                        src_dir=src_dir, 
    #                        dest_dir=dst_dir, 
    #                        camera_name=camera_name, 
    #                        cam_mac_address=cam_mac_address)
        

if __name__=='__main__':
    main()