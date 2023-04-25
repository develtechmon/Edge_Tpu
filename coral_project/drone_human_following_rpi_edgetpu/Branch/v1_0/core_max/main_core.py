from picamera import *
from detect import *
from track import *
from drone import *
from record import *
from distance import *
from cores import *

from time import sleep
from datetime import datetime

import state
import cv2
import os

pError   = 0
altitude = 1.3

pid      = [0.5,0.4]
#pid      = [0.3,0.1]

if __name__ == "__main__":
    while True:
        try:
            drone = Drone()
            break
        
        except Exception as e:
            sleep(2)
    
    # Init PiCam
    cam = Picam()

    writer = record()

    det = Detect(cam,drone)
    
    core = Cores()

    dis = Distance(drone,altitude)
    dis.start()

    state.set_system_state("takeoff")
    state.set_airborne("off")
    
    while drone.is_active:
        try:
            cap = cam.read()
            
            # Perform Inference
            img, id, info = det.inference(cap)   
            
            # Convert HSV to RGB format
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            det.track.visualise(img,info)

            core.run(id,info,drone,altitude,det,writer)
                                                                            
            cv2.imshow("Capture",frame)
            writer.write(frame)

            if cv2.waitKey(1) & 0XFF == ord('q'):
               #os.system("echo 2328 | sudo -S pkill -9 -f main.py")
               break
                   
        except Exception as e:
            print(str(e))
            
    writer.release()
    cv2.destroyAllWindows()
    
