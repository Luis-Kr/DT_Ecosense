import subprocess
import multiprocessing as mp
from itertools import product
import pprint
from datetime import datetime, timedelta

def get_previous_day(day):
    #previous_date = datetime.now() - timedelta(days=1)
    previous_date = datetime(2024, 9, day)
    return (previous_date.year, previous_date.month, previous_date.day)

def run_main(date, camera_name):
    command = (
        f"python /home/geosense/Documents/DT_Ecosense/DT_Ecosense/main.py "
        f"VM.camera_name={camera_name} "
        f"VM.year={date[0]} "
        f"VM.month={date[1]} "
        f"VM.day={date[2]} "
    )
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    camera_names = ["G5Bullet_07", "G5Bullet_26", "G5Bullet_27", "G5Bullet_28", "G5Bullet_31", 
                     "G5Bullet_32", "G5Bullet_33", "G5Bullet_34", "G5Bullet_35", "G5Bullet_36", 
                     "G5Bullet_37", "G5Bullet_39", "G5Bullet_40", "G5Bullet_43", "G5Bullet_47", 
                     "G5Bullet_48"]
    
    dates = [get_previous_day(day=i) for i in list([16,17,18])]
    
    args = list(product(dates, camera_names))
        
    for arg in args:
        try:
            result = run_main(*arg)
        except Exception as e:
            print(f"Error processing task {arg}: {e}")
            
            
            
    # camera_names = ["G5Bullet_07", "G5Bullet_26", "G5Bullet_27", "G5Bullet_31", 
    #                 "G5Bullet_32", "G5Bullet_34", "G5Bullet_36", "G5Bullet_39", 
    #                 "G5Bullet_40", "G5Bullet_43"]
            
    #dates = [(2024, 9, 5), (2024, 9, 6), (2024, 9, 7), (2024, 9, 8)]
    #dates = [(2024, 9, 9), (2024, 9, 10)]
    #dates = [(2024, 9, 11), (2024, 9, 12), (2024, 9, 13), (2024, 9, 14)]
    
    # # Set the multiprocessing start method to 'spawn'
    # mp.set_start_method('spawn')
 
    # Create a pool of workers
    # with mp.Pool(1) as pool: #len(camera_names)
    #     result = pool.starmap_async(run_main, args)
    #     result.wait()