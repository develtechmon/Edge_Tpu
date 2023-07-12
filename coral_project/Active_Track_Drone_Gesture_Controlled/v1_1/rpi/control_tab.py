from dronekit import *
from pymavlink import mavutil
from time import sleep
from engines import *
import numpy as np
import state

class controlTab:
    def __init__(self,D):
        self.vehicle = D.vehicle
        self.drone = D
        self.THRESHOLD_ALT = 0.3
        self.engine = D.engines
        
        self.inputValueYaw = 0
        
        self.MAX_SPEED = 4     
        self.MAX_YAW = 15  
          
        self.takeoff_alt = 1.3
    
    ######################################### - START - ###############################################
    # Takeoff without GPS
    def armAndTakeoff_nogps(self,altitude):
        ## Constant ##
        DEFAULT_TAKEOFF_THRUST = 0.7
        SMOOTH_TAKEOFF_THRUST = 0.6
        
        mode_a = 0
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        # If you need to disable the arming check,
        # just comment it with your own responsibility.
        while not self.vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)
        
        print("Arming motors")
        # Copter should arm in GUIDED_NOGPS mode
        self.vehicle.mode = VehicleMode("GUIDED_NOGPS")
        self.vehicle.armed = True
    
        while not self.vehicle.armed:
            print("waiting for arming...")
            time.sleep(1)
            
        print("Taking off!")
        
        thrust = DEFAULT_TAKEOFF_THRUST
        while True:
            current_altitude = self.vehicle.location.global_relative_frame.alt
            print(" Altitude: %f  Desired: %f" %(current_altitude, altitude))
            if (current_altitude >= altitude*0.95 and mode_a==0 ): # Trigger just below target alt.
                print("Reached target altitude")
                mode_a = 1
                break
                        
            elif current_altitude >= altitude*0.6:
               thrust = SMOOTH_TAKEOFF_THRUST
            
            self.set_attitude(thrust = thrust)
            time.sleep(0.1)

    def send_attitude_target(self, roll_angle = 0.0, pitch_angle = 0.0,yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,thrust = 0.5):
        """
        use_yaw_rate: the yaw can be controlled using yaw_angle OR yaw_rate.
                    When one is used, the other is ignored by Ardupilot.
        thrust: 0 <= thrust <= 1, as a fraction of maximum vertical thrust.
                Note that as of Copter 3.5, thrust = 0.5 triggers a special case in
                the code for maintaining current altitude.
        """
        if yaw_angle is None:
            # this value may be unused by the vehicle, depending on use_yaw_rate
            yaw_angle = self.vehicle.attitude.yaw
        # Thrust >  0.5: Ascend
        # Thrust == 0.5: Hold the altitude
        # Thrust <  0.5: Descend
        self.msg = self.vehicle.message_factory.set_attitude_target_encode(
            0, # time_boot_ms
            1, # Target system
            1, # Target component
            0b00000000 if use_yaw_rate else 0b00000100,
            self.to_quaternion(roll_angle, pitch_angle, yaw_angle), # Quaternion
            0, # Body roll rate in radian
            0, # Body pitch rate in radian
            math.radians(yaw_rate), # Body yaw rate in radian/second
            thrust  # Thrust
        )
        self.vehicle.send_mavlink(self.msg)
                 
    def set_attitude(self,roll_angle = 0.0, pitch_angle = 0.0, yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,thrust = 0.5, duration = 0):
        self.send_attitude_target(roll_angle, pitch_angle,yaw_angle, yaw_rate, False, thrust) 
        
        start = time.time()
        while time.time() - start < duration:
            self.send_attitude_target(roll_angle, pitch_angle, yaw_angle, yaw_rate, False,thrust)
            time.sleep(0.1)
        
        # Reset attitude, or it will persist for 1s more due to the timeout
        self.send_attitude_target(0, 0,0, 0, True,thrust)
    
    def to_quaternion(self,roll = 0.0, pitch = 0.0, yaw = 0.0):
        """
        Convert degrees to quaternions
        """
        t0 = math.cos(math.radians(yaw * 0.5))
        t1 = math.sin(math.radians(yaw * 0.5))
        t2 = math.cos(math.radians(roll * 0.5))
        t3 = math.sin(math.radians(roll * 0.5))
        t4 = math.cos(math.radians(pitch * 0.5))
        t5 = math.sin(math.radians(pitch * 0.5))

        w = t0 * t2 * t4 + t1 * t3 * t5
        x = t0 * t3 * t4 - t1 * t2 * t5
        y = t0 * t2 * t5 + t1 * t3 * t4
        z = t1 * t2 * t4 - t0 * t3 * t5
        
        return [w, x, y, z]
    
    def forward_no_gps(self):
        self.set_attitude(pitch_angle = -5, thrust = 0.5, duration = 3.21)

    def backward_no_gps(self):
        self.set_attitude(pitch_angle = 5, thrust = 0.5, duration = 3)
    
    ######################################### - END - ###############################################

    ######################################### - START - ###############################################
    # Takeoff with GPS
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
            state.set_airborne("on")
            time.sleep(1)
            
    def guided(self):
        print("guided")
        self.vehicle.channels.overrides = {}
        self.vehicle.mode = VehicleMode("GUIDED")
        #state.set_system_state("end")
    
    def left(self):
        print("left")
        self.x,self.y = 0.0,-0.7
        self.z = 0
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
    
    def right(self):
        print("Go Right")
        self.x,self.y=0.0,0.7
        self.z=0
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
        
    def back(self):
        print("Go Back")
        self.x, self.y = -0.7, 0.0  # meters
        self.z = 0
                    
        # 3rd option
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
        
    def forward(self):
        # Go Front
        print("Go Front")
        self.x, self.y = 0.7, 0.0  # meters
        self.z = 0

        # 3rd option
        self.engine.executeChangesNow(self.x,self.y,self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
    
    def yaw_left(self):
        print("Yaw Left")
        self.yaw = -40
        self.engine.executeChangesNow(0, 0,self.takeoff_alt)
        self.engine.send_movement_command_YAW(self.yaw)
    
    def yaw_right(self):
        print("Yaw Right")
        self.yaw = 40
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
        print("Stop Drone")
        self.engine.executeChangesNow(0, 0, self.takeoff_alt)
        self.engine.send_movement_command_YAW(0)
        