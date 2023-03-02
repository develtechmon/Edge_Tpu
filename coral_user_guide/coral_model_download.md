# User Guide To Download Edge TPU model

## Quantized Model for Edge TPU
Create all_models directory
- *mkdir -p all_models*

Download model using wget
- *wget https://dl.google.com/coral/canned_models/all_models.tar.gz*

Unzip or Untar model files
- *tar -C all_models -xvzf all_models.tar.gz*

Remove the tar model files
- *rm -f all_models.tar.gz*

## Efficientdet_lite0_edgeTPU model
- [Efficientdet_lite0_edgetpu*_metadata](https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/object_detection/rpi/efficientdet_lite0_edgetpu_metadata.tflite)