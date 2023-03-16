
from camera import *
from picamera import *
from detect import *
import cv2
import os

imW, imH = 640,480

if __name__ == "__main__":
    # Webcam
    #cam = VideoStream(resolution=(imW,imH),framerate=30).start()
    
    # PiCam
    cam = Picam()
    
    det = Detect()

    while True:       
        # Webcam
        #cap = cam.read()
        
        # PiCam
        cap = cam.read()
        img = det.inference(cap)
        
        cv2.imshow("Capture",img)

        if cv2.waitKey(1) & 0XFF == ord('q'):
            break

    cv2.destroyAllWindows()
    #cam.stop()


