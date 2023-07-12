import serial
import threading
from drone import *
from time import sleep
from distance import *

altitude = 1.3

def guided_mode():
    drone.control_tab.guided()
    up_mode()
    
def up_mode():
    drone.control_tab.armAndTakeoff(altitude)
    #drone.control_tab.armAndTakeoff_nogps(altitude)
    
def yawleft_mode():
    drone.control_tab.yaw_left()

def yawright_mode():
    drone.control_tab.yaw_right()

def left_mode():
    drone.control_tab.left()

def right_mode():
    drone.control_tab.right()

def forward_mode():
    drone.control_tab.forward()
    #drone.control_tab.forward_no_gps()

def back_mode():
    drone.control_tab.back()
    #drone.control_tab.backward_no_gps()

def stop_mode():
    drone.control_tab.stop_drone()

def land_mode():
    drone.control_tab.land()
    
# Connect to Pico
def initConnection(portNo, baudRate):
    try:
        ser = serial.Serial(portNo, baudRate)
        print("Device Connected")
        return ser
    except:
        print("Not connected")

# Extract data from Pico NRF - Receiver
def getData(ser):
    try:
        data = ser.readline()
        data = data.decode("utf-8")
        data = data.split()
        data = data[0]
        return data
                
    except:
        pass

sleep(0.25)
    
if __name__ == "__main__":
     
    mode_g = 0
    mode_u = 0
    mode_d = 0
    mode_a = 0
    mode_w = 0
    mode_s = 0
    mode_q = 0
    mode_e = 0
    mode_l = 0
    mode_x = 0
    
    ser = initConnection("/dev/ttyACM0", 57600)
    
    while True:
        try:
            drone = Drone()
            break

        except Exception as e:
            sleep(2)
    
    # Init Distance - Obstacle
    dis = Distance(drone, altitude)
    dis.start()
            
    while drone.is_active:
        try:
            receivedata = getData(ser)
            
            if receivedata != None:
                #print(receivedata)
                # print(chr(receivedata))  
                            
                if (receivedata == 'g'):
                    mode_g += 1
                    if mode_g < 2:
                        guide = threading.Thread(target=guided_mode, daemon=True)
                        guide.start()
            
                #elif (receivedata == 'u'):
                #    mode_u += 1
                #    if mode_u < 2:
                #        up = threading.Thread(target=up_mode, daemon=True)
                #        up.start()
            
                elif (receivedata == '100'): #d
                    mode_d += 1
                    if mode_d < 2:
                        #print("Move Right")
                        right = threading.Thread(target=right_mode, daemon=True)
                        right.start()
                        mode_g = 0
                        mode_u = 0
                        mode_a = 0
                        mode_w = 0
                        mode_s = 0
                        mode_q = 0
                        mode_e = 0
                        mode_l = 0
                        mode_x = 0
            
                elif (receivedata == '97'): #a
                    mode_a += 1
                    if mode_a < 2:   
                        #print("Move Left")
                        left = threading.Thread(target=left_mode, daemon=True)
                        left.start()
                        mode_d = 0
                        mode_g = 0
                        mode_u = 0
                        mode_w = 0
                        mode_s = 0
                        mode_q = 0
                        mode_e = 0
                        mode_l = 0
                        mode_x = 0
            
                elif (receivedata == '119'): # w
                    mode_w += 1
                    if mode_w < 2:
                        #print("Move Forward")
                        forward = threading.Thread(target=forward_mode, daemon=True)
                        forward.start()
                        mode_s = 0
                        mode_g = 0
                        mode_u = 0
                        mode_d = 0
                        mode_a = 0
                        mode_q = 0
                        mode_e = 0
                        mode_l = 0
                        mode_x = 0
            
                elif (receivedata == '115'): #s
                    mode_s += 1
                    if mode_s < 2:
                        #print("Move Backward")
                        back = threading.Thread(target=back_mode, daemon=True)
                        back.start()
                        mode_g = 0
                        mode_u = 0
                        mode_d = 0
                        mode_a = 0
                        mode_w = 0
                        mode_q = 0
                        mode_e = 0
                        mode_l = 0
                        mode_x = 0
                        
                elif (receivedata == '108'): #q
                    mode_q += 1
                    if mode_q < 2:
                        #print("Yaw Left")
                        yawleft = threading.Thread(target=yawleft_mode, daemon=True)
                        yawleft.start()
                        mode_g = 0
                        mode_u = 0
                        mode_d = 0
                        mode_a = 0
                        mode_w = 0
                        mode_s = 0
                        mode_e = 0
                        mode_l = 0
                        mode_x = 0
                        
                elif (receivedata == '114'): #e
                    mode_e += 1
                    if mode_e < 2:
                        #print("Yaw Right")
                        yawright = threading.Thread(target=yawright_mode, daemon=True)
                        yawright.start()
                        mode_g = 0
                        mode_u = 0
                        mode_d = 0
                        mode_a = 0
                        mode_w = 0
                        mode_s = 0
                        mode_q = 0
                        mode_l = 0
                        mode_x = 0
                                    
                elif (receivedata == 'l'):
                    mode_l += 1
                    if mode_l < 2:
                        #print("Land")
                        land = threading.Thread(target=land_mode, daemon=True)
                        land.start()
                        mode_g = 0
                        mode_u = 0
                        mode_d = 0
                        mode_a = 0
                        mode_w = 0
                        mode_s = 0
                        mode_q = 0
                        mode_e = 0
                        mode_x = 0
            
                elif (receivedata == '120'): # x
                    mode_x += 1
                    if mode_x < 2:
                        #print("Freeze and Hover")
                        stop = threading.Thread(target=stop_mode, daemon=True)
                        stop.start()
                        mode_g = 0
                        mode_u = 0
                        mode_d = 0
                        mode_a = 0
                        mode_w = 0
                        mode_s = 0
                        mode_q = 0
                        mode_e = 0
                        mode_l = 0
                
        except:
            pass
        
    guide.join()
    right.join()
    left.join()
    forward.join()
    back.join()
    yawleft.join()
    yawright.join()
    land.join()
    stop.join()
    
    
    
    
    
