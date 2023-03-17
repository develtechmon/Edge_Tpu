from flask import Flask, Response, render_template
from camera import *
#from picamera import *
from detect import *
from track import *
import state
import cv2
import os

import numpy as np
import sys
import threading
import time

imW, imH = 640,480

pError   = 0
pid      = [0.5,0.4]

# Frame sent to Flask object
global video_frame
video_frame = None

# Use locks for thread-safe viewing of frames in multiple browsers
global thread_lock
thread_lock = threading.Lock()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

def main():
    global video_frame, thread_lock

    # Webcam
    cam = VideoStream(resolution=(imW,imH),framerate=30).start()
    
    # PiCam
    #cam = Picam()

    det = Detect()
    track = Track()

    while True:
        # Webcam
        cap = cam.read()

        # PiCam
        # cap = cam.read()

        # Perform Inference
        img,info = det.inference(cap)

        # Perform Tracking
        track.trackobject(info,pid,pError)

        # Visualize
        track.visualise(img,info)

        with thread_lock:
            video_frame = img.copy()

def encode_cam():
    global thread_lock
    while True:
        with thread_lock:
            global video_frame
            if video_frame is None:
                continue
                    
            success, encoded_image = cv2.imencode('.jpg', video_frame)
            frame = encoded_image.tobytes()
            if not success:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
@app.route('/video_feed')
def video_feed():
    return Response(encode_cam(),mimetype = 'multipart/x-mixed-replace; boundary=frame')  

if __name__ == "__main__":
    init= threading.Thread(target=main)
    init.daemon = True
    init.start()
    app.run(host='0.0.0.0',port=80, threaded=True)