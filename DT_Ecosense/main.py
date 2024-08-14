from datetime import datetime
from pathlib import Path
import warnings

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


@hydra.main(version_base=None, config_path="../config", config_name="main")
def main(cfg: DictConfig):
    # Clear the hydra config cache
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    date_today = datetime.now().strftime("%Y-%m-%d")
    lgr.check_path(root_dir / cfg.dst_dir)
    
    # Set up the logger
    logger = lgr.logger_setup('main', root_dir / cfg.paths.logger.dst_dir / f"{date_today}.log")
    
    # logger.info("Grouping files in sets...")
    # largest_files = dp.find_largest_files_in_groups(dir_path=cfg.raw_data, set_size=cfg.set_size)
    
    # logger.info("Extracting camera metadata and subsampling the data...")
    # filenames = dp.extract_camera_metadata(output_dir=root_dir / cfg.dst_dir, image_paths=largest_files)
    
    logger.info("Extract frames...")
    frames_dir, video_timelapse_dir, camera_name, date = dp.extract_frames(video_path=root_dir / cfg.raw_video_path, 
                                                                            output_dir=root_dir / cfg.dst_dir, 
                                                                            frame_interval=30)
    
    logger.info("Generate video...")
    dp.generate_video_from_images(image_folder=frames_dir, 
                                  video_name=video_timelapse_dir / ("Camera_"+ camera_name + '_' + date + '_' + 'timelapse.mp4'), 
                                  codec='avc1', 
                                  frame_rate=120)
    
    
if __name__=='__main__':
    main()