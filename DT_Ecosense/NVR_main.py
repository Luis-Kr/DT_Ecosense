from datetime import datetime, timedelta
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

def get_date_yesterday(cfg: DictConfig) -> Tuple[int, int, int]:
    """Get the date of yesterday."""
    #yesterday = datetime.now() - timedelta(days=4)
    # Starting 2024-09-14 include the new cameras!!!
    #yesterday = datetime(cfg.NVR.year, cfg.NVR.month, cfg.NVR.day)
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.year, yesterday.month, yesterday.day


def get_camera_paths(cam: Tuple[str, str]) -> Tuple[str, str]:
    camera_name, cam_mac_address = cam
    # src_dir = Path(cfg.NVR.src_dir) / str(year) / f"{month:02}" / f"{day:02}"
    # dst_dir = Path(cfg.NVR.dst_dir) / f"{year}-{month:02}-{day:02}" / camera_name
    
    # # Create the destination directory if it does not exist
    # if not dst_dir.exists():
    #     dst_dir.mkdir(parents=True)
    
    return camera_name, cam_mac_address


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig):
    # Clear the hydra config cache
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    
    # Get the list of cameras
    cams = list(cfg.cams.items())
    
    # Get the date of today
    year, month, day = get_date_yesterday(cfg)
    
    # Set up the logger
    logger = lgr.logger_setup('main', root_dir / cfg.paths.logger.dst_dir_NVR / f"NVR_{year}_{month:02}_{day:02}.log")
    
    cvv.convert_videos(cfg=cfg, 
                       logger=logger, 
                       year=year, 
                       month=month, 
                       day=day, 
                       cameras=cams)
        

if __name__=='__main__':
    main()