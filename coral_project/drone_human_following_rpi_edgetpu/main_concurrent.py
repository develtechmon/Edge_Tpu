from picamera import *
from detect import *
from track import *
from drone import *
from ultrasonic import *

from time import sleep
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor

import state
import cv2
import os

pError   = 0
altitude = 1.5

#pid      = [0.5,0.4]
pid      = [0.3,0.1]

def takeoff():
    drone.control_tab.armAndTakeoff(altitude)
    state.set_system_state("search")
    
def search(id):
    start = time.time()
    drone.control_tab.stop_drone(altitude)
    while time.time() - start < state.get_time():
        if (id == "person"):
            state.set_system_state("track")
    state.set_system_state("land")
    
def track(info):
    if (info[1]) != 0:
        state.set_airborne("on")
        det.track.trackobject(info,pid,pError,altitude)
      
    else:
        state.set_system_state("search")
        state.set_time(60)

def record():
    #curr_timestamp = int(datetime.timestamp(datetime.now()))
    path = "/home/jlukas/Desktop/My_Project/Edge_Tpu/coral_project/drone_human_following_rpi_edgetpu/record/"
    writer= cv2.VideoWriter(path + "record" + f"{time.time()}" + '.mp4', cv2.VideoWriter_fourcc('m','p','4','v'), 10 ,(640,480))
    return writer

def write(frame):
    writer.write(frame)

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
    
    executor = ThreadPoolExecutor(12)

    while drone.is_active:
        try:
            cap = cam.read()
            
            # Perform Inference
            img, id, info = det.inference(cap)   
            
            # Convert HSV to RGB format
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            det.track.visualise(img,info)
           
            if (state.get_system_state() == "takeoff"):
                off = executor.submit(takeoff)
            
            if(state.get_system_state() == "search"):
                state.set_time(60)
                sea = executor.submit(search,id)
                
            if(state.get_system_state() == "track"):
                state.set_time(60)
                tra = executor.submit(track,info)
                        
            if(state.get_system_state() == "land"):
                drone.control_tab.land()
                #cv2.destroyAllWindows()
                writer.release()

            if(state.get_system_state() == "end"):
                state.set_system_state("takeoff")
                state.set_airborne("off")
                
                print("Waiting to change to GUIDED Mode")
                
                while not drone.vehicle.mode.name == "GUIDED":
                    sleep(1)
                writer=record()
            
            #print(state.get_system_state())
            
            #cv2.imshow("Capture",frame)
            writer.write(frame)

            #wri = threading.Thread(target=write,daemon=True,args=(frame,))
            #wri.start()
            
            if cv2.waitKey(1) & 0XFF == ord('q'):
               #os.system("echo 2328 | sudo -S pkill -9 -f main.py")
               break
                   
        except Exception as e:
            print(str(e))
            
    writer.release()
    #cv2.destroyAllWindows()
    
