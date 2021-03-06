######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# Author: @CameronTrumpy
# Date: 7/31/2021
# Description: 
# This program uses a TensorFlow Lite model to perform object detection on a live webcam
# feed. It draws boxes and scores around the objects of interest in each frame from the
# webcam. To improve FPS, the webcam object runs in a separate thread from the main program.
# This script will work with either a Picamera or regular USB webcam.
#
# This code is based off the TensorFlow Lite image classification example at:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
#
# I added my own method of drawing boxes and labels using OpenCV.

# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
from processes.PITemp import PITemp
from processes.VideoStream import VideoStream
from processes.MJPGHandler import MJPGHandler
from networktables import NetworkTables
from networktables.util import ChooserControl

#Init NT server
serverIP='192.168.1.232'
NetworkTables.initialize(server=serverIP)
NetworkTables.deleteAllEntries()
nTable = NetworkTables.getTable('FroggyVision')
statusTable = nTable.getSubTable('status')
tgtTable = nTable.getSubTable('targets')

mainTgt = tgtTable.getSubTable('mainTgt')
altTgts = tgtTable.getSubTable('altTgts')

##START TARGETING MODE and type METHODS
#tgtModes = ["largest", "centermost", "most_confident"]
# largest = 0 centermost = 1 most_confident = 2
def getTargetMode():
    mode = tgtTable.getNumber('tgtMode', 0)
    return mode

statusTable.putNumber('tgtMode', 0)

def getTargetType():
    type = statusTable.getString('tgtType', "robot")
    return type

statusTable.putString('tgtType', "robot")



##END TARGETING MODE METHODS

##TARGET LIST AND METHODS
mainTgtList = [
    #example entry
    #{'tgtNum': 0,'area': 0, 'conf': 0.0, 'tX': 0.0, 'tY': 0.0}    
]

maintN = 1

def gettA(target):
    return target.get('tA')

def gettConf(target):
    return target.get('tConf')

def getpNum(target):
    return target.get('tgtNum')

def gettX(target):
    return target.get('tX')

def gettY(target):
    return target.get('tY')

def getXCenter(target):
    return target.get('xCenter')

def getYCenter(target):
    return target.get('yCenter')
##END TARGET LIST METHODS

xFov = 60
yFov = 34

# Define and parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                    required=True)
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=0.5)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                    default='1280x720')
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                    action='store_true')

args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
use_TPU = args.edgetpu

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter
    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME = 'edgetpu.tflite'       

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

# Load the Tensorflow Lite model.
# If using Edge TPU, use special load_delegate argument
if use_TPU:
    interpreter = Interpreter(model_path=PATH_TO_CKPT,
                              experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print(PATH_TO_CKPT)
else:
    interpreter = Interpreter(model_path=PATH_TO_CKPT)

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()

# Initialize video stream & output mjpg stream
videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
mjpgStream = MJPGHandler().start()
time.sleep(1)

#for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
while True:

    # Start timer (for calculating frame rate)
    t1 = cv2.getTickCount()

    # Grab frame from video stream
    frame1 = videostream.read()

    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std
        print("nonquant")

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
    
    #reset robot list before next detection iteration
    mainTgtList.clear()
    
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    mainTgtN = 0
    altTgtN = 0
    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
           
            tgtXCenter = xmin + ((xmax-xmin)/2.0)
            tgtYCenter = ymin + ((ymax-ymin)/2.0)
            
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name + " " + str(mainTgtN), int(scores[i]*100)) # Example: 'robot: 72%'  
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
            
            
            
             #Populating target list 
            if(object_name == getTargetType()):

                    tArea = ((xmax-xmin)*(ymax-ymin))
                    confidence = int(scores[i]*100.0)
                    tX = ((tgtXCenter - (imW/2.0))*((xFov/2.0)/(imW/2.0)))
                    tY = ((tgtYCenter - (imH/2.0))*((xFov/2.0)/(imH/2.0)))

                    mainTgtList.append({'tgtNum': mainTgtN, 'tA': tArea, 'tConf': confidence,
                                      'tX': tX, 'tY': tY, 'xCenter':tgtXCenter, 'yCenter':tgtYCenter})

                    mainTgtN += 1
            else:
                altTgtN += 1
                    
    
    altTgts.putNumber('targetCount', altTgtN)

    # Draw framerate in corner of frame and send to NT
    cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,0),1,cv2.LINE_AA)
    statusTable.putNumber("FPS", frame_rate_calc)
    tempC = PITemp.readTemp()
    statusTable.putNumber("CPU Temp", tempC)
    cv2.putText(frame,'{0:.1f}C'.format(tempC),(20,65),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,0),1,cv2.LINE_AA)


    #populate NT with saved target list, reversed sort ensures sorting in descending order    
    
    if getTargetMode() == 0:
        mainTgtList.sort(key=gettA, reverse=True)
    elif getTargetMode() == 1:
        mainTgtList.sort(key=gettX)
    elif getTargetMode() == 2:
        mainTgtList.sort(key=gettConf, reverse=True)

    #if there are any main targets, take the highest priority target. draw target crosshair and populate NT data
    if len(mainTgtList) > 0:
        t = mainTgtList[0]
        mainTgt.putValue("area", gettA(t)/(1000))
        mainTgt.putNumber("conf", int(gettConf(t)))
        mainTgt.putValue("tX", gettX(t))
        mainTgt.putValue("tY", gettY(t))
        
        xCenter = int(getXCenter(t))
        yCenter = int(getYCenter(t))

        cv2.line(frame, (xCenter-4,yCenter), (xCenter+4,yCenter), (0, 255, 0), 2)
        cv2.line(frame, (xCenter,yCenter-4), (xCenter,yCenter+4), (0, 255, 0), 2)

    # All the results have been drawn on the frame, so it's time to display it.
    #cv2.imshow('Object detector', frame)
    mjpgStream.writeFrame(frame)

    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1

    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
mjpgStream.stop()
videostream.stop()


