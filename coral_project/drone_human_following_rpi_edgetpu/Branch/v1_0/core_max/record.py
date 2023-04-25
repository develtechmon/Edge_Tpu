import cv2
import time

def record():
    path = "/home/jlukas/Desktop/My_Project/Edge_Tpu/coral_project/drone_human_following_rpi_edgetpu/Branch/v1_0/core_max/record/"
    writer= cv2.VideoWriter(path + "record_core" + f"{time.time()}" + '.mp4', cv2.VideoWriter_fourcc('m','p','4','v'), 10 ,(640,480))
    return writer
