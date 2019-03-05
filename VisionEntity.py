import time
from Camera import Camera
from IntrinsicCalibrator import IntrinsicCalibrator
from arucoPoseEstimator import ArucoPoseEstimator
import numpy as np
import exceptions as exc
import logging


class VisionEntity:
    """
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """

    _guess_pose = None

    def __init__(self, cv2_index, board_length=3, board_width=3, marker_size=30, marker_gap=5):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, activateSavedValues=True)
        self._arucoPoseEstimator = ArucoPoseEstimator(board_length, board_width, marker_size, marker_gap)
        self._intrinsic_calibrator = IntrinsicCalibrator()
        self._camera.loadCameraParameters()
        self.setIntrinsicCamParams()

    def runThreadedLoop(self, singlecam_curr_pose, singlecam_curr_pose_que, frame_que):
        while True:
            frame = self.getFrame()
            frame_que.put(frame)
            singlecam_curr_pose = self.getModelPose(frame)
            singlecam_curr_pose_que.put(singlecam_curr_pose)
         #   logging.info("Running threaded loop")

    def calibrateCameraWithTool(self):
        """
        # TODO: This function is not yet created in camera Class.
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self._camera.calibrateCamera()

    def calibrateCameraWithImages(self, images):
        """
        Calibrates the cameras Intrinsic matrix and distortion coefficients from a collection of images.
        :param images: Images to use to use for camera calibration
        :return: None
        """
        self._camera.calibrateCam(images)

    def setCameraIntrinsicParameters(self, intrinsic_parameters):
        """
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self._camera.setIntrinsicParams(intrinsic_parameters)

    def setCameraDistortionCoefficents(self, distortion_coefficients):
        """
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self._camera.setDistortionCoefficients(distortion_coefficients)


    def getCameraStream(self):
        """
        returns Video stream from Camera
        :return: Video stream from camera.
        """
        return self._camera.getStream()

    def getUndistortedFrame(self):
        """
        Returns an undistorted frame from the camera basaed on the calibration
        :return: Undistorted image frame
        """
        return self._camera.getUndistortedFrame()

    def getModelPose(self, frame):
        """
        Returns six axis pose of model
        :return: Tuple of size 2 with numpy arrays (x, y, z) (pitch, yaw, roll) (angles in degrees)
        """
        showFrame = True
        return self._arucoPoseEstimator.getModelPose(frame, self.intrinsic_matrix,
                                                     self.getDistortionCoefficients(), showFrame=showFrame)

    def getFrame(self):
        """
        Returns a raw frame from the camera
        :return: distortion coefficients of camera
        """
        return self._camera.getSingleFrame()

    def getDistortionCoefficients(self):
        """
        Returns distortion coefficients of camera
        :return: distortion coefficients of camera
        """
        return self._camera.getDistortionCoefficients()

    def setModelReferenceFrame(self):
        """
        #TODO: write this function
        :return:
        """
        raise NotImplementedError("setModelReferenceFrame has not yet been written")

    def setIntrinsicCamParams(self):
        """
        Sets Calibration values for intrinsic matrix and distortion coefficients. Useful for using saved vales.
        :param intrinsic_matrix: Intrinsic camera matrix type np.matrix dtype=float
        :param distortion_coefficients: Distortion coefficients
        :return: None
        """
        self.intrinsic_matrix = self._camera.getIntrinsicParams()

    def getCam(self):
        return self._camera
