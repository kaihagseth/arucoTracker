import numpy as np
import logging

from WebcamVideoStream import WebcamVideoStream
import cv2
from IntrinsicCalibrator import IntrinsicCalibrator as ic

class Camera():
    """
    Class for Camera.
    """
    def __init__(self, cam_name = "Cam0", src_index=0, camera_pose_matrix=None, camera_label='A1',
                 activateSavedValues = True):
        '''Create a cam '''
        print("Creating OTCam")
        #self._ID = cam_id # A distinct number for each camera.
        self._name = cam_name
        self.camera_parameters = {'mtx': None, 'ret': None, 'dist': None, 'rvecs': None, 'tvecs': None,
                                 'newcameramtx': None, 'roi': None}
        self._src = src_index
        self._vidCap = cv2.VideoCapture(self._src)
        # Test
        if not self._vidCap.open(self._src):
            logging.error('Camera not opened!!')
        if activateSavedValues:
            self.loadCameraParameters(camera_label)

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

    def set_intrinsic_params(self, new_mtrx):
        '''Set intrinsic params for the camera'''
        self.camera_parameters['mtx'] = new_mtrx
        logging.info('Intrinsic param set.')

    def getIntrinsicParams(self):
        """
        returns intrinsic camera matrix
        :return: Intrinsic camera matrix
        """
        return self.camera_parameters['mtx']

    def setIntrinsicParams(self, intrinsic_params):
        """
        :param intrinsic_params: New intrinsic matrix
        :return: None
        """
        self.camera_parameters['mtx'] = intrinsic_params

    def setDistortionCoefficients(self, distortion_coefficients):
        """
        :param distortion_coefficients: new distortion coefficients
        :return: None
        """
        self.camera_parameters['dist'] = distortion_coefficients


    def getDistortionCoefficients(self):
        """
        :return: distortion coefficients
        """
        return self.camera_parameters['dist']

    def getSingleFrame(self):
        '''Get non-threaded camera frame.'''
        grabbed, frame = self._vidCap.read()
        if not grabbed:
            logging.error('Camera grabbed unsuccesfully.')
        return frame

    def calibrateCam(self, cbFrames):
        '''
        Calibrate the camera in the IC-section.
        :param cbFrame:
        :return:
        '''
        self.camera_parameters = ic.calibCam(cbFrames)

    def getUndistortedFrame(self):
        "Get threaded, undistorted frame. "
        img = ic.getUndistortedFrame(self.getFrame())
        return img


    def loadCameraParameters(self, camera_id='A1'):
        '''Load and use the earlier saved intrinsic parameters from a file.
        :param filename: Name of file to get params from.
        '''
        filename =  'calibValues/' + camera_id +'calib.npz'
        self.camera_parameters = ic.loadSavedValues(filename)

    def getSrc(self):
        return self._src