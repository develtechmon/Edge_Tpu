import cv2
import time
from time import sleep
from datetime import datetime

def write_video(frame_queue):
    path = "/home/jlukas/Desktop/My_Project/Edge_Tpu/coral_project/drone_human_following_rpi_edgetpu/Branch/v1_0/max/queue/record/"
    out= cv2.VideoWriter(path + "record_queue" + f"{time.time()}" + '.mp4', cv2.VideoWriter_fourcc('m','p','4','v'), 10 ,(640,480))
    
    while True:
        #Get the next frame frome the queue
        frame = frame_queue.get()

        #If we receive none, we're done
        if frame is None:
            break
        
        # Write the frame to the output video
        out.write(frame)

    # Release the videowriter
    out.release()
