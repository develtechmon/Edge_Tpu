import state
import threading
import record
from time import time, sleep
from main_core import *
import cv2

class Core:
    def takeoff(self):
        self.drone.control_tab.armAndTakeoff(self.altitude)
        state.set_system_state("search")

    def search(self,id):
        start = time.time()
        self.drone.control_tab.stop_drone(self.altitude)
        while time.time() - start < 60:
            if (id == "person"):
                state.set_system_state("track")
        state.set_system_state("land")

    def track(self,info):
        if (info[1]) != 0:
            state.set_airborne("on")
            self.det.track.trackobject(info,self.pid,self.pError,self.altitude)
      
        else:
            state.set_system_state("search")

    def run(self,id,info,drone,altitude,det,writer):
        self.drone = drone
        self.altitude = altitude
        self.det = det
        self.writer = writer

        if (state.get_system_state() == "takeoff"):
            off = threading.Thread(target=self.takeoff, daemon=True)
            off.start()

        elif(state.get_system_state() == "search"):
            sea = threading.Thread(target=self.search, daemon=True, args=(id,))
            sea.start()

        elif(state.get_system_state() == "track"):
            tra = threading.Thread(target=self.track, daemon=True, args=(info,))
            tra.start()
                    
        elif(state.get_system_state() == "land"):
            self.drone.control_tab.land()
            #cv2.destroyAllWindows()
            self.writer.release

        elif(state.get_system_state() == "end"):
            state.set_system_state("takeoff")
            state.set_airborne("off")
        
            print("Waiting to change to GUIDED Mode")
        
            while not self.drone.vehicle.mode.name == "GUIDED":
                sleep(1)
            self.writer = record()


            
            

           

        
                        
