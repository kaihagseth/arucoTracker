from Camera import Camera
import SingleFramePointDetector
import IntrinsicCalibrator
import SingleCameraPoseEstimator



class VisionEntity:
    """
    Represents a stand alone vision entity that handles a camera and the logic that can be applied to a single video
    stream
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

    def calibrateCamera(self):
        self.camera.calibrateCamera()

    def calibratePointDetector(self):
        self.single_frame_point_detector.calibrate(self.camera.getStream())

    def getObjectPose(self):
        """
        :return: A list of the six axis of the model.
        """
        # get points from point detector, then plug points into pose estimator to get six axis
        return self.single_camera_pose_estimator.estimateModelPose(self.detectPoints())

    def getFrame(self):
        """
        :return: A frame from this classes camera object.
        """
        return self.camera.getFrame()