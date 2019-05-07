import logging
import cv2
import numpy as np
from VisionEntityClasses import IntrinsicCalibrator as ic
from exceptions import CamNotOpenedException

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
        logging.info("Creating Camera: Name: " + str(cam_name) + "; Label: " + str(camera_label) + "Index: " + str(src_index))
        self._name = cam_name
        self.camera_label = camera_label
        self.camera_parameters = {'mtx': None, 'ret': None, 'dist': None, 'rvecs': None, 'tvecs': None,
                                  'newcameramtx': None, 'roi': None}
        self._src = src_index
        self._frame = None
        self._vidCap = cv2.VideoCapture(self._src)
        self._vidCap.set(cv2.CAP_PROP_AUTOFOCUS, False)
        self._vidCap.set(cv2.CAP_PROP_FOCUS, 0.0)
        # Test
        if not self._vidCap.open(self._src):
            logging.error('Camera not opened!')
            raise CamNotOpenedException("Cam not opened on corresponding index.")
        if load_camera_parameters:
            self.loadCameraParameters()

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

    def calibrateCam(self, cbFrames):
        '''
        Calibrate the camera in the IC-section.
        :param cbFrame:
        :return:
        '''
        self.camera_parameters = ic.calibCam(cbFrames)

    def getUndistortedFrame(self):
        "Get threaded, undistorted frame. "
        img = ic.getUndistortedFrame(self.getFrame(), self.camera_parameters)
        return img

    def loadCameraParameters(self):
        """Load and use the earlier saved intrinsic parameters from a file.
        :param filename: Name of file to get params from.
        """
        filename =  'calibValues/' + self.camera_label +'.npz'
        try:
            npzfile = np.load(filename)
            npzfile2 = np.load('calibValues/A1calib.npz')
            #logging.debug(str(filename))
            #print("Fil 2 keys dict:")
            #for k in npzfile.files():
            #    print(k)
            #
            #logging.debug(str(filename))
            #for k in npzfile.files():
            #    print(k)
            self.camera_parameters = {'mtx': npzfile['mtx'], 'dist': npzfile['dist'],
                                      'newcameramtx': npzfile['newcameramtx'], 'roi': npzfile['roi']}
            logging.info("New camera values has been set.")
        except IOError as e:
            logging.error('Calib file not found in dictionary.' + str(e))
        except KeyError as e:
            logging.error('.' + str(e))

    def saveCameraParameters(self):
        """
        Saves current camera values to a file
        :return:
        """
        filename = 'calibValues/' + self.camera_id +'.npz'
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
        return ret, self._frame

    def getFrame(self):
        """
        Returns saved frame from camera.
        :return: Frame
        """
        return self._frame

    def terminate(self):
        """
        Readies camera for termination
        :return:
        """
        self._vidCap.release()

    def setCamLabel(self, callname):
        """
        Set new label and import new camera settings from filename with accordingly
        :param callname: New label, i.e. A2 or B9. MAX LENGTH TWO letters/numbers!
        :return: None
        """
        self.camera_label = callname
        self.loadCameraParameters()