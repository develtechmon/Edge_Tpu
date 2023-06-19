from dronekit import *
from pymavlink import mavutil
from time import sleep
from engines import *
import numpy as np
#import state

class controlTab:
    def __init__(self,D):
        self.vehicle = D.vehicle
        self.drone = D
        self.THRESHOLD_ALT = 0.3
        self.engine = D.engines
        
        self.inputValueYaw = 0
        
        self.MAX_SPEED = 4       # M / s
        self.MAX_YAW = 15  
          
        self.takeoff_alt = 1.3
          
    def armAndTakeoff(self,altitude):
        print("Setting ground speed to 3")
        self.vehicle.groundspeed = 3
        
        print("Basic pre-arm checks")
        
        while not self.vehicle.is_armable:
            print("waiting for vehicle to initialize")
            time.sleep(1)
            
        print("Arming Motors")
        
        self.vehicle.mode  = VehicleMode("GUIDED")
        self.vehicle.armed = True
        
        while not self.vehicle.armed:
            print("waiting for arming...")
            time.sleep(1)
        
        print("Taking off")
        self.vehicle.simple_takeoff(altitude)
        
        while True:
            #print (" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            if self.vehicle.location.global_relative_frame.alt>=altitude*0.95:
                #print ("Reached target altitude")
                break
            time.sleep(1)
            
    def guided(self):
        print("guided")
        self.vehicle.channels.overrides = {}
        self.vehicle.mode = VehicleMode("GUIDED")
        #state.set_system_state("end")
    
    def left(self):
        print("left")
        self.x,self.y = 0.0,-0.5
        self.z = 0
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
    
    def right(self):
        print("Go Right")
        self.x,self.y=0.0,0.5
        self.z=0
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
        
    def back(self):
        print("Go Back")
        self.x, self.y = -0.5, 0.0  # meters
        self.z = 0
                    
        # 3rd option
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
        
    def forward(self):
        # Go Front
        print("Go Front")
        self.x, self.y = 0.5, 0.0  # meters
        self.z = 0

        # 3rd option
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
    
    def yaw_left(self):
        print("Yaw Left")
        self.yaw = -25
        self.engine.executeChangesNow(0, 0,self.takeoff_alt)
        self.engine.send_movement_command_YAW(self.yaw)
    
    def yaw_right(self):
        print("Yaw Right")
        self.yaw = 25
        self.engine.executeChangesNow(0, 0,self.takeoff_alt)
        self.engine.send_movement_command_YAW(self.yaw)
           
    def land(self):
        print("Landing")
        self.vehicle.channels.overrides = {}
        self.vehicle.mode = VehicleMode("LAND")
        #state.set_system_state("end")

    def goHome(self):
        print('Going Home')
        self.vehicle.mode = VehicleMode("RTL")
        
    def stop_drone(self):
        self.engine.executeChangesNow(0, 0, self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
        