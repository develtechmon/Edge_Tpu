from picamera import *
from detect import *
from track import *
from drone import *
from record import *
from distance import *

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

def takeoff():
    drone.control_tab.armAndTakeoff(altitude)
    state.set_system_state("search")
    
def search(id):
    start = time.time()
    drone.control_tab.stop_drone(altitude)
    while time.time() - start < 60:
        if (id == "person"):
            state.set_system_state("track")
    state.set_system_state("land")
    
def track(info):
    if (info) != 0:
        state.set_airborne("on")
        det.track.trackobject(info,pid,pError,altitude)
      
    else:
        state.set_system_state("search")

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

    dis = Distance(drone,altitude)
    dis.start()
    
    state.set_system_state("takeoff")
    state.set_airborne("off")
    
    while drone.is_active:
        try:
            cap = cam.read()
            
            # Perform Inference
            img, id, info = det.inference(cap)   
           
            print("info >> ", info)

            # Convert HSV to RGB format
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            det.track.visualise(img,info)
           
            if (state.get_system_state() == "takeoff"):
                off = threading.Thread(target=takeoff, daemon=True)
                off.start()
            
            elif(state.get_system_state() == "search"):
                sea = threading.Thread(target=search, daemon=True, args=(id,))
                sea.start()
                
            elif(state.get_system_state() == "track"):
                tra = threading.Thread(target=track, daemon=True, args=(info,))
                tra.start()
                        
            elif(state.get_system_state() == "land"):
                drone.control_tab.land()
                #cv2.destroyAllWindows()
                
                writer.release()

            elif(state.get_system_state() == "end"):
                state.set_system_state("takeoff")
                state.set_airborne("off")
                
                print("Waiting to change to GUIDED Mode")
                
                while not drone.vehicle.mode.name == "GUIDED":
                    sleep(1)
                writer=record()
                        
            cv2.imshow("Capture",frame)
            writer.write(frame)

            if cv2.waitKey(1) & 0XFF == ord('q'):
               #os.system("echo 2328 | sudo -S pkill -9 -f main.py")
               break
                   
        except Exception as e:
            print(str(e))
            
    writer.release()

    # Finish the thread
    off.join()
    sea.join()
    tra.join()

    cv2.destroyAllWindows()
    
