from picamera import *
from detect import *
from track import *
from drone import *
from distance import *

from time import sleep
from datetime import datetime

import threading
import record 
import state
import cv2
import os
import queue

pError   = 0
altitude = 1.3

pid      = [0.5,0.4]
#pid      = [0.3,0.1

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

# Here is record section initially

# Create a queue to hold the frames
frame_queue = queue.Queue()

# Create a new thread to write the video
#rec = threading.Thread(target=write_video, args=(frame_queue,))
rec = threading.Thread(target=record.write_video, args=(frame_queue,))
rec.start()

if __name__ == "__main__":
    while True:
        try:
            drone = Drone()
            break
        
        except Exception as e:
            sleep(2)
    
    # Init PiCam
    cam = Picam()
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
                frame_queue.put(None)
                drone.control_tab.land()
                #cv2.destroyAllWindows()
                
            elif(state.get_system_state() == "end"):
                state.set_system_state("takeoff")
                state.set_airborne("off")
                
                print("Waiting to change to GUIDED Mode")
                
                while not drone.vehicle.mode.name == "GUIDED":
                    sleep(1)

                rec = threading.Thread(target=record.write_video, args=(frame_queue,))
                rec.start()

            frame_queue.put(frame)
                        
            #cv2.imshow("Capture",frame)

            if cv2.waitKey(1) & 0XFF == ord('q'):
               break
                   
        except Exception as e:
            print(str(e))
            
    # Add a None to the queue to signal the end of the video
    frame_queue.put(None)

    # Finish the thread
    rec.join()
    off.join()
    sea.join()
    tra.join()

    #cv2.destroyAllWindows()
    
