import logging, time, threading
import cv2
import numpy as np
import state

#class Track(threading.Thread):
class Track:
    def __init__(self,D):
        # threading.Thread.__init__(self)
        self.daemon = True
        self.w      = 640
        self.h      = 480
        self.engine = D.engines

    def trackobject(self,info,pid,pError,altitude):
        self.info   = info
        self.pid    = pid
        self.pError = pError
        
        if ((self.info[1]) !=0):
            error = self.w//2 - self.info[0][0]
            self.posXC  = (self.pid[0]*error + self.pid[1]*(error-self.pError))
            self.posX   = (np.interp(self.posXC, [-self.w//4, self.w//4], [-10,10]))

            #self.posX   = (np.clip(self.posXC, -10,10))
	    
            self.pError = error
            
            #print(str(self.posX) + " " + str(info[1]))
            
            self.engine.executeChangesNow(0.2,0,altitude)
            self.engine.send_movement_command_YAW(self.posX)
                    
        else:
            self.engine.executeChangesNow(0,0,altitude)
            self.engine.send_movement_command_YAW(0)
        
    def visualise(self,img,info):
        if len(info) != 0:
            # Top
            cv2.rectangle(img, (0,0), (self.w,24), (0,0,0), -1)

            # Bottom
            cv2.rectangle(img, (0, self.h-24), (self.w,self.h), (0,0,0), -1)
        
            # Width and Height
            text_dur = 'Width : {} Height: {}'.format(self.w, self.h)
            cv2.putText(img, text_dur, (10,16), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150,150,255), 2)
        
            #if (state.get_visualise_state() == "draw"):
                # Draw Center Middle Line
                #cv2.line(img,(self.w//2,0),(self.w//2,self.h-24), (255,0,255),3)
        
                # Draw Center Image
                #cv2.circle(img, (self.w // 2, self.h // 2), 10, (0, 0, 255), cv2.FILLED)
        
                # Draw Center Circle
                #cv2.circle(img, (int(info[0][0]), int(info[0][1])), 10, (0, 0, 255), thickness=-1, lineType=8, shift=0)

                # Draw Arrowed Line
                #cv2.line(img, (int(self.w // 2), int(self.h // 2)), (int(info[0][0]), int(info[0][1])), (255, 0, 0), 5, 10)
