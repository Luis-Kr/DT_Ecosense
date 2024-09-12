import subprocess
from itertools import product

def run_main(args):
    command = (
        f"python /home/lk1167/DT_Ecosense/DT_Ecosense/utils/calibration.py "
        f"calibration.camera_name={args[0]} "
        f"calibration.year={args[1][0]} "
        f"calibration.month={args[1][1]} "
        f"calibration.day={args[1][2]} "
    )
    subprocess.run(command, shell=True)
    
if __name__ == "__main__":
    camera_names = ["07", "26", "27", "31", "32", "34", "36", "39", "40", "43"]

    dates = [(2024, 8, 31), (2024, 8, 30), (2024, 8, 29), (2024, 8, 28)]
    num_workers = 4
    
    args = sorted(list(product(camera_names, dates)))
    
    for arg in args:
        run_main(arg)