# Guide on how install tflite-runtime in Raspberry Pi

Latest release of tflite-runtime especially for v2.11 will yield "segementation fault" when you run 
python code with Edge TPU enabled in Raspberry Pi (Bullseye)

See this issue reported in this link :
- > https://github.com/google-coral/edgetpu/issues/674

See the solution reported in this link:
- > https://github.com/tensorflow/tensorflow/blob/v2.5.0/tensorflow/lite/g3doc/guide/python.md#install-tensorflow-lite-for-python
- > *We will need to install tflite-runtime 2.5 version*

Solution
- > sudo pip uninstall tflite-runtime
- > echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
- > curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
- > sudo apt-get update
- > sudo apt-get install python3-tflite-runtime
- > pip list and ensure that tflite-runtime 2.5.0.post1






