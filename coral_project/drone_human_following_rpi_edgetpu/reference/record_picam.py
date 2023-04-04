import cv2
import time
from picamera2 import Picamera2

width = 640
height = 480

# Grab images as numpy arrays and leave everything else to OpenCV.
#face_detector = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")
#cv2.startWindowThread()

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
#picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# Create video writer object
filename = f"recording_{time.time()}.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

#out = cv2.VideoWriter('output.avi',cv2.cv.CV_FOURCC('M','J','P','G'), 20.0, (640,480))
out = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))

while True:
    im = picam2.capture_array()
    
    #frame = im.copy()
    #grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    #faces = face_detector.detectMultiScale(grey, 1.1, 5)

    #for (x, y, w, h) in faces:
    #    cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0))

    out.write(im)
    cv2.imshow("Camera", im)
    if cv2.waitKey(1) == ord('q'):
        break
    
out.release()
cv2.destroyAllWindows()