# Installation Guide To Install Edge TPU in Windows

## See this link
- > https://coral.ai/docs/accelerator/get-started/#runtime-on-windows

## First make sure to have latest version of
- > Microsoft Visual C++ 2019 redistributable. DOwnload 64 bit version
- > https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads 

## Then download
- > download edgetpu_runtime_20221024.zip
- > https://github.com/google-coral/libedgetpu/releases/download/release-grouper/edgetpu_runtime_20221024.zip

## Extract the Zip and double click the 
- > install.bat file
- > type 'N' to use the reduce operating frequency to avoid the USB accelerator from hot. Can run this file again later to change the setting.

## Now connect the USB accelerator
- > Provided using USB 3.0 cable is the best

## Python version requirement
- > use python3.6 to 3.9

## Install PyCoral
- > python3 -m pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0
- > py -3.8 -m pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0

## Run a model on Edge TPU

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


