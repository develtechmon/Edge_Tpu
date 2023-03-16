# 
# Webcam object detection supporting toggling between CPU and TPU acceleration
#
# Author:   Jerry Kurata
# Date:     Oct 1, 2020
# Description:
#  NOTE: THIS CODE HAS ONLY BEEN TESTED ON RASPBERRY PI 4.  HAVING A USB 3 PORT IS KEY TO PERFORMANCE.
#
# This is a modifier version of the Evan Juras's Object detection classifier. https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi
# This version lets the user toggle between using the Google Coral TPU accelerator or CPU for object detection.
# The use of the TPU can increase performance 5 to 10 times, depending up the TPU type.
# USB 3 connect TPUs such as the Coral USB Accelerator will see up to a 5 times increase in the 
# number of frames for which objects are detected.  Typically this means going from 3-4 fps with CPU to 
# 20-24 fps with the Accelerator.  For other devices higher performance connections like the Coral Dev 
# Board the difference can be 10 times faster.
#
# To toggle back and forth between using or not using the acclerator, the user presses the 't' key. 
#

######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 10/27/19
# Description: 
# This program uses a TensorFlow Lite model to perform object detection on a live webcam
# feed. It draws boxes and scores around the objects of interest in each frame from the
# webcam. To improve FPS, the webcam object runs in a separate thread from the main program.
# This script will work with either a Picamera or regular USB webcam.
#
# This code is based off the TensorFlow Lite image classification example at:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
#
# I added my own method of drawing boxes and labels using OpenCV.

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
from picamera2 import Picamera2

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

# Define and parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                    required=True)
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=0.5)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                    default='1280x720')
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                    action='store_true')

args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
# use_TPU = args.edgetpu
use_TPU = True
using_TPU = False    # are we currenty using TPU.  Toggle by pressing 't' key

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')

if pkg:
    print('tflite_runtime found')
    from tflite_runtime.interpreter import Interpreter
    from tflite_runtime.interpreter import load_delegate
else:
    print('tflite_runtime NOT found')
    from tensorflow.lite.python.interpreter import Interpreter
    from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME_TPU = 'edgetpu.tflite'
        GRAPH_NAME_CPU = 'detect.tflite' #'edgetpu2.tflite'       

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT_TPU = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME_TPU)
PATH_TO_CKPT_CPU = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME_CPU)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

# Create 2 interpreter objects.  One using TPU version and on using CPU version of model
print("TPU model:", PATH_TO_CKPT_TPU)
print("CPU model:", PATH_TO_CKPT_CPU)

# Linux
interpreter_tpu = Interpreter(model_path=PATH_TO_CKPT_TPU, experimental_delegates=[load_delegate('libedgetpu.so.1.0')])

# WIndow
#interpreter_tpu = Interpreter(model_path=PATH_TO_CKPT_TPU , experimental_delegates=[load_delegate('edgetpu.dll')])

interpreter_cpu = Interpreter(model_path=PATH_TO_CKPT_CPU)

# Allocate tensor for both interpreters
interpreter_tpu.allocate_tensors()
interpreter_cpu.allocate_tensors()

print('Initializing to use CPU.')
print('Press "t" to toggle between CPU and TPU, and "q" to terminate.')

# Start running on CPU
interpreter = interpreter_cpu
accelerator_used = 'CPU'
using_TPU = False

# Initial settings for model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()

# Initialize video stream
#videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

#time.sleep(1)

#for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
while True:

    # Start timer (for calculating frame rate)
    t1 = cv2.getTickCount()

    # Grab frame from video stream
    frame1 = picam2.capture_array()

    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    # Draw accelerator used and framerate in corner of frame
    cv2.putText(frame,'{0} FPS: {1:.2f}'.format(accelerator_used, frame_rate_calc),(30,50), \
        cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,0),2,cv2.LINE_AA)

    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1

    # capture keypress
    keypressed = cv2.waitKey(1)
    if keypressed == ord('q'):       # q = quit
        break
    else:
        if keypressed == ord('t'):   # t = toggle between CPU and TPU
            if using_TPU:
                interpreter = interpreter_cpu
                using_TPU = False
                accelerator_used = 'CPU'
            else:
                interpreter = interpreter_tpu
                using_TPU = True
                accelerator_used = 'TPU'     
            
            # Since interpreter is changed we need to reload details based on interpreter
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            height = input_details[0]['shape'][1]
            width = input_details[0]['shape'][2]

            floating_model = (input_details[0]['dtype'] == np.float32)
    
    
# Clean up
cv2.destroyAllWindows()
videostream.stop()
