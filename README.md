# TensorFlow-Lite-Object-Detection-on-Raspberry-Pi

## Introduction
TensorFlow Lite is an optimized framework for deploying lightweight deep learning models on resource-constrained edge devices. TensorFlow Lite models have faster inference time and require less processing power, so they can be used to obtain faster performance in realtime applications. This guide provides step-by-step instructions for how to run a Tensorflow Lite model on the Raspberry Pi with and without a Google Coral Co-processor.


This repository contains Python code for running the converted TensorFlow Lite model to perform detection on webcam input, with data output over NetworkTables, and a MJPG video stream. You can utilized quantized or non-quantized models based on the script you run and if you have a Google Coral Co-processor.

## Section 1 - Setting up the Pi
### Step 1. Setup Raspi OS
Follow the instructions at https://www.raspberrypi.org/software for OS imaging and setup. We currently use [Raspberry Pi OS with Desktop](https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit), the one that does not include "reccomended software".
### Step 2. Download Repo
Once your PI is set up and running, open a terminal and navigate to your documents directory.
```
cd Documents
```
Then, use git to clone the repository. This will create a new directory, ```/Documents/TFliteNT/```. This is where all of the files will be downloaded to.
```
git clone https://github.com/FF503/TFliteNT
```
### Step 3. Setup Environment
To set up your environment, run the ```setup.sh``` file. This file handles getting you the correct apt and python packages, and setting up your python virtual environment.
```
cd TFliteNT
sh setup.sh
```




## Section 2 - Run the TensorFlow Lite model!

The following instructions show how to run the webcam script. These instructions assume your .tflite model file and labelmap.txt file are in the same directory.


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

## Common Errors
