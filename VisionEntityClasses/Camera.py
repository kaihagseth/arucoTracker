import logging

import cv2
import numpy as np

from VisionEntityClasses import IntrinsicCalibrator as ic
from WebcamVideoStream import WebcamVideoStream


class Camera():
    """
    Class for Camera.
    """
    def __init__(self, cam_name="Cam0", src_index=0, camera_label='A1',
                 load_camera_parameters=True):
        """
        :param cam_name: Name of camera
        :param src_index: Index opencv uses to access this camera
        :param camera_label: String corresponding to yellow label on camera.
        :param loadCameraParameters: Flag to decide if you should load this cameras parameters.
        """
        print("Creating Camer: Name: ", cam_name, "; Label: ", camera_label, "Index: ", src_index)
        self._name = cam_name
        self.camera_label = camera_label
        self.camera_parameters = {'mtx': None, 'ret': None, 'dist': None, 'rvecs': None, 'tvecs': None,
                                  'newcameramtx': None, 'roi': None}
        self._src = src_index
        self._frame = None
        self._vidCap = cv2.VideoCapture(self._src)
        # Test
        if not self._vidCap.open(self._src):
            logging.error('Camera not opened!')
        if load_camera_parameters:
            self.loadCameraParameters()

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

    def loadCameraParameters(self):
        """Load and use the earlier saved intrinsic parameters from a file.
        :param filename: Name of file to get params from.
        """
        filename =  'calibValues/' + self.camera_label +'calib.npz'
        npzfile = np.load(filename)
        self.camera_parameters = {'mtx': npzfile['mtx'], 'dist': npzfile['dist'],
                             'newcameramtx': npzfile['newcameramtx'], 'roi': npzfile['roi']}

    def saveCameraParameters(self):
        """
        Saves current camera values to a file
        :return:
        """
        filename = 'calibValues/' + self.camera_id +'calib.npz'
        np.savez(filename, ret=self.camera_parameters['ret'], mtx=self.camera_parameters['mtx'],
                 dist=self.camera_parameters['dist'], rvecs=self.self.camera_parameters['rvecs'],
                 tvecs=self.self.camera_parameters['tvecs'], newcameramtx=self.camera_parameters['newcameramtx'],
                 roi=self.camera_parameters['newcameramtx'])

    def getSrc(self):
        return self._src

    def grabFrame(self):
        """
        Grabs frame from stream
        :return:  None
        """
        return self._vidCap.grab()

    def retrieveFrame(self):
        """
        retrieves frame from stream
        :return: retval, frame
        """
        ret, self._frame = self._vidCap.retrieve()
        return ret, self._vidCap.retrieve()


    def getFrame(self):
        """
        Returns saved frame from camera.
        :return: Frame
        """
        return self._frame
