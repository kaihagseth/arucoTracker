import cv2

import exceptions as exc
from VisionEntityClasses.Camera import Camera


class VisionEntity:
    """
    TODO: Still only supports tracking of one board. Mrvec and Mtvec needs to be updated to a dictionary containing
    TODO :Positions of all boards
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """


    _guess_pose = None

    def __init__(self, cv2_index):
        self.intrinsic_matrix = None
        self._camera = Camera(src_index=cv2_index, load_camera_parameters=True)
        self.Mrvec = None  # Camera - Model rvec
        self.Mtvec = None  # Camera - Model tvec
        self.Crvec = None  # World - Camera rvec
        self.Ctvec = None  # World - Camera tvec
        self.corners = None
        self.ids = None
        self.rejected = None
        self._camera.loadCameraParameters()
        self.setIntrinsicCamParams()

    def runThreadedLoop(self, dictionary, boards):
        while True:
            self.grabFrame()
            ret, frame = self.retrieveFrame()
            print("Frame retrieved")
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

    def getPosePreviewImage(self):
        '''

        :return:
        '''
        return self._arucoPoseEstimator.getPosePreviewImage()

    def getFrame(self):
        """
        Returns a raw frame from the camera
        :return: distortion coefficients of camera
        """
        return self._camera.getFrame()

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
        self.Mtvec = None
        self.Mrvec = None

    def setCameraPosition(self, board):
        """
        Sets the camera position in world coordinates
        :param board: The aruco board seen from cam.
        :param cam: Camera to be calibrated.
        :return:
        """
        self.Crvec, self.Ctvec = cv2.composeRT(-board.rvec, board.tvec, -self.Mrvec, -self.Mtvec,)[0:2]

    def getExtrinsicMatrix(self, frame=None):
        '''
        Returns the camera extrinsic matrix
        :return:
        '''

        ext = self._arucoPoseEstimator.getExtrinsic(frame, self.intrinsic_matrix,
                                                    self.getDistortionCoefficients())
        if ext is not None:
            return ext
        else:
            raise exc.MissingExtrinsicException('Extrinsic matrix not returned')

    def detectMarkers(self, dictionary):
        """
        Detects aruco markers and updates fields
        :param dictionary:
        :return:
        """
        frame = self.getFrame()
        if ret:
            self.corners, self.ids, self.rejected = cv2.aruco.detectMarkers(frame, dictionary)

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
        _, self.Mrvec, self.Mtvec = cv2.aruco.estimatePoseBoard(self.corners, self.ids, board.getGridBoard(),
                                                                self.intrinsic_matrix, self.getDistortionCoefficients())

    def drawAxis(self, frame):
        """
        Draws axis cross on image frame
        :param frame: Image frame to be drawn on
        :param vision_entity: Vision entity the frame came from.
        :return:
        """
        return cv2.aruco.drawAxis(frame, self.intrinsic_matrix, self._camera.getDistortionCoefficients(),
                                  self.Mrvec, self.Mtvec, 100)