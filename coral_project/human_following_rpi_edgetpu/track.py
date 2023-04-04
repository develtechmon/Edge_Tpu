import logging, time, threading
import cv2
import numpy as np
import state

#class Track(threading.Thread):
class Track:
    def __init__(self):
        # threading.Thread.__init__(self)
        self.daemon = True
        self.w      = 640
        self.h      = 480
        #self.ser    = sm.initConnection('/dev/ttyACM0',9600)

    def trackobject(self,info,pid,pError):
        self.info   = info
        self.pid    = pid
        self.pError = pError
        
        if ((self.info[1]) !=0) and ((self.info[1]) < 500000):
            error = self.w//2 - self.info[0][0]
            self.posX   = int(self.pid[0]*error + self.pid[1]*(error-self.pError))
            self.posX   = int(np.interp(self.posX, [-self.w//4, self.w//4], [-35,35]))
            self.pError = error
            
            print(str(self.posX) + " " + str(info[1]))
            #sm.sendData(self.ser, [50,self.posX],4)
            
        # elif ((info[1]) !=0) and ((info[1]) > 5760000):
        #     sm.sendData(self.ser,[0,0],4)
        
        else:
            pass
            #sm.sendData(self.ser,[0,0],4)
        
    def visualise(self,img,info):
         # Top
        cv2.rectangle(img, (0,0), (self.w,24), (0,0,0), -1)

        # Bottom
        cv2.rectangle(img, (0, self.h-24), (self.w,self.h), (0,0,0), -1)
        
        # Width and Height
        text_dur = 'Width : {} Height: {}'.format(self.w, self.h)
        cv2.putText(img, text_dur, (10,16), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150,150,255), 2)
        
        #if (state.get_system_state() == "draw"):
            # Draw Center Middle Line
            #cv2.line(img,(self.w//2,0),(self.w//2,self.h-24), (255,0,255),3)
        
            # Draw Center Image
            #cv2.circle(img, (self.w // 2, self.h // 2), 10, (0, 0, 255), cv2.FILLED)
        
            # Draw Center Circle
            #cv2.circle(img, (int(info[0][0]), int(info[0][1])), 10, (0, 0, 255), thickness=-1, lineType=8, shift=0)

            # Draw Arrowed Line
            #cv2.line(img, (int(self.w // 2), int(self.h // 2)), (int(info[0][0]), int(info[0][1])), (255, 0, 0), 5, 10)
