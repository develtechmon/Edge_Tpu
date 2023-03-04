# Train custom object detection model using your data with Raspberry Pi

In this userguide, we're going to train the model using model maker provided by tensor flow.
Here we are going to create develop face mask detection model for

* `tflite model`
* `tlite_edgeTPU model` for USB Coral Accelerator

To start, visit this google colab
[model maker object](https://colab.research.google.com/github/khanhlvg/tflite_raspberry_pi/blob/main/object_detection/Train_custom_model_tutorial.ipynb#scrollTo=VdRihInCJ3ie) Then upload this [Face Model into google drive](https://drive.google.com/drive/u/0/folders/1x4t0iuSMLN3NH8P0OaAVeX4xaTYEmxQn). Open google colab and Mount the drive. Please ensure `Face Mode` detections directory consist of `validate` and `train` directory. From google colab, run cell accordingly.

## Note 
In this project. I'm using Pascal VOC format to annotate the dataset `mask` and `no-mask` class using `labelimg` software.
See `coral_user_guide\coral_labelimg_download.md` to install this tool.

* Below is dataset data for each directory

```
train : 60 images
validate : 29 images (randomly copy from train)
```
## Install the required package

```
!pip install -q tflite-model-maker
!pip install -q tflite-support

```

```
import numpy as np
import os

from tflite_model_maker.config import ExportFormat, QuantizationConfig
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

from tflite_support import metadata

import tensorflow as tf
assert tf.__version__.startswith('2')

tf.get_logger().setLevel('ERROR')
from absl import logging
logging.set_verbosity(logging.ERROR)

```

## Prepare the dataset
```
from google.colab import drive
drive.mount('/content/drive')

#!unzip -q android_figurine.zip

!print(/content/drive/MyDrive/Face_Mask_EdgeTPU/)
```

## Train the object detection model

### Step 1: Load the dataset

* Images in `train_data` is used to train the custom object detection model.
* Images in `val_data` is used to check if the model can generalize well to new images that it hasn't seen before.

```
train_data = object_detector.DataLoader.from_pascal_voc(
    '/content/drive/MyDrive/Face_Mask_EdgeTPU/train',
    '/content/drive/MyDrive/Face_Mask_EdgeTPU/train',
    ['mask', 'no-mask']
)

val_data = object_detector.DataLoader.from_pascal_voc(
    '/content/drive/MyDrive/Face_Mask_EdgeTPU/validate',
    '/content/drive/MyDrive/Face_Mask_EdgeTPU/validate',
    ['mask', 'no-mask']
)
```
### Step 2: Select a model architecture

EfficientDet-Lite[0-4] are a family of mobile/IoT-friendly object detection models derived from the [EfficientDet](https://arxiv.org/abs/1911.09070) architecture.

Here is the performance of each EfficientDet-Lite models compared to each others.

| Model architecture | Size(MB)* | Latency(ms)** | Average Precision*** |
|--------------------|-----------|---------------|----------------------|
| EfficientDet-Lite0 | 4.4       | 146           | 25.69%               |
| EfficientDet-Lite1 | 5.8       | 259           | 30.55%               |
| EfficientDet-Lite2 | 7.2       | 396           | 33.97%               |
| EfficientDet-Lite3 | 11.4      | 716           | 37.70%               |
| EfficientDet-Lite4 | 19.9      | 1886          | 41.96%               |

<i> * Size of the integer quantized models. <br/>
** Latency measured on Raspberry Pi 4 using 4 threads on CPU. <br/>
*** Average Precision is the mAP (mean Average Precision) on the COCO 2017 validation dataset.
</i>

In this notebook, we use EfficientDet-Lite0 to train our model. You can choose other model architectures depending on whether speed or accuracy is more important to you.

```
spec = model_spec.get('efficientdet_lite0')
```

### Step 3: Train the TensorFlow model with the training data.

* Set `epochs = 20`, which means it will go through the training dataset 20 times. You can look at the validation accuracy during training and stop when you see validation loss (`val_loss`) stop decreasing to avoid overfitting.
* Set `batch_size = 4` here so you will see that it takes 15 steps to go through the 62 images in the training dataset.
* Set `train_whole_model=True` to fine-tune the whole model instead of just training the head layer to improve accuracy. The trade-off is that it may take longer to train the model.

```
model = object_detector.create(train_data, model_spec=spec, batch_size=4, train_whole_model=True, epochs=20, validation_data=val_data)
```

### Step 4. Evaluate the model with the validation data.

After training the object detection model using the images in the training dataset, use the 10 images in the validation dataset to evaluate how the model performs against new data it has never seen before.

As the default batch size is 64, it will take 1 step to go through the 10 images in the validation dataset.

The evaluation metrics are same as [COCO](https://cocodataset.org/#detection-eval).

```
model.evaluate(val_data)
```

### Step 5: Export as a TensorFlow Lite model.

Export the trained object detection model to the TensorFlow Lite format by specifying which folder you want to export the quantized model to. The default post-training quantization technique is [full integer quantization](https://www.tensorflow.org/lite/performance/post_training_integer_quant). This allows the TensorFlow Lite model to be smaller, run faster on Raspberry Pi CPU and also compatible with the Google Coral EdgeTPU.

```
model.export(export_dir='.', tflite_filename='face_mask.tflite')
```

### Step 6:  Evaluate the TensorFlow Lite model.

Several factors can affect the model accuracy when exporting to TFLite:
* [Quantization](https://www.tensorflow.org/lite/performance/model_optimization) helps shrinking the model size by 4 times at the expense of some accuracy drop.
* The original TensorFlow model uses per-class [non-max supression (NMS)](https://www.coursera.org/lecture/convolutional-neural-networks/non-max-suppression-dvrjH) for post-processing, while the TFLite model uses global NMS that's much faster but less accurate.
Keras outputs maximum 100 detections while tflite outputs maximum 25 detections.

Therefore you'll have to evaluate the exported TFLite model and compare its accuracy with the original TensorFlow model.

```
model.evaluate_tflite('face_mask.tflite', val_data)
```

```
# Download the TFLite model to your local computer.
from google.colab import files
files.download('face_mask.tflite')
```

## Test the Face Mask detection model

After training the model, copy this `face_mask.tflite` model into coral_rpi/object_detection directory and
runn following python script

```
python3 detect_picamv2.py --model face_mask.tflite
```

## Compile the model for EdgeTPU

Finally, we'll compile the model using `edgetpu_compiler` so that the model can run on [Google Coral EdgeTPU](https://coral.ai/).

We start with installing the EdgeTPU compiler on Colab.

```
!curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
!echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
!sudo apt-get update
!sudo apt-get install edgetpu-compiler
```

**Note:** When training the model using a custom dataset, beware that if your dataset includes more than 20 classes, you'll probably have slower inference speeds compared to if you have fewer classes. This is due to an aspect of the EfficientDet architecture in which a certain layer cannot compile for the Edge TPU when it carries more than 20 classes.

Before compiling the `.tflite` file for the Edge TPU, it's important to consider whether your model will fit into the Edge TPU memory. 

The Edge TPU has approximately 8 MB of SRAM for [caching model paramaters](https://coral.ai/docs/edgetpu/compiler/#parameter-data-caching), so any model close to or over 8 MB will not fit onto the Edge TPU memory. That means the inference times are longer, because some model parameters must be fetched from the host system memory.

One way to elimiate the extra latency is to use [model pipelining](https://coral.ai/docs/edgetpu/pipeline/), which splits the model into segments that can run on separate Edge TPUs in series. This can significantly reduce the latency for big models.

The following table provides recommendations for the number of Edge TPUs to use with each EfficientDet-Lite model.

| Model architecture | Minimum TPUs | Recommended TPUs
|--------------------|-------|-------|
| EfficientDet-Lite0 | 1     | 1     |
| EfficientDet-Lite1 | 1     | 1     |
| EfficientDet-Lite2 | 1     | 2     |
| EfficientDet-Lite3 | 2     | 2     |
| EfficientDet-Lite4 | 2     | 3     |

If you need extra Edge TPUs for your model, then update `NUMBER_OF_TPUS` here:

```
NUMBER_OF_TPUS = 1

!edgetpu_compiler face_mask.tflite --num_segments=$NUMBER_OF_TPUS
```

Finally, we'll copy the metadata, including the label file, from the original TensorFlow Lite model to the EdgeTPU model.

```
populator_dst = metadata.MetadataPopulator.with_model_file('face_mask_edgetpu.tflite')

with open('face_mask.tflite', 'rb') as f:
  populator_dst.load_metadata_and_associated_files(f.read())

populator_dst.populate()
updated_model_buf = populator_dst.get_model_buffer()

```

```
# Download the edgeTPU TFLite model compiled for EdgeTPU to your local computer.
from google.colab import files
files.download('face_mask_edgetpu.tflite')

```

## Test the Face Mask detection model

After training the model, copy this `face_mask_edgetpu.tflite` model into coral_rpi/object_detection directory and
runn following python script with `--enableEdgeTPU`

```
python3 detect_picamv2.py --enableEdgeTPU --model face_mask_edgetpu.tflite
```
