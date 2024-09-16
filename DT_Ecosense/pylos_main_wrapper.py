import subprocess
import multiprocessing as mp
from itertools import product

def run_main(args):
    command = (
        f"python /home/lk1167/DT_Ecosense/DT_Ecosense/Pylos_main.py "
        f"pylos.camera_name={args[1]} "
        f"pylos.year={args[0][0]} "
        f"pylos.month={args[0][1]} "
        f"pylos.day={args[0][2]} "
    )
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    camera_names = ["G5Bullet_07", "G5Bullet_26", "G5Bullet_27", "G5Bullet_31", 
                    "G5Bullet_32", "G5Bullet_34", "G5Bullet_36", "G5Bullet_39", 
                    "G5Bullet_40", "G5Bullet_43"]
    
    # camera_names = ["G5Bullet_07", "G5Bullet_26", "G5Bullet_27", "G5Bullet_28", "G5Bullet_31", 
    #                 "G5Bullet_32", "G5Bullet_33", "G5Bullet_34", "G5Bullet_35", "G5Bullet_36", 
    #                 "G5Bullet_37", "G5Bullet_39", "G5Bullet_40", "G5Bullet_43", "G5Bullet_47", 
    #                 "G5Bullet_48"]
    
    #dates = [(2024, 8, 31), (2024, 8, 30), (2024, 8, 29), (2024, 8, 28)]
    #dates = [(2024, 8, 26), (2024, 8, 25), (2024, 8, 24), (2024, 8, 23), (2024, 9, 4)]
    dates = [(2024, 9, 3), (2024, 9, 4), (2024, 9, 5), (2024, 9, 6), (2024, 9, 7)]
    
    args = sorted(list(product(dates, camera_names)))

    # Set the multiprocessing start method to 'spawn'
    mp.set_start_method('spawn')

    # Create a pool of workers
    with mp.Pool(1) as pool: #len(camera_names)
        pool.map(run_main, args)
        

# New cameras
#"G5Bullet_28", "G5Bullet_33", "G5Bullet_35", "G5Bullet_37", "G5Bullet_47", "G5Bullet_48"