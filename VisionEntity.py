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
        self.camera = Camera()
        self.single_frame_point_detector = SingleFramePointDetector
        self.intrinsic_calibrator = IntrinsicCalibrator
        self.single_camera_pose_estimator = SingleCameraPoseEstimator

    def detectPoints(self):
        """
        :return: A list of the largest circles found in cameras frame (x,y,r)
        """
        return self.single_frame_point_detector.findBallPoints(self.getFrame())

    def calibrateCameraWithTool(self):
        """
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self.camera.calibrateCamera()

     def calibrateCameraWithImages(self, images):
         """
         Calibrates intrinsic matrix and distortion coefficients for camera.
         :return: None
         """
         self.camera.calibrateCam(images)

    def setCameraIntrinsicParameters(self, intrinsic_parameters):
        """
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self.camera.set_intrinsic_params(intrinsic_parameters)

    def setCameraDistortionCoefficents(self, distortion_coefficients):
        """
        Calibrates intrinsic matrix and distortion coefficients for camera.
        :return: None
        """
        self.camera.set_distortion_coefficients(distortion_coefficients)

    def calibratePointDetector(self):
        """
        Opens color calibration tool for image segmentation.
        :return: None
        """
        self.single_frame_point_detector.calibrate(self.camera.getStream())

    def getObjectPose(self):
        """
        :return: A list of the six axis of the model.
        """
        # get points from point detector, then plug points into pose estimator to get six axis
        return self.single_camera_pose_estimator.estimateModelPose(self.detectPoints())

    def getFrame(self):
        """
        Returns the current frame from camera.
        :return: A frame from this object's camera object.
        """
        return self.camera.getFrame()