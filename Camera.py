import numpy as np
from WebcamVideoStream import WebcamVideoStream
import cv2
from IntrinsicCalibrator import IntrinsicCalibrator
import imutils
from heapq import nlargest
from math import pi
import time


class Camera():
    """
    Class for Camera.
    # TODO: Refactoring
    """
    def __init__(self, cam_name = "Cam0", cam_id = 0, src_index=0, camera_pose_matrix=None, intrinsic_camera_matrix=None):
        '''Create a cam '''
        print("Creating OTCam")
        self._ID = cam_id # A distinct number for each camera.
        self._name = cam_name
        self._intrinsic_camera_matrix = intrinsic_camera_matrix
        self._distortion_coefficients
        self._cam_pose = camera_pose_matrix
        self._src = src_index
        self._vidCap = cv2.VideoCapture(self._src)
        self._IC = IntrinsicCalibrator(self)

    def startVideoStream(self):
        '''
        Start threaded vidstream. Needs more work.
        :return:
        '''
        self._video_stream_thread = WebcamVideoStream(src=0, camName=self._name)
        self._video_stream_thread.start()

    def getStream(self):
        """
        Returns video stream
        :return: Video stream
        """
        return self._vidCap

    def getFrame(self):
        '''Get frame from vidthread.'''
        self._vidstreamthread.read()

    def set_intrinsic_params(self, intrinsic_params):
        """
        :param intrinsic_params: New intrinsic matrix
        :return: None
        """
        self._intrinsic_camera_matrix = intrinsic_params

    def set_distortion_coefficients(self, distortion_coefficients):
        """
        :param distortion_coefficients: new distortion coefficients
        :return: None
        """
        self._distortion_coefficients = distortion_coefficients


    def calibrateCamera(self):
        '''
        Calibrate the camera.
        Take a image, find the
        :return:
        '''
    def getSingleFrame(self):
        '''Get non-threaded camera frame.'''
        grabbed, frame = self._vidCap.read()
        return frame

    def calibrateCam(self, cbFrames):
        '''
        Calibrate the camera in the IC-section.
        :param cbFrame:
        :return:
        '''
        self._IC.calibCam(cbFrames)

    def loadSavedCalibValues(self):
        self._IC.loadSavedValues()

    def undistort(self, img):
        '''Return a undistorted version of a distorted image. '''
        self._IC.undistort_image(img)
    def activateSavedValues(self, filename='IntriCalib.npz'):
        '''Load and use the earlier saved intrinsic parameters from a file.
        :param filename: Name of file to get params from.
        '''
        self._IC.loadSavedValues(filename)

    # Code based upon this guide: https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
    # import the necessary packages

#otc1 = OTCam()
#otc2 = OTCam(camName="Cam2",srcIndex=1)
#time.sleep(1)
#frame = otc1.getFrame()
#print(frame)
#cv2.imshow("Hello",frame)
#cv2.waitKey(0)