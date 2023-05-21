from dronekit import *

'''
    ## This is how to port forward data from Mavproxy (Ground Stations) to Copter (IP address)
    10.60 address is from ifconfig of the connected wifi, to enable this run:
    
    USING USB  : mavproxy.py --master=/dev/ttyACM0 --out=udp:10.60.216.198
    USING JETSON NANO UART : mavproxy.py --master=/dev/ttyTHS1,921600 --out=udp:10.60.216.198:14550
    USING RPI UART : mavproxy.py --master=/dev/ttyAMA0,921600
    
    /dev/ttyTHS1 port from Pixhawk is not authorized for read and write access. May encounter, permission denied.
    To enable this simply run chmod 666 /dev/ttyTHS1
'''
#connection_string = '10.60.216.198:14550'

'''Using SiTL Connection'''
#connection_string = '127.0.0.1:14550'

'''Using SiTL Connection from  different computer - This IP address below to receiver device for example RPI
   This IP address is based on given ZeroTier IP address'''
#connection_string = '192.168.195.204:14551'
#connection_string = '192.168.195.204:14553'
connection_string = '192.168.8.146:14553'

'''Using Uart Serial Rx->Tx and Tx-Rx connection'''
# For Jetson Nano
#connection_string = '/dev/ttyTHS1,921600'

'''
For RPI
Use below setting in Mission Planner
Write and reboot the pixhawk

Telemetry 2 (Serial 2)
SERIAL2_BAUD = 921600
SERIAL2_PROTOCOL = 1 (Mavlink)

Alternatively, you can run below command to test 
mavproxy.py --master=/dev/ttyAMA0,921600

'''
#connection_string = '/dev/ttyAMA0,921600'

''' Using USB Connection '''
#connection_string = '/dev/ttyACM0'

vehicle = connect(connection_string, wait_ready = True)
print("Virtual Copter is Ready")


