import os
import numpy as np
import cv2
import state
from track import *

class Detect():
    def __init__(self,cam,D):
        self.track = Track(D)
        
        '''
        Working in RPI. Enable this if below doesn't work
        self.path = os.getcwd() 
        self.default_model_dir = self.path + '/model/'
        self.model = 'object-detector-quantized_edgetpu.tflite'
        
        self.default_label = self.default_model_dir +  'object_detection_labelmap.txt'
        print("----> " + self.path)
        '''
       	#self.path = "/home/jlukas/Desktop/My_Project/Edge_Tpu/coral_project/drone_human_following_rpi_edgetpu/model/""
        self.absolute_path = os.path.dirname(__file__)
        self.default_model_dir = self.absolute_path + '/model/'
        self.model = 'object-detector-quantized_edgetpu.tflite'
        self.default_label = self.default_model_dir + 'object_detection_labelmap.txt'
        
        from tflite_runtime.interpreter import Interpreter
        from tflite_runtime.interpreter import load_delegate

        with open(self.default_label, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Linux - libedgetpu.so.1.0
        self.interpreter = Interpreter(model_path=self.default_model_dir + self.model, experimental_delegates=[load_delegate('libedgetpu.so.1.0')]) 

        # Windows -edgetpu.dll
        #self.interpreter = Interpreter(model_path=self.default_model_dir + self.model, experimental_delegates=[load_delegate('edgetpu.dll')]) 
        
        self.interpreter.allocate_tensors()

        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.5
        self.input_std = 127.5
        self.min_conf_threshold = float(0.5)
        self.imW = 640
        self.imH = 480

    def inference(self,img):
        self.frame = img.copy()
        self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.frame_resized = cv2.resize(self.frame_rgb, (self.width, self.height))
        self.input_data = np.expand_dims(self.frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if self.floating_model:
             self.input_data = (np.float32( self.input_data) - self.input_mean) / self.input_std

        # Perform the actual detection by running the model with the image as input
        self.interpreter.set_tensor(self.input_details[0]['index'], self.input_data)
        self.interpreter.invoke()

        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0] # Class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
        
        # List
        #myobjectlistC = []
        #myobjectlistArea = []
        
        # Numpy
        myobjectlistC = np.array([])
        myobjectlistArea = np.array([])
        
        for i in range(len(scores)):
            if ((scores[i] > self.min_conf_threshold) and (scores[i] <= 1.0)):

                self.object_name = self.labels[int(classes[i])] # Look up object name from "labels" array using class index
                self.label = '%s: %d%%' % ( self.object_name, int(scores[i]*100)) # Example: 'person: 72%'

                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * self.imH)))
                xmin = int(max(1,(boxes[i][1] * self.imW)))
                ymax = int(min(self.imH,(boxes[i][2] * self.imH)))
                xmax = int(min(self.imW,(boxes[i][3] * self.imW)))
                
                xdif = xmax - xmin
                ydif = ymax - ymin
                cx = xmin + (xdif/2)
                cy = ymin + (ydif/2)
                area = round(xdif * ydif)
                
                # Using Numpy
                myobjectlistArea = np.append(myobjectlistArea,area)
                myobjectlistC = np.append(myobjectlistC,[cx,cy])

                # Using List
                #myobjectlistArea.append(area)
                #myobjectlistC.append([cx,cy])
                
                #print("Area >> ", myobjectlistArea)
                #print("Cx,Cy >> ", myobjectlistC)
                
                #if len(myobjectlistArea) !=0 and myobjectlistC != None:
                if len(myobjectlistArea) !=0:
                    if self.object_name == 'person':
                        
                        state.set_visualise_state("draw")
                        cv2.rectangle(self.frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                        # Draw label   
                        labelSize, baseLine = cv2.getTextSize(self.label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                        label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                        cv2.rectangle(self.frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                        cv2.putText(self.frame, "Lukas", (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                        
                        info = ([myobjectlistC, myobjectlistArea])
                        print("\ninfo >> ", info)
                        print("First index >> ", info[0])
                        print("Cx >> ", info[0][0])
                        print("Cy >> ", info[0][1])
                        print("Area >> ", info[1])

                        # Numpy
                        i = np.argmax(myobjectlistArea)                        
                        return (self.frame,self.object_name,[[myobjectlistC[i], myobjectlistC[i+1]], myobjectlistArea[i]])

                        # Using List
                        #i = myobjectlistArea.index(max(myobjectlistArea))
                        #return self.frame,self.object_name,[myobjectlistC[i],myobjectlistArea[i]]
                
                else:
                    #state.set_visualise_state("nodraw")
                    return self.frame,self.object_name,[[0,0],0]
                    

