# Define NTProcessor Class to contain and handle networktables processes

from threading import Thread
from networktables import NetworkTables
from networktables.util import ChooserControl


class NTProcessor:
    """NT Object that handles passing data back and forth from networktables"""

    nTable = None
    statusTable = None
    tgtTable = None
    mainTgt = None

    def __init__(self,serverIP=('1.1.1.1')):
        # Initialize NetworkTables
        NetworkTables.initialize(server=serverIP)
        NetworkTables.deleteAllEntries()
        
        nTable = NetworkTables.getTable('FroggyVision')
        statusTable = nTable.getSubTable('status')
        tgtTable = nTable.getSubTable('targets')
        mainTgt = tgtTable.getSubTable('mainTgt')

        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the NT Processor is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

    ####
    #NT GETTERS AND SETTERS

    
    def getTargetMode():
        mode = statusTable.getNumber("Targeting Mode", 0)
        return mode

    statusTable.putNumber("Targeting Mode", 0)