import time
from Camera import Camera
from SingleFramePointDetector import SingleFramePointDetector
from IntrinsicCalibrator import IntrinsicCalibrator
from SingleCameraPoseEstimator import SingleCameraPoseEstimator
import numpy as np
import exceptions as exc
import logging

class VisionEntity:
    """
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """

    def __init__(self, cv2_index):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, activateSavedValues=True)
        self._single_frame_point_detector = SingleFramePointDetector()
        self._intrinsic_calibrator = IntrinsicCalibrator()
        self._single_camera_pose_estimator = SingleCameraPoseEstimator()


    def findPoseResult_th(self, singlecam_curr_pose, singlecam_curr_pose_que):
        '''
        Function to thread.
        :param singlecam_curr_pose:
        :param singlecam_curr_pose_que:
        :return:
        '''
        logging.info('Starting getPoseFromCams()')
        useNonThreadedDistortedCam = True
        run = True
        while run:
            #singlecam_curr_pose = singlecam_curr_pose + random.random() - 0.5

            try:
                if useNonThreadedDistortedCam:
                    frame = self._camera.getSingleFrame()
                else:
                    frame = self._camera.getUndistortedFrame()
                img_points = self._single_frame_point_detector.findBallPoints(frame)
                singlecam_curr_pose = self._single_camera_pose_estimator.getPose(self._camera.getIntrinsicParams(),img_points,None)
            except exc.MissingReferenceFrameException as refErr:
                print('ERROR: ',refErr.msg)
            print('Singlecam_curr_pose: ', singlecam_curr_pose)
            time.sleep(0.5) # MUST BE HERE
            singlecam_curr_pose_que.put(singlecam_curr_pose)

            print('Singlecam_curr_pose: ', singlecam_curr_pose)
            time.sleep(0.5)  # MUST BE HERE
            singlecam_curr_pose_que.put(singlecam_curr_pose)

    def getFramePoints(self):
        """
        Finds x, y and radius of circles in current video stream frame from camera.
        :return: A list of the largest circles found in cameras frame (x,y,r)
        """
        return self._single_frame_point_detector.findBallPoints(self._camera.getSingleFrame())

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
        self._camera.set_intrinsic_params(intrinsic_parameters)

    def setCameraDistortionCoefficents(self, distortion_coefficients):
        """
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self._camera.set_distortion_coefficients(distortion_coefficients)

    def calibratePointDetector(self):
        """
        Opens color calibration tool for image segmentation.
        :return: None
        """
        self._single_frame_point_detector.calibrate(self._camera.getStream())

    def getObjectPose(self):
        """
        Returns Object pose
        :return: A list of the six axis of the model.
        """
        # get points from point detector, then plug points into pose estimator to get six axis
        return self._single_camera_pose_estimator.estimateModelPose(self.detectPoints())

    def setHSV(self, lower_values, upper_values):
        """
        Sets the HSV values for the image segmenter in the point detector class
        :param lower_values: 3 long tuple with lower threshold for Hue, Saturation and Value
        :param upper_values: 3 long tuple with upper threshold for Hue, Saturation and Value
        :return: None
        """
        self._single_frame_point_detector.setHSVValues(lower_values, upper_values)

    def getHSV(self):
        """
        returns HSV-values from the image segmenter
        :return: lower_values, upper_values with thresholds for Hue Saturation and Value
        """
        return self._single_frame_point_detector.getHSVValues()

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

    def getModelPose(self):
        """
        Returns six axis pose of model
        :return: Tuple of size 6 with (x, y, z, pitch, yaw, roll) (angles in radians)
        """
        return self._single_camera_pose_estimator.getPose(self.intrinsic_matrix, self.getFramePoints())

    def setModelReferenceFrame(self):
        """
        #TODO: write this function
        :return:
        """
        raise NotImplementedError("setModelReferenceFrame has not yet been written")

    def setCalibrationValues(self, intrinsic_matrix, distortion_coefficients):
        """
        Sets Calibration values for intrinsic matrix and distortion coefficients. Useful for using saved vales.
        :param intrinsic_matrix: Intrinsic camera matrix type np.matrix dtype=float
        :param distortion_coefficients: Distortion coefficients
        :return: None
        """
        self.intrinsic_matrix = intrinsic_matrix
        self._camera.set_distortion_coefficients(distortion_coefficients)
    def getCam(self):
        return self._camera