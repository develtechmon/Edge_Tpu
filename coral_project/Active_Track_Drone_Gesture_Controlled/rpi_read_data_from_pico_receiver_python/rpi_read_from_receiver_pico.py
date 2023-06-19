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

class readdatafromArdtoRpi:

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

if __name__ == "__main__":
    init = readdatafromArdtoRpi()
    
    """use tx and rx port connect to Arduino"""
    #ser = init.initConnection("/dev/ttyAMA0", 9600)

    """use usb connection port connect to Arduino"""
    #ser = init.initConnection("/dev/ttyUSB0", 9600)
    #ser = init.initConnection("COM14", 115200)
    ser = init.initConnection("/dev/ttyACM0", 115200)

    while True:
        receivedata = init.getData(ser)
        
        if receivedata != None:
            print(receivedata)
            #vals = init.getKeyboardInput(receivedata)

