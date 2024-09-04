import logging 
from pathlib import Path
import hydra
from hydra import compose, initialize
from omegaconf import DictConfig
from typing import List, Tuple

formatter = logging.Formatter('%(asctime)s - Module(%(module)s):Line(%(lineno)d) %(levelname)s - %(message)s')

def check_path(inp_path):
    """
    Check if a given path exists, and create it if it doesn't.

    Parameters
    ----------
    inp_path : str
        The path to check/create.

    Returns
    -------
    None
    """
    
    # Create a Path object from the input path
    inp_path_obj = Path(inp_path)
    
    # Check if the path exists
    if not inp_path_obj.exists():
        # If not, create the directories in the path
        inp_path_obj.mkdir(parents=True)
        

def logger_setup(name, log_file, level=logging.INFO):
    """
    Set up a logger with a specified name, log file, and logging level.

    Parameters
    ----------
    name : str
        The name of the logger.
    log_file : str
        The path to the log file.
    level : int, optional
        The logging level. By default, logging.INFO.

    Returns
    -------
    logger : logging.Logger
        The configured logger.
    """
    # Check if the parent directory of the log file exists, create it if not
    check_path(log_file.parent)

    # Create a file handler for writing log messages to a file
    handler = logging.FileHandler(log_file, mode='a')        
    handler.setFormatter(formatter)

    # Get a logger with the specified name
    logger = logging.getLogger(name)
    
    # Set the logging level for the logger
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def clear_hydra_cache() -> None:
    """Clear the Hydra config cache."""
    hydra.core.global_hydra.GlobalHydra.instance().clear()


def log_separator(logger: logging.Logger) -> None:
    """Log separator lines to the provided logger."""
    separator = "--------------------------------------------------"
    logger.info(separator)
    logger.info(separator)
    
    
def setup_logger(cfg: DictConfig, date_today: str) -> logging.Logger:
    """Set up the logger."""
    root_dir = Path(cfg.paths.logger.dst_dir)
    log_file = root_dir / f"{date_today}.log"
    return logger_setup('main', log_file)