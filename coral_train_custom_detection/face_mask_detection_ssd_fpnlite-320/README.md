# How to run trained `ssd_fpnlite-320` Face Detection model

```
cd /home/jlukas/Desktop/My_Project/Edge_Tpu/coral_train_custom_detection/face_mask_detection_ssd_fpnlite-320/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/

python3 TFLite_detection_rpi.py --modeldir ../../face_mask_detection_ssd_fpnlite-320/Model --edgetpu (To run with TPU support)

python3 TFLite_detection_webcam.py --modeldir ../../face_mask_detection_ssd_fpnlite-320/Model/ (To run without TPU support)

```