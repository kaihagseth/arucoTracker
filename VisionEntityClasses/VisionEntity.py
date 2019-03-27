import cv2
import numpy as np
import exceptions as exc
from VisionEntityClasses.Camera import Camera
from VisionEntityClasses.helperFunctions import *
import logging


class VisionEntity:
    """
    TODO: Still only supports tracking of one board. Mrvec and Mtvec needs to be updated to a dictionary containing
    TODO: Positions of all boards
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """


    _guess_pose = None

    def __init__(self, cv2_index):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, load_camera_parameters=True)
        # cameraToModelToMatrix should be a list containing all boards
        self.__cameraToModelMatrices = []  # Camera -> Model transformation - Should only be written to from thread!!
        self._cameraPoseMatrix = None
        self._cameraPoseQuality = 0
        self._detection_quality = []
        self.runThread = False
        self.__corners = None # Detected aruco corners - Should only be written to from thread.
        self.__ids = None # Detected aruco ids - Should only be written to from thread.
        self.__rejected = None # Rejected aruco corners - Should only be written to from thread.
        self._camera.loadCameraParameters()
        self.setIntrinsicCamParams()

    def runThreadedLoop(self, dictionary, boards):
        """
        TODO: Moving grabFrame to PE might synchronize cameras.
        Runs the pose estimation loop in a thread for this vision entity.
        :param dictionary: The dictionary the pose estimator should use as a reference.
        :param boards: The board object the pose estimator should detect and calculate pose for.
        :return:
        """

        while self.runThread:
            self.grabFrame()
            self.retrieveFrame()
            self.detectMarkers(dictionary)
            for board in boards:
                self.estimatePose(board)
        self.terminate()

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
        Sets distortion coefficients for camera.
        :return: None
        """
        self._camera.setDistortionCoefficients(distortion_coefficients)

    def getUndistortedFrame(self):
        """
        Returns an undistorted frame from the camera based on the calibration. This function seems redundant for the
        current scope of this project.
        :return: Undistorted image frame
        """
        return self._camera.getUndistortedFrame()

    def getFrame(self):
        """
        Returns the newest frame the camera has saved. Note: This function only gathers the frame, it does not create
        a new one.
        :return: Camera image frame
        """
        return self._camera.getFrame()

    def getDistortionCoefficients(self):
        """
        Returns distortion coefficients of camera
        :return: distortion coefficients of camera
        """
        return self._camera.getDistortionCoefficients()

    def setIntrinsicCamParams(self):
        """
        Sets Calibration values for intrinsic matrix and distortion coefficients. Useful for using saved vales.
        :param intrinsic_matrix: Intrinsic camera matrix type np.matrix dtype=float
        :param distortion_coefficients: Distortion coefficients
        :return: None
        """
        self.intrinsic_matrix = self._camera.getIntrinsicParams()

    def getCam(self):
        """
        Returns this vision entitys Camera object
        :return: Camera object
        """
        return self._camera

    def resetExtrinsicMatrix(self):
        """
        Set model pose to None.
        :return:
        """
        self._cameraPoseMatrix = None

    def setCameraPose(self, board, boardID, threshold):
        """
        Sets the camera position in world coordinates
        :param board: The aruco board seen from cam.
        :param cam: Camera to be calibrated.
        :param threshold: threshold to be above
        :return:
        """
        origin_to_model = board.getTransformationMatrix()
        model_to_camera = invertTransformationMatrix(self.__cameraToModelMatrices[boardID])
        assert model_to_camera is not None, "Attempting to set camera pose without knowing Model->Camera transfrom"
        assert origin_to_model is not None, "Attempting to set camera pose without knowing World->Model transform"

        origin_to_camera = origin_to_model * model_to_camera
        origin_to_camera = origin_to_camera / origin_to_camera[3, 3]
        self._cameraPoseMatrix = origin_to_camera
        self.setCameraPoseQuality(board, threshold)

    def setCameraPoseQuality(self, board, threshold):
        """
        Sets the quality of the camera pose to a number between 0 and 1, based on how many markers are visible from the
        camera to be calibrated and the master camera.
        :param board:
        :return:
        """
        w, h = board.getGridBoardSize()
        detectionQuality = self.getDetectionQuality()
        boardPoseQuality = board.getPoseQuality()
        assert boardPoseQuality <= 1, "Board pose quality is above 1: bpq is " + str(boardPoseQuality)
        assert detectionQuality <= 1, "Detection quality is above 1: dq is " + str(detectionQuality)
        cameraPoseQuality = min(detectionQuality, boardPoseQuality)
        if cameraPoseQuality >= threshold:
            self._cameraPoseQuality = cameraPoseQuality
            return True
        return False

    def getCameraPoseQuality(self):
        """
        Returns camera pose quality
        :return: camera pose quality
        """
        return self._cameraPoseQuality

    def getDetectionQuality(self):
        """
        Returns model pose quality
        :return: Model pose quality
        """
        return self._detection_quality

    def detectMarkers(self, dictionary):
        """
        Detects aruco markers and updates fields
        :param dictionary:
        :return:
        """
        frame = self.getFrame()
        if frame is not None:
            self.__corners, self.__ids, self.__rejected = cv2.aruco.detectMarkers(frame, dictionary)

    def grabFrame(self):
        """
        Grabs frame from video stream
        :return:
        """
        """
        if not self.runThread: # If not interferring with poseestimation
            ret, frame = self.getCam().grabFrame()
            if ret:
                return frame
        return None"""
        cam = self.getCam()
        return cam.grabFrame()

    def retrieveFrame(self):
        """
        Retrieves grabbed frame from video stream
        :return: frame from video stream
        """
        cam = self.getCam()
        return cam.retrieveFrame()


    def estimatePose(self, board, boardID):
        """
        Estimates pose and saves pose to object field
        :param board: Board yo estimate
        :return: None
        """
        extendListToIndex(self._detection_quality, boardID, None)
        _, rvec, tvec = cv2.aruco.estimatePoseBoard(self.__corners, self.__ids, board.getGridBoard(),
                                                      self.intrinsic_matrix, self.getDistortionCoefficients())
        self.setModelPoseQuality(board)
        self.__cameraToModelMatrices[boardID] = rvecTvecToTransMatrix(rvec, tvec)

    def setModelPoseQuality(self, board, boardIndex):
        """
        Calculates the quality of the current pose estimation between the camera and the model
        # TODO: Test if recursive call is working as intended.
        :return: None
        """

        # Checks if the list is long enough to accomodate for the new board index. Extends it if not.
        extendListToIndex(self._detection_quality, boardIndex, 0)
        w, h = board.getGridBoardSize()
        detectedBoardIds = None
        boardIds = set(board.getIds())
        if self.__ids is not None:
            detectedIds = set(np.reshape(self.__ids, -1))
            detectedBoardIds = boardIds.intersection(detectedIds)
        total_marker_count = w * h
        if detectedBoardIds is not None:
            visible_marker_count = len(detectedBoardIds)
        else:
            visible_marker_count = 0
        self._detection_quality = visible_marker_count / total_marker_count
        #return None
        #7print(self.__cameraToModelMatrix)
        #print("Cam index: ", self._camera.getSrc())
        if self.__cameraToModelMatrix is not None:
            z1 = np.asarray(self.__cameraToModelMatrix[0:3, 2]).flatten() # Get the z-row
            z2 = np.asarray(np.matrix([0, 0, 1]).T).flatten()
            print("Z1: ", z1)
            print("Z2: ", z2)
            msg1 = self.__cameraToModelMatrix
            logging.debug(msg1)
            q = np.linalg.norm(np.dot(z1,z2)) / (np.linalg.norm(z1) * np.linalg.norm(z2))
            msg = "Q: ", q
            logging.debug(msg)
        else:
            logging.error("__cameraToModelMatrix not set.")
        self._detection_quality[boardIndex] = visible_marker_count / total_marker_count

    def drawAxis(self):
        """
        TODO: Multi object support.
        Draws axis cross on image frame
        :param frame: Image frame to be drawn on
        :param vision_entity: Vision entity the frame came from.
        :return:
        """
        image = self.getFrame()
        image = cv2.aruco.drawDetectedMarkers(image, self.__corners, self.__ids)
        for matrix in self.__cameraToModelMatrices:
            rvec, tvec = transMatrixToRvecTvec(matrix)
            image = cv2.aruco.drawAxis(image, self.intrinsic_matrix, self._camera.getDistortionCoefficients(),
                                    rvec, tvec, 100)
        return image

    def getPoses(self):
        """
        Returns pose from private fields.
        :return: Transformation matrix from camera to model
        """
        return self.__cameraToModelMatrices

    def getCameraPose(self):
        """
        Returns homogenous camera extrinsic matrix
        :return: Rotation and translation vectors for cameras pose.
        """
        return self._cameraPoseMatrix

    def getCornerDetectionAttributes(self):
        """

        :return:
        """
        return self.__corners, self.__ids, self.__rejected

    def terminate(self):
        """
        Readies Vision Entity for termination
        :return:
        """
        self._camera.terminate()

