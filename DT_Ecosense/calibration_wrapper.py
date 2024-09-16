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

    #dates = [(2024, 8, 31), (2024, 8, 30), (2024, 8, 29), (2024, 8, 28)]
    #dates = [(2024, 8, 27), (2024, 8, 26), (2024, 8, 25), (2024, 8, 24), (2024, 8, 23)]
    dates = [(2024, 9, 1), (2024, 9, 2), (2024, 9, 3), (2024, 9, 4), (2024, 9, 5), (2024, 9, 6), (2024, 9, 7)]
    num_workers = 10
    
    args = sorted(list(product(camera_names, dates)))
    
    for arg in args:
        run_main(arg)