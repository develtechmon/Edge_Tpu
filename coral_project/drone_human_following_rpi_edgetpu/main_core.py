from picamera import *
from detect import *
from track import *
from drone import *
from ultrasonic import *
from core import *

from time import sleep
from datetime import datetime

import threading

import state
import cv2
import os

pError   = 0
altitude = 1.3

pid      = [0.5,0.4]
#pid      = [0.3,0.1]

def record():
    #curr_timestamp = int(datetime.timestamp(datetime.now()))
    path = "/home/jlukas/Desktop/My_Project/Edge_Tpu/coral_project/drone_human_following_rpi_edgetpu/record/"
    writer= cv2.VideoWriter(path + "record" + f"{time.time()}" + '.mp4', cv2.VideoWriter_fourcc('m','p','4','v'), 10 ,(640,480))
    return writer

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

    #distance = ultrasonic(drone,altitude)
    #distance.start()
    
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

            Core.run(id,info,drone,altitude,det,writer)
                                                                            
            cv2.imshow("Capture",frame)
            writer.write(frame)

            if cv2.waitKey(1) & 0XFF == ord('q'):
               #os.system("echo 2328 | sudo -S pkill -9 -f main.py")
               break
                   
        except Exception as e:
            print(str(e))
            
    writer.release()
    cv2.destroyAllWindows()
    
