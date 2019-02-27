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

    def __init__(self, cv2_index, board_length, board_width, marker_size, marker_gap):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, activateSavedValues=True)
        self._arucoPoseEstimator = ArucoPoseEstimator(board_length, board_width, marker_size, marker_gap)
        self._intrinsic_calibrator = IntrinsicCalibrator()
        self._camera.loadSavedCalibValues()
        self.setIntrinsicCamParams()


    def findPoseResult_th(self, singlecam_curr_pose, singlecam_curr_pose_que):
        '''
        Function to thread.
        :param singlecam_curr_pose:
        :param singlecam_curr_pose_que:
        :return:
        '''
        logging.info('Starting getPoseFromCams()')
        use_non_threaded_distorted_cam = True
        run = True
        reference_not_set = True
        while reference_not_set:
            try: # Set reference frame
                self.intrinsic_matrix = self._camera.getIntrinsicParams()
                if self.intrinsic_matrix is None:
                    logging.error('Intrinsic camera matrix is None.')
                if use_non_threaded_distorted_cam:
                    frame = self._camera.getSingleFrame()
                else:
                    frame = self._camera.getUndistortedFrame()
                img_points = self._single_frame_point_detector.findBallPoints(frame)
                img_points = img_points[:, 0:2]  # Don't include circle radius in matrix.
                #singlecam_curr_pose = self._single_camera_pose_estimator.getPose(self._camera.getIntrinsicParams(),
                 # img_points, None)
                #self._single_camera_pose_estimator.setReference(self.intrinsic_matrix, image_points=img_points)
                self._single_camera_pose_estimator.testSetReference(self.intrinsic_matrix, image_points=img_points)
                logging.info('Referenceframe is set.')
                reference_not_set = False
            except exc.MissingIntrinsicCameraParametersException as intErr:
                logging.error('Unsuccesfull setting reference frame. Did not get intrinsic params.')
                print(intErr.msg)
            except exc.MissingImagePointException as imgErr:
                logging.error('Unsuccesfull setting reference frame. Did not find the ball points.')
                print(imgErr.msg)


        while run: # Run application and get pose results for real
            try:
                if use_non_threaded_distorted_cam:
                    frame = self._camera.getSingleFrame()
                else:
                    frame = self._camera.getUndistortedFrame()
                img_points = self._single_frame_point_detector.findBallPoints(frame)
                img_points = img_points[:, 0:2] # Don't include circle radius in matrix.
                #singlecam_curr_pose, self._guess_pose = self._single_camera_pose_estimator.getPose(self.intrinsic_matrix, img_points, guess_pose=self._guess_pose)
                singlecam_curr_pose, self._guess_pose = self._single_camera_pose_estimator.testGetPose(self.intrinsic_matrix, img_points, guess_pose=self._guess_pose)
                print("Guess_pose: ", self._guess_pose)
                result = self._guess_pose
                try:
                    print("#####  Guess_pose:  ###### ")
                    # print(result)
                    print("Rotation x - roll: ", result[0] * 180.0 / np.pi, " grader")
                    print("Rotation y - pitch: ", result[1] * 180.0 / np.pi, " grader")
                    print("Rotation z - yaw: ", result[2] * 180.0 / np.pi, " grader")
                    print("Position x: ", result[3], ' mm')
                    print("Position y: ", result[4], ' mm')
                    print("Position z: ", result[5], ' mm')
                except TypeError:
                    print("Could not print.")
                msg = "Guess pose: ", str(self._guess_pose)
                logging.debug(msg)
            except exc.MissingReferenceFrameException as refErr:
                print('ERROR: ',refErr.msg)
           # print('Singlecam_curr_pose: ', singlecam_curr_pose)
            time.sleep(0.5) # MUST BE HERE
            singlecam_curr_pose_que.put(singlecam_curr_pose)

            #print('Singlecam_curr_pose: ', singlecam_curr_pose)
            time.sleep(0.5)  # MUST BE HERE
            singlecam_curr_pose_que.put(singlecam_curr_pose)

    def getFramePoints(self):
        """
        Finds x, y and radius of circles in current video stream frame from camera.
        :return: A list of the largest circles found in cameras frame (x,y,r)
        """
        return self._single_frame_point_detector.findBallPoints(self._camera.getSingleFrame())

    def runThreadedLoop(self):
        while True:
            frame = self.getFrame()
            self.getModelPose(frame)


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
