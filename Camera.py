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
        print("Creating OTCam")
        self._ID = camID # A distinct number for each camera.
        self._name = camName
        self._intri_cam_mtrx = intri_cam_mtrx
        self._cam_loca = cam_loca
        self._cam_pose = cam_pose_mtrc
        self.src = srcIndex
        self.vidCap = cv2.VideoCapture(self.src)
        self._aov = aov
        self.IC = IntrinsicCalibration()

    def startVidStream(self):
        self._vidstreamthread = WebcamVideoStream(src=0,camName=self._name)
        self._vidstreamthread.start()
    def getFrame(self):
        self._vidstreamthread.read()

    def set_intrinsic_params(self, new_mtrx):
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
        grabbed, frame = self.vidCap.read()
        return frame

    def saveFrameToCalib(self, cbFrame):
        #print('Chessboardframe is saved to this came on index ', self._ID, '.')
        self.IC.calibCamVeg(cbFrame)

    def undistort(self, img):
        self.IC.undistortImage(img)
    def activateSavedValues(self, filename='IntriCalib.npz'):
        self.IC.loadSavedValues(filename)
#otc1 = OTCam()
#otc2 = OTCam(camName="Cam2",srcIndex=1)
#time.sleep(1)
#frame = otc1.getFrame()
#print(frame)
#cv2.imshow("Hello",frame)
#cv2.waitKey(0)