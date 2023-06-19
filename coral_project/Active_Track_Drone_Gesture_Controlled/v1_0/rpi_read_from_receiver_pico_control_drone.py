"""
Author : Lukas Johnny
Date : 23/8/2022
Description : This script is used to establish the connection between RPI to Arduino using RX and TX
             Arduino : Tx --Connect -- Rpi : Rx
             Arduino : Rx --Connect -- Rpi : Tx
             
             and also using Arduino port

             Before running this code do ensure to:
             1. sudo raspi-config and enable SPI
             2. disable Serial login shell connection and enable Serial interface connection
             3. go to sudo vi /boot/config.txt -last line. Disable bluetooth using this command
             "dtoverlay=disable-bt"
             4. Reboot the Pi
             5. if ttyAMAO is not in dev, please enable_uart=1 in /boot/config too.
             6. ttyAMAO is serial protocol to connect PI and Arduino
             
             This script will extract data from Arduino Receiver and send those data into RPI which
             will be read by this script. 
             
             This script will then classify those data and command Pixhawk controller to execute 
             Copter function based in MAVLink connection
             
             Below is Key input from Python and Arduino and its function
             Keyboard : Arduino : Function
               g           g     : GUIDED Mode
               h           h     : STABILIZE Mode
               UP          u     : TAKEOFF Mode
               d           d     : Go Right
               a           a     : Go Left
               w           w     : Move Front
               s           s     : Move backward
               q           q     : LAND Mode
               e           e     : Freeze
               r           r     : Reset
               LEFT        n     : Yaw left
               RIGHT       m     : Yaw Right
                           
"""
import serial
from time import sleep
import numpy as np
import os
from dronekit import *
from dronekit_engine_for_rpi import *
import threading

