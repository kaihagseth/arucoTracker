import cv2
import numpy as np
import exceptions as exc
from VisionEntityClasses.helperFunctions import invertTransformationMatrix
from VisionEntityClasses.Camera import Camera


class VisionEntity:
    """
    TODO: Still only supports tracking of one board. Mrvec and Mtvec needs to be updated to a dictionary containing
    TODO: Positions of all boards
    TODO: Protect thread-sensitive fields.
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """


    _guess_pose = None

    def __init__(self, cv2_index):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, load_camera_parameters=True)
        self._ModelWrtCam = None  # Transformation model --> camera
        self._CamWrtWorld = None  # Transformation camera --> world
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

    def resetModelPose(self):
        """
        Set model pose to None.
        :return:
        """
        self._ModelWrtCam = None

    def setCameraPosition(self, board):
        """
        Sets the camera position in world coordinates
        :param board: The aruco board seen from cam.
        :param cam: Camera to be calibrated.
        :return:
        """
        self._CamWrtWorld = board.getModelWrtWorld()*invertTransformationMatrix(self._ModelWrtCam)

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
        return self.getCam().grabFrame()

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
        :param board: Board yo estomate
        :return: None
        """
        _, rvec, tvec = cv2.aruco.estimatePoseBoard(self.__corners, self.__ids, board.getGridBoard(),
                                                                    self.intrinsic_matrix, self.getDistortionCoefficients())
        if rvec is not None:
            R = np.matrix(cv2.Rodrigues(rvec)[0])
            P = np.reshape(np.matrix(tvec), (3, 1))
            T = np.matrix(np.eye(4, 4))
            T[0:3, 0:3] = R
            T[0:3, 3] = P
            self._ModelWrtCam = T


    def drawAxis(self):
        """
        Draws axis cross on image frame
        :param frame: Image frame to be drawn on
        :param vision_entity: Vision entity the frame came from.
        :return:
        """
        R = cv2.Rodrigues(self._ModelWrtCam[0:3, 0:3])[0]
        P = self._ModelWrtCam[0:3, 3].T
        image = self.getFrame()
        image = cv2.aruco.drawDetectedMarkers(image, self.__corners, self.__ids)
        image = cv2.aruco.drawAxis(image, self.intrinsic_matrix, self._camera.getDistortionCoefficients(),
                                  R, P, 100)

        return image
    def getModelWrtCam(self):
        """
        Returns pose from private fields.
        :return: rotation and translation vectors from camera to boards.
        """
        return self._ModelWrtCam

    def getCamWrtWorld(self):
        """
        Returns camera pose
        :return: Rotation and translation vectors for cameras pose.
        """
        return self._CamWrtWorld

    def getCorners(self):
        """
        Returns corners
        :return: corners of aruco markers in image coordinates
        """
        return self.__corners

    def getIds(self):
        """
        returns aruco ids
        :return:
        """
        return self.__ids