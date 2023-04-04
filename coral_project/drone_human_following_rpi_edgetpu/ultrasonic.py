import threading
import gpiozero
import state
import time

class ultrasonic (threading.Thread):
    def __init__(self,D,Alt):
        threading.Thread.__init__(self)
        self.daemon   = True
        self.engine   = D.engines
        self.altitude = Alt
        self.distance = 0

        self.TRIG = 23
        self.ECHO = 24

        self.trigger = gpiozero.OutputDevice(self.TRIG)
        self.echo = gpiozero.DigitalInputDevice(self.ECHO)

    def get_distance(self):
        self.trigger.on()
        time.sleep(0.00001)
        self.trigger.off()

        while self.echo.is_active == False:
            self.pulse_start = time.time()

        while self.echo.is_active == True:
            self.pulse_end = time.time()

        self.pulse_duration = self.pulse_end - self.pulse_start
        self.distance = 34300 * (self.pulse_duration/2)
        self.round_distance = round(self.distance,1)

        return(self.round_distance)
    
    def run(self):
        while True:
            dist = self.get_distance()
            print(dist)

            if (dist <= 15) and (state.get_airborne() == "on"):
                self.engine.executeChangesNow(-0.2,0,self.altitude)

