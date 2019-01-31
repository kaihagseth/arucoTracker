import numpy as np
from WebcamVideoStream import WebcamVideoStream
import cv2
from IntrinsicCalibration import IntrinsicCalibration
import time

'''
Class for Object Tracking Camera.
'''
class Camera():
    def __init__(self,camName="Cam0", camID=0, srcIndex=0, cam_loca=False, cam_pose_mtrc=None, aov=False, intri_cam_mtrx=None):
        '''Create a cam '''
        print("Creating OTCam")
        self._ID = camID # A distinct number for each camera.
        self._name = camName
        self._intri_cam_mtrx = intri_cam_mtrx
        self._cam_loca = cam_loca
        self._cam_pose = cam_pose_mtrc
        self.src = srcIndex
        self.vidCap = cv2.VideoCapture(self.src)
        self._aov = aov
        self._IC = IntrinsicCalibration(self)

    def startVidStream(self):
        '''
        Start threaded vidstream. Needs more work.
        :return:
        '''
        self._vidstreamthread = WebcamVideoStream(src=0,camName=self._name)
        self._vidstreamthread.start()
    def getFrame(self):
        '''Get frame from vidthread.'''
        self._vidstreamthread.read()

    def set_intrinsic_params(self, new_mtrx):
        '''Set intrinsic params for the camera'''
        self._intri_cam_mtrx = new_mtrx

    def set_dist_coeff(self, new_dist_coeff):
        self._dist_coeff = new_dist_coeff


    def calibrateCamera(self):
        '''
        Calibrate the camera.
        Take a image, find the
        :return:
        '''
    def getSingleFrame(self):
        '''Get non-threaded camera frame.'''
        grabbed, frame = self.vidCap.read()
        return frame

    def calibrateCam(self, cbFrames):
        '''
        Calibrate the camera in the IC-section.
        :param cbFrame:
        :return:
        '''
        self._IC.calibCam(cbFrames)

    def undistort(self, img):
        '''Return a undistorted version of a distorted image. '''
        self._IC.undistortImage(img)
    def activateSavedValues(self, filename='IntriCalib.npz'):
        '''Load and use the earlier saved intrinsic parameters from a file.
        :param filename: Name of file to get params from.
        '''
        self._IC.loadSavedValues(filename)
#otc1 = OTCam()
#otc2 = OTCam(camName="Cam2",srcIndex=1)
#time.sleep(1)
#frame = otc1.getFrame()
#print(frame)
#cv2.imshow("Hello",frame)
#cv2.waitKey(0)