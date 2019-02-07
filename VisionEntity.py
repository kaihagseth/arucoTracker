from Camera import Camera
from SingleFramePointDetector import SingleFramePointDetector
from IntrinsicCalibrator import IntrinsicCalibrator
from SingleCameraPoseEstimator import SingleCameraPoseEstimator



class VisionEntity:
    """
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream.
    """

    def __init__(self):
        self._camera = Camera()
        self._single_frame_point_detector = SingleFramePointDetector()
        self._intrinsic_calibrator = IntrinsicCalibrator()
        self._single_camera_pose_estimator = SingleCameraPoseEstimator()

    def detectPoints(self):
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