class readdatafromArdtoRpi:
    def __init__(self):
        try:       
            '''RPI'''
            #self.connection_string = '/dev/ttyAMA0,921600'

            '''Gazebo'''
            self.connection_string = '192.168.8.146:14553'

            '''SiTL'''
            #self.connection_string = '127.0.0.1:14550'

            '''ZeroTier'''
            #self.connection_string = '192.168.8.141:14553'

            #self.buzzer  = Buzzer(23)
            self.vehicle = connect(self.connection_string, wait_ready=True)
            print("Virtual Copter is Ready")

        except socket.error:
            print("Failed to connect to Vehicle")
            
        self.engine = Engine_Improve(self)
        self.engine.start()
        self.THRESHOLD_ALT = 0.3
        self.mode_g   = 0
        self.mode_l   = 0
        self.mode_s   = 0
        self.count    = 0
        self.takeoff  = False
        self.takeoff_alt = 1.5
        self.yaw = 0
    
    # Connect to Pico
    def initConnection(self,portNo, baudRate):
        try:
            ser = serial.Serial(portNo, baudRate)
            print("Device Connected")
            return ser
        except:
            print("Not connected")

    # Extract data from Pico NRF - Receiver
    def getData(self,ser):
        try:
            data = ser.readline()
            data = data.decode("utf-8")
            data = data.split()
            data = data[0]
            return data
                 
        except:
            pass
    
    sleep(0.25)
                 
    def getKeyboardInput(self,kp):
        # Set into Guided Mode
        if (kp =='g'): 
            print("Guided Mode")
            self.mode_g +=1        
            if self.mode_g < 2:
                print("Vehicle Mode : Guided") 
                @self.vehicle.on_attribute('mode')
                def mode_callback(self,attr_name, value):
                    print(f">> Mode Updated: {value}")
                
                print("Setting ground speed to 3")
                self.vehicle.groundspeed = 3
                
                # We will not let the script to continue unless it changes to GUIDED
                self.vehicle.mode = VehicleMode("GUIDED")
                while not self.vehicle.mode.name == "GUIDED":
                    sleep(1)
                    
                self.mode_s   = 0
                self.mode_l   = 0
                
                if (self.vehicle.mode.name == "GUIDED"):
                    if not self.vehicle.armed:
                        self.vehicle.armed = True
                        print("Waiting to take off")
                        
                else:
                    # Disarm if landed
                    if (self.vehicle.location.global_relative_frame.alt < self.THRESHOLD_ALT):
                        self.vehicle.armed = False
                        self.takeoff = False
                        print("Vehicle Mode : Disarmed")
                        
        if (kp == 'h'):
            print("Stabilized Mode")
            @self.vehicle.on_attribute('mode')
            def mode_callback(self,attr_name, value):
                print(f">> Mode Updated: {value}")
                
            self.vehicle.mode = VehicleMode("STABILIZE")
            print("Vehicle Mode : Stabilize")

            self.mode_s += 1
            if self.mode_s < 2:
                print("Warning : Reset Vehicle State")
                self.mode_g = 0
                self.mode_l = 0
                self.count = 0

            while not self.vehicle.mode.name == "STABILIZE":
                sleep(1)
                
        # Go Up
        if (kp == 'u') and self.vehicle.armed :
            print("Take Off")
            self.count +=1    
            if self.count < 2:     
                print("Vehicle Mode : Take Off")
                if (self.vehicle.location.global_relative_frame.alt < self.THRESHOLD_ALT):
                    
                    self.vehicle.simple_takeoff(self.takeoff_alt)         
                    
                    while True:
                        current_high = self.vehicle.location.global_relative_frame.alt
                        print(f"Altitude : {current_high}")
                        
                        if current_high >= self.takeoff_alt * 0.95:
                            print("Altitude Reached")
                            self.takeoff = False
                            
                            #self.buzzer.beep()
                            #self.buzzer.on()
                            #sleep(1)
                            #self.buzzer.off()
                            #sleep(1)
                            
                            break
                        sleep(1)
                    
                else:
                    if (self.vehicle.location.global_relative_frame.alt > self.THRESHOLD_ALT):
                        self.vehicle.mode = VehicleMode("LAND")
            
        # Go Right
        if (kp == 'd') and self.vehicle.armed:
            print("Go Right")
            self.x,self.y=0.0,0.5
            self.z=0
            self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)
            self.engine.send_movement_command_YAW(0)
  
        # Go Left
        if (kp == 'a') and self.vehicle.armed:
            print("Go Left")
            self.x,self.y = 0.0, -0.5 
            self.z=0
            self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)
            self.engine.send_movement_command_YAW(0)
            
        # Go Back
        if (kp == 's') and self.vehicle.armed:
            print("Go Back")
            self.x, self.y = -0.5, 0.0  # meters
            self.z = 0
                        
            # 3rd option
            self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)
            self.engine.send_movement_command_YAW(0)
          
        # Go Front
        if (kp == 'w') and self.vehicle.armed:
            print("Go Front")
            self.x, self.y = 0.5, 0.0  # meters
            self.z = 0

            # 3rd option
            self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)
            self.engine.send_movement_command_YAW(0)
            
        # Land   
        if (kp == 'l') and self.vehicle.armed:
            print("Land")
            self.mode_l +=1
            if self.mode_l < 2:
                self.vehicle.armed = False
                self.takeoff = False
                self.mode_g = 0
                self.count = 0
                
                self.vehicle.channels.overrides = {}
                self.vehicle.mode = VehicleMode("LAND")
                print("Vehicle Mode : Land")
                #os.system("echo 2328 | sudo -S pkill -9 -f send_keyboard_data_to_RPI.py")

                self.mode_s += 1
                if self.mode_s < 2:
                    print("Warning : Reset Vehicle State")
                    self.mode_g = 0
                    self.mode_l = 0
                    self.count = 0

                # Added Buzzer to notify user that Land command is accepted
                # self.buzzer.on()
                # sleep(1)
                # self.buzzer.off()
                # sleep(1)
                # self.buzzer.on()
                # sleep(1)
                # self.buzzer.off()
                # sleep(1)
                
        # Stop Movement
        if (kp == 'x') and self.vehicle.armed:
            print("Stop movement")
            print("Vehicle Mode : Freeze")
            self.x,self.y,self.z = 0,0,0

            # 3rd option
            self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)    
            self.engine.send_movement_command_YAW(0)
            
        # Yaw Left
        if (kp == 'q') and self.vehicle.armed:
            print("Yaw Left")
            self.yaw=-50
            #self.engine.executeChangesNow(0,0,0,self.takeoff_alt)
            #self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)
            self.engine.send_movement_command_YAW(self.yaw)

            #self.engine.rotate(-5)

        # Yaw Right
        if (kp == 'e') and self.vehicle.armed:
            print("Yaw RIGHT")
            self.yaw=50
            #self.engine.executeChangesNow(0,0,0,self.takeoff_alt)
            #self.engine.executeChangesNow(self.x,self.y,self.z,self.takeoff_alt)
            self.engine.send_movement_command_YAW(self.yaw)

            #self.engine.rotate(5)
            
        # Reset
        if (kp == 'r'):
            print("Reset")
            self.mode_s +=1
            if self.mode_s < 2:
                print("Warning : Reset Vehicle State")
                self.mode_g = 0
                self.mode_l = 0
                self.count  = 0


if __name__ == "__main__":
    init = readdatafromArdtoRpi()
    
    """use tx and rx port connect to Arduino"""
    #ser = init.initConnection("/dev/ttyAMA0", 9600)

    """use usb connection port connect to Arduino"""
    #ser = init.initConnection("/dev/ttyUSB0", 9600)
    #ser = init.initConnection("COM14", 115200)
    ser = init.initConnection("/dev/ttyACM0", 57600)

    while True:
        receivedata = init.getData(ser)
        
        if receivedata != None:
            print(receivedata)
            
            # if (receivedata == 'g'):
            #     guide = threading.Thread(target=guided_mode, daemon=True)
            #     guide.start()
            
            # elif (receivedata == 'u'):
            #     up = threading.Thread(target=up_mode, daemon=True)
            #     up.start()
            
            # elif (receivedata == 'r'):
            #     right = threading.Thread(target=right_mode, daemon=True)
            #     right.start()
            
            # elif (receivedata == 'l'):
            #     left = threading.Thread(target=left_mode, daemon=True)
            #     left.start()
            
            # elif (receivedata == 'w'):
            #     forward = threading.Thread(target=forward_mode, daemon=True)
            #     forward.start()
            
            # elif (receivedata == 's'):
            #     back = threading.Thread(target=back_mode, daemon=True)
            #     back.start()
                
            # elif (receivedata == 'l'):
            #     land = threading.Thread(target=land_mode, daemon=True)
            #     land.start()
            
            # elif (receivedata == 'x'):
            #     stop = threading.Thread(target=stop_mode, daemon=True)
            #     stop.start()
                    
            vals = init.getKeyboardInput(receivedata)
        

