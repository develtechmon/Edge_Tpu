from picamera import *
from detect import *
from track import *
from drone import *
from time import sleep
from datetime import datetime

import state
import cv2
import os

imW, imH = 640,480

pError   = 0
altitude = 1.5

pid      = [0.5,0.4]

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
    #print(info[1])
    if (info[1]) != 0:
        state.set_airborne("on")
        #det.track.trackobject(info,pid,pError,altitude)
        track.trackobject(info,pid,pError,altitude)

    else:
        state.set_system_state("search")
        state.set_time(120)

if __name__ == "__main__":
    while True:
        try:
            drone = Drone()
            break
        
        except Exception as e:
            print(str(e))
            sleep(2)
    
    # Init PiCam
    cam = Picam()
    curr_timestamp = int(datetime.timestamp(datetime.now()))
    
    path = "/home/jlukas/Desktop/My_Project/Jetson_Nano/Projects/Autonomous_Human_Follower_Drone/record/"
    writer= cv2.VideoWriter(path + "record" + str(curr_timestamp) + '.mp4', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 120 ,(cam.DISPLAY_WIDTH,cam.DISPLAY_HEIGHT))

    # det   = Detect(cam,drone)
    det = Detect(cam,Drone)
    
    state.set_system_state("takeoff")
    state.set_airborne("off")
    
    while drone.is_active:
        try:
            
            cap = cam.read()
            
            # Perform Inference
            img, id, info = det.inference(cap)   
            
            det.track.visualise(img,info)
            
            if (state.get_system_state() == "takeoff"):
                off = threading.Thread(target=takeoff)
                off.start()
            
            elif(state.get_system_state() == "search"):
                state.set_time(120)
                sea = threading.Thread(target=search, args=(id,))
                sea.start()
                
            elif(state.get_system_state() == "track"):
                state.set_time(120)
                tra = threading.Thread(target=track, args=(info,))
                tra.start()
                        
            elif(state.get_system_state() == "land"):
                drone.control_tab.land()
                writer.release()
                cv2.destroyAllWindows()

            elif(state.get_system_state() == "end"):
                print("Program End !")  
                state.set_system_state("takeoff")
                state.set_airborne("off")
                
                print("Waiting to change to GUIDED Mode")
                
                while not drone.vehicle.mode.name == "GUIDED":
                    sleep(1)
                     
            writer.write(img)
            #cv2.imshow("Capture",img)
            
            if cv2.waitKey(1) & 0XFF == ord('q'):
               os.system("echo 2328 | sudo -S pkill -9 -f main.py")
               break
                   
        except Exception as e:
            print(str(e))
            
    writer.release()  
    