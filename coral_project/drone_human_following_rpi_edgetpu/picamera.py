from picamera2 import Picamera2
from libcamera import Transform

class Picam:
    def __init__(self):
        self.picam2 = Picamera2()
        self.DISPLAY_WIDTH = 640
        self.DISPLAY_HEIGHT = 480
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)},transform=Transform(hflip=True)))
        #self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888'}))

        self.picam2.start()
    
    def read(self):
        frame = self.picam2.capture_array()
        return frame
