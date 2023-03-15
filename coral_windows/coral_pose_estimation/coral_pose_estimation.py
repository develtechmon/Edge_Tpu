import cv2
import numpy as np
import tflite_runtime.interpreter as tflite

# Load the EdgeTPU model
model_path = 'mediapipe_pose_edgetpu.tflite'
model_path = r'C:\Users\Lukas\Desktop\My_Projects\Edge_Tpu\coral_windows\coral_pose_estimation\project-posenet\models\mobilenet\posenet_mobilenet_v1_075_353_481_quant_decoder_edgetpu.tflite'
#model_path = r'C:\Users\jlukas\Downloads\posenet_mobilenet_v1_075_324_324_16_quant_decoder_edgetpu.tflite'

## For Linux    
#interpreter = tflite.Interpreter(model_path, experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])

## For Windows    
interpreter = tflite.Interpreter(model_path, experimental_delegates=[tflite.load_delegate('edgetpu.dll')])

# Get the input and output tensor details
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Open the Pi camera
cap = cv2.VideoCapture(0)

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    # Preprocess the frame for the model
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (input_details[0]['shape'][2], input_details[0]['shape'][1]))
    frame = np.expand_dims(frame, axis=0)

    # Run the model on the EdgeTPU accelerator
    interpreter.set_tensor(input_details[0]['index'], frame)
    interpreter.invoke()
    keypoints = interpreter.get_tensor(output_details[0]['index'])

    # Display the results
    for kp in keypoints[0]:
        x, y, c = kp
        if c > 0.2:
            cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
    cv2.imshow('Pose Estimation', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
