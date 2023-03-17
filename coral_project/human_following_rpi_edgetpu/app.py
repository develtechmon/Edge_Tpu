
from camera import *
#from picamera import *
from detect import *
from track import *
import state
import cv2
import os

imW, imH = 640,480

pError   = 0
pid      = [0.5,0.4]

if __name__ == "__main__":
    
    # Webcam
    cam = VideoStream(resolution=(imW,imH),framerate=30).start()
    
    # PiCam
    #cam = Picam()
    
    det = Detect()
    track = Track()

    while True:       
        #Webcam
        cap = cam.read()
        
        #PiCam
        #cap = cam.read()
        
        # Perform Inference
        img,info = det.inference(cap)
        
        # Perform Tracking
        track.trackobject(info,pid,pError)
        
        # Visualize
        track.visualise(img,info)
        
        cv2.imshow("Capture",img)

        if cv2.waitKey(1) & 0XFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cam.stop()


