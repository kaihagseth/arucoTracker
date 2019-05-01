# import the necessary packages
from threading import Thread
import threading
import cv2, logging


class WebcamVideoStream:
    def __init__(self, src=0,camName="Cam0"):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.threadname =   "ImgGrab_ {0}".format(camName)

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, name=self.threadname, args=()).start()
        logging.info(threading.current_thread().name, " starting")
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            print(self.frame)
            if self.grabbed is False:
                logging.error("Not successfull capture.")

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True