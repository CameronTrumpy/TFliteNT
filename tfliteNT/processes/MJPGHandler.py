# MJPG Output stream, which streams the processed video input to be displayed at the driver station
# THIS IS YOUR OUTPUT VIDEO STREAM WITH ALL POST PROCESSING

# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/ & @n3wtron - https://gist.github.com/n3wtron/4624820s

from threading import Thread
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import cv2

processedFrame = None
server = None
class MJPGHandler:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self):
        # Initialize the PiCamera and the camera image stream
        # Read frame from the stream
        

		# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
		# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        server = ThreadedHTTPServer(('localhost', 8080), CamHandler)
        print("server started at http://127.0.0.1:8080/cam.html")
        server.serve_forever()
        return self


    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = processedFrame

    def writeFrame(self, frame):
        processedFrame = frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True
        server.socket.close()



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"Threaded Server"

class CamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()
            while True:
                try:

                    rc, img = processedFrame.read()
                    if not rc:
                        continue

                    img_str = cv2.imencode('.jpg', img)[1].tostring()

                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(img_str))
                    self.end_headers()

                    self.wfile.write(img_str)
                    self.wfile.write(b"\r\n--jpgboundary\r\n")

                except KeyboardInterrupt:
                    self.wfile.write(b"\r\n--jpgboundary--\r\n")
                    break
                except BrokenPipeError:
                    continue
            return

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><head></head><body>')
            self.wfile.write(b'<img src="http://127.0.0.1:8080/cam.mjpg"/>')
            self.wfile.write(b'</body></html>')
            return