# Installation Guide To Install Edge TPU in RPI

## See this link
- > https://coral.ai/docs/accelerator/get-started/#runtime-on-linux

## Add Debian package repository to system
- > echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
- > curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
- > sudo apt-get update

## Install Edge TPU runtime
- > sudo apt-get install libedgetpu1-std
- > now connec the USB accelerator to computer using the provided USB3.0 cable.

## Install with maximum operating frequency (optional)
- > sudo apt-get install libedgetpu1-max

## Install PyCoral Library
- > sudo apt-get install python3-pycoral

## Run model on Edge TPU
*Download the example from Github. Suggested install using Windows Subsystem for Linux and Git for Windows*
- > mkdir coral && cd coral
- > git clone https://github.com/google-coral/pycoral.git
- > cd pycoral

*Download the models, labels and bird photo*
- > bash examples/install_requirements.sh classify_image.py

*Run the image classifier with the bird photo*
- > python3 examples/classify_image.py \
--model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--labels test_data/inat_bird_labels.txt \
--input test_data/parrot.jpg

- > py -3.8 examples/classify_image.py \
--model test_data/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite \
--labels test_data/inat_bird_labels.txt \
--input test_data/parrot.jpg

## Alternatively you can also use tflite_runtime instead of coral. To install tflite
- > sudo pip install tflite-support
- > sudo pip install protobuf
- > sudo pip install numpy




