import subprocess
import multiprocessing as mp
from itertools import product
from datetime import datetime, timedelta

def get_previous_day(day=15):
    #previous_date = datetime.now() - timedelta(days=1)
    previous_date = datetime(2024, 9, day)
    return (previous_date.year, previous_date.month, previous_date.day)

# def run_main(date):
#     command = (
#         f"python /volume1/DT_Ecosense/DT_Ecosense/NVR_main.py "
#         f"NVR.year={date[0]} "
#         f"NVR.month={date[1]} "
#         f"NVR.day={date[2]} "
#     )
#     subprocess.run(command, shell=True)
    
def run_main(year, month, day):
    command = (
        f"python /volume1/DT_Ecosense/DT_Ecosense/NVR_main.py "
        f"NVR.year={year} "
        f"NVR.month={month} "
        f"NVR.day={day} "
    )
    subprocess.run(command, shell=True)

def process_task(arg):
    try:
        result = run_main(*arg)
    except Exception as e:
        print(f"Error processing task {arg}: {e}")


if __name__ == "__main__":
    dates = [get_previous_day(day=i) for i in list([23])]
    
    for arg in dates:
        try:
            result = run_main(*arg)
        except Exception as e:
            print(f"Error processing task {arg}: {e}")