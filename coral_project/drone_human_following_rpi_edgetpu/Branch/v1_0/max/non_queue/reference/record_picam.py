import cv2
import time
from picamera2 import Picamera2

picam2 = Picamera2()

# Enable this if you want to have RGB image. However, this format wont work if you're using videowriter
#picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
#picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))

# Enable this if you want to img format as HSV. Here i convert HSV to RGB image using BGR2RGB 
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# Enable this if you want to write with MJPG codec. Outputfile should avi as follow
#out = cv2.VideoWriter('output.avi',cv2.cv.CV_FOURCC('M','J','P','G'), 20.0, (640,480))

# Create video writer object
#filename = f"recording_{time.time()}.avi"
#fourcc = cv2.VideoWriter_fourcc(*"XVID")

# Create video writer object
filename = f"recording_{time.time()}.mp4"
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')

out = cv2.VideoWriter(filename, fourcc, 15, (640, 480))

while True:
    im = picam2.capture_array()
    frame  = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    
    cv2.imshow("Camera", frame)
    out.write(frame)
    if cv2.waitKey(1) == ord('q'):
        break
    
out.release()
cv2.destroyAllWindows()
