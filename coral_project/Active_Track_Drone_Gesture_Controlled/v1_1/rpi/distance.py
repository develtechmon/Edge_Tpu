import time
import board
import busio
import adafruit_vl53l0x
import state
import threading

class Distance(threading.Thread):
    def __init__(self,D,Alt):
        threading.Thread.__init__(self)
        self.daemon   = True
        self.drone    = D
        self.engine   = D.engines
        self.altitude = Alt
        self.distance = 0
        
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.vl53 = adafruit_vl53l0x.VL53L0X(self.i2c)
        self.vl53.measurement_timing_budget = 200000

    def run(self):
        with self.vl53.continuous_mode():
            while True:
                #time.sleep(0.1)
                curTime = time.time()
                if (self.vl53.range * 0.1 < 800) and (state.get_airborne() == "on"):
                    self.drone.control_tab.back()
                    
                    #self.engine.executeChangesNow(-0.4,0,self.altitude)
                    #self.engine.send_movement_command_YAW(0)

                #print("Range: {0}mm ({1:.2f}ms)".format(self.vl53.range * 0.1, time.time() - curTime))
        
