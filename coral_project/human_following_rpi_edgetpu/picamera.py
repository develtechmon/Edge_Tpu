from picamera2 import Picamera2

class Picam:
    def __init__(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        self.picam2.start()
    
    def read(self):
        frame = self.picam2.capture_array()
        return frame