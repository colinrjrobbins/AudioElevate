import os
import time

check = 0

def programStart():
        os.system("sudo python3 /home/pi/Desktop/audioElevate.py")
        time.sleep(5)

while check != 1:
    programStart()
