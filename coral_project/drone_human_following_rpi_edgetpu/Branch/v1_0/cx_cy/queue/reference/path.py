import os

# path = os.path.abspath("/model/")

absolute_path = os.path.dirname(__file__)
model_dir = absolute_path+ '/model/'

model = 'object-detector-quantized_edgetpu.tflite'
label = model_dir + 'object_detection_labelmap.txt'

model_file = model_dir + model
print(model_file)
print(label)


