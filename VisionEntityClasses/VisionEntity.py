import cv2
import numpy as np
import exceptions as exc
from VisionEntityClasses.Camera import Camera
from VisionEntityClasses.helperFunctions import *
import logging


class VisionEntity:
    """
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """


    _guess_pose = None

    def __init__(self, cv2_index):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, load_camera_parameters=True)
        # cameraToModelToMatrix should be a list containing all boards
        self.__cameraToModelMatrices = dict()  # Camera -> Model transformation - Should only be written to from thread!!
        self._cameraPoseMatrix = None
        self._cameraPoseQuality = 0
        self._detection_quality = dict()
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
            for board in boards.values():
                logging.debug("Estimating pose for board "+ str(board.ID))
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

    def setCameraPose(self, board):
        """
        Sets the camera position in world coordinates
        :param board: The aruco board seen from cam.
        :param cam: Camera to be calibrated.
        :param threshold: threshold to be above
        :return:
        """
        print("This message should only pop up once or twice")
        origin_to_model = board.getTransformationMatrix()
        model_to_camera = invertTransformationMatrix(self.__cameraToModelMatrices[board.ID])
        assert model_to_camera is not None, "Attempting to set camera pose without knowing Model->Camera transfrom"
        assert origin_to_model is not None, "Attempting to set camera pose without knowing World->Model transform"
        origin_to_camera = origin_to_model * model_to_camera
        origin_to_camera = origin_to_camera / origin_to_camera[3, 3]
        self._cameraPoseMatrix = origin_to_camera

    def calculatePotentialCameraPoseQuality(self, board):
        """
        Checks what the camera pose quality would be with current parameters.
        :param board: Board to check camera pose quality in relation to.
        :return: potential camera pose quality
        """
        detectionQuality = self.getDetectionQuality()[board.ID]
        boardPoseQuality = board.getPoseQuality()
        assert boardPoseQuality <= 1, "Board pose quality is above 1: bpq is " + str(boardPoseQuality)
        assert detectionQuality <= 1, "Detection quality is above 1: dq is " + str(detectionQuality)
        return detectionQuality * boardPoseQuality

    def setCameraPoseQuality(self, quality):
        """
        Sets the camera pose quality.
        :param quality: The board to calculate camera pose quality from
        :return: None
        """
        self._cameraPoseQuality = quality

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


    def estimatePose(self, board):
        """
        Estimates pose and saves pose to object field
        :param board: Board yo estimate
        :return: None
        """
        _, rvec, tvec = cv2.aruco.estimatePoseBoard(self.__corners, self.__ids, board.getGridBoard(),
                                                    self.intrinsic_matrix, self.getDistortionCoefficients())
        self.setModelPoseQuality(board)
        self.__cameraToModelMatrices[board.ID] = rvecTvecToTransMatrix(rvec, tvec)

    def setModelPoseQuality(self, board):
        """
        Calculates the quality of the current pose estimation between the camera and the model
        :return: None
        """
        # Checks if the list is long enough to accomodate for the new board index. Extends it if not.
        w, h = board.getGridBoardSize()
        detectedBoardIds = None
        boardIds = np.reshape(board.getIds(), -1)#set(board.getIds())
        detectedBoardIds = np.array([])
        if self.__ids is not None:
            detectedIds = np.reshape(self.__ids, -1)
            detectedBoardIds = np.intersect1d(boardIds, detectedIds)
        total_marker_count = w * h
        self._detection_quality[board.ID] = detectedBoardIds.size / total_marker_count
        return None
        #7print(self.__cameraToModelMatrix)
        #print("Cam index: ", self._camera.getSrc())
        CToMMatrix = self.__cameraToModelMatrices[board.ID]
        if CToMMatrix is not None:
            z1 = np.asarray(CToMMatrix[0:3, 2]).flatten() # Get the z-row
            z2 = np.asarray(np.matrix([0, 0, 1]).T).flatten()
            print("Z1: ", z1)
            print("Z2: ", z2)
            msg1 = CToMMatrix
            logging.debug(msg1)
            q = np.linalg.norm(np.dot(z1, z2)) / (np.linalg.norm(z1) * np.linalg.norm(z2))
            msg = "Q: ", q
            logging.debug(msg)
        else:
            logging.error("__cameraToModelMatrix not set.")

    def drawAxis(self):
        """
        Draws axis cross on image frame
        :param frame: Image frame to be drawn on
        :param vision_entity: Vision entity the frame came from.
        :return:
        """
        image = self.getFrame()
        image = cv2.aruco.drawDetectedMarkers(image, self.__corners, self.__ids)
        for matrix in self.__cameraToModelMatrices.values():
            if matrix is not None:
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
        Returns saved values from co
        :return: None
        """
        return self.__corners, self.__ids, self.__rejected

    def terminate(self):
        """
        Readies Vision Entity for termination
        :return: None
        """
        self._camera.terminate()

    def addBoards(self, boards):
        """
        Extends cameraToModelMatrices list to accommodate for tracking of more boards.
        :param boards: The board to add to tracking list.
        :return: None
        """
        if isinstance(boards,dict):
            for board in boards.values():
                self.__cameraToModelMatrices[board.ID] = None
                self._detection_quality[board.ID] = 0
        else:
            self.__cameraToModelMatrices[boards.ID] = None
            self._detection_quality[boards.ID] = 0

    def removeBoard(self, board):
        """
        Removes an aruco board from the tracker.
        :param board: The boar to remove
        :return: None
        """

    def getCameraID(self):
        """
        Returns camera ID
        :return: camera Id
        """
        return self._camera.getSrc()

    def setCameraLabelAndParameters(self, callname="A1"):
        """
        Give camera a new 'name' and thus search for a new settingsfile for this name.
        :param callname: New callname to camera
        :return:
        """
        self._camera.setCamLabel(callname)