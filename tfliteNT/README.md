# TensorFlow-Lite-Object-Detection-on-Raspberry-Pi

## Introduction
TensorFlow Lite is an optimized framework for deploying lightweight deep learning models on resource-constrained edge devices. TensorFlow Lite models have faster inference time and require less processing power, so they can be used to obtain faster performance in realtime applications. This guide provides step-by-step instructions for how train a custom TensorFlow Object Detection model, convert it into an optimized format that can be used by TensorFlow Lite, and run it on Android phones or the Raspberry Pi.


This repository contains Python code for running the converted TensorFlow Lite model to perform detection on images, videos, or webcam feeds. You can utilized quantized or non-quantized models based on the script you run and if you have a Google Coral TPU Coprocessor.

##Step 1. Setup your Pi.
### 1a. Setup Raspi OS
### 1b. Download Repo
### 1c. Setup Environment

#### Step 3c. Run the TensorFlow Lite model!
I wrote three Python scripts to run the TensorFlow Lite object detection model on an image, video, or webcam feed: TFLite_detection_image.py, TFLite_detection_video.py, and [TFLite_detection_wecam.py](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py). The scripts are based off the label_image.py example given in the [TensorFlow Lite examples GitHub repository](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py).

The following instructions show how to run the webcam, video, and image scripts. These instructions assume your .tflite model file and labelmap.txt file are in the “TFLite_model” folder in your \object_detection directory as per the instructions given in this guide.

If you’d like try using the sample TFLite object detection model provided by Google, simply download it [here](https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip) and unzip it into the \object_detection folder. Then, use `--modeldir=coco_ssd_mobilenet_v1_1.0_quant_2018_06_29` rather than `--modeldir=TFLite_model` when running the script. 

For more information on options that can be used while running the scripts, use the `-h` option when calling the script. For example:

```
python TFLite_detection_image.py -h
```

##### Webcam
Make sure you have a USB webcam plugged into your computer. If you’re on a laptop with a built-in camera, you don’t need to plug in a USB webcam. 

From the \object_detection directory, issue: 

```
python TFLite_detection_webcam.py --modeldir=TFLite_model 
```

After a few moments of initializing, a window will appear showing the webcam feed. Detected objects will have bounding boxes and labels displayed on them in real time.

##### Video stream
To run the script to detect images in a video stream (e.g. a remote security camera), issue: 

```
python TFLite_detection_stream.py --modeldir=TFLite_model --streamurl="http://ipaddress:port/stream/video.mjpeg" 
```

After a few moments of initializing, a window will appear showing the video stream. Detected objects will have bounding boxes and labels displayed on them in real time.

Make sure to update the URL parameter to the one that's being used by your security camera. It has to include authentication information in case the stream is secured.

If the bounding boxes are not matching the detected objects, probably the stream resolution wasn't detected. In this case you can set it explicitly by using the `--resolution` parameter:

```
python TFLite_detection_stream.py --modeldir=TFLite_model --streamurl="http://ipaddress:port/stream/video.mjpeg" --resolution=1920x1080
```

##### Image
To run the image detection script, issue:

```
python TFLite_detection_image.py --modeldir=TFLite_model
```

The image will appear with all objects labeled. Press 'q' to close the image and end the script. By default, the image detection script will open an image named 'test1.jpg'. To open a specific image file, use the `--image` option:

```
python TFLite_detection_image.py --modeldir=TFLite_model --image=squirrel.jpg
```

It can also open an entire folder full of images and perform detection on each image. There can only be images files in the folder, or errors will occur. To specify which folder has images to perform detection on, use the `--imagedir` option:

```
python TFLite_detection_image.py --modeldir=TFLite_model --imagedir=squirrels
```

Press any key (other than 'q') to advance to the next image. Do not use both the --image option and the --imagedir option when running the script, or it will throw an error.


* [Part 2. How to Run TensorFlow Lite Object Detection Models on the Raspberry Pi (with optional Coral USB Accelerator)](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Raspberry_Pi_Guide.md)
* Part 3. How to Run TensorFlow Lite Object Detection Models on Android Devices 

## Frequently Asked Questions and Common Errors

#### Why does this guide use train.py rather than model_main.py for training?
This guide uses "train.py" to run training on the TFLite detection model. The train.py script is deprecated, but the model_main.py script that replaced it doesn't log training progress by default, and it requires pycocotools to be installed. Using model_main.py requires a few extra setup steps, and I want to keep this guide as simple as possible. Since there are no major differences between train.py and model_main.py that will affect training ([see TensorFlow Issue #6100](https://github.com/tensorflow/models/issues/6100)), I use train.py for this guide.

#### How do I check which TensorFlow version I used to train my detection model?
Here’s how you can check the version of TensorFlow you used for training.  

1. Open a new Anaconda Prompt window and issue `activate tensorflow1` (or whichever environment name you used)  
2. Open a python shell by issuing `python`  
3. Within the Python shell, import TensorFlow by issuing `import tensorflow as tf`  
4. Check the TensorFlow version by issuing `tf.__version__` . It will respond with the version of TensorFlow. This is the version that you used for training. 

#### Building TensorFlow from source
In case you run into error `error C2100: illegal indirection` during TensorFlow compilation, simply edit the file `tensorflow-build\tensorflow\tensorflow\core\framework\op_kernel.h`, go to line 405, and change `reference operator*() { return (*list_)[i_]; }` to `reference operator*() const { return (*list_)[i_]; }`. Credits go to: https://github.com/tensorflow/tensorflow/issues/15925#issuecomment-499569928
