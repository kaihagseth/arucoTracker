import cv2
import numpy as np
import logging
import copy
from fpdf import FPDF
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.helperFunctions import *


class ArucoBoard:
    # TODO: first_marker should only be updated when board is added to tracking list.
    first_marker = 0
    nextIndex = 0

    def __init__(self, board_width=0, board_height=0, marker_size=0, marker_gap=0,
                 dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50), board=None):
        self._poseQuality = 0 # How good the current estimated pose is from a scale from 0 to 1.
        self._transformationMatrix = None # World -> Model transformation
        self._tracking_ve = None # The vision entity that is currently responsible for tracking this board
        self.ID = ArucoBoard.nextIndex
        ArucoBoard.nextIndex += 1
        self.dictionary = dictionary
        if board is not None:
            self._board = board
            return
        self._board = cv2.aruco.GridBoard_create(board_width, board_height, marker_size, marker_gap, dictionary,
                                                 self.first_marker)
        ArucoBoard.first_marker = self.first_marker + (board_height * board_width)

    def getGridBoardSize(self):
        return self._board.getGridSize()

    def getMarkerCount(self):
        return len(self.getObjPoints())

    def getGridBoard(self):
        return self._board

    def getRvecTvec(self):
        """
        Returns pose in rvec, tvec-format
        :return: rvec, tvec
        """
        return transMatrixToRvecTvec(self._transformationMatrix)

    def updateBoardPose(self):
        """
        Sets boards pose in world coordinates from a calibrated vision entity.
        # FIXME: Sometimes causes crashes when ve loses sight of board?
        :param cam: The camera spotting the board.
        :return:
        """
        camera_to_model_transformation = self._tracking_ve.getPoses()[self.ID]
        world_to_camera_transformation = self._tracking_ve.getCameraPose()
        world_to_model_transformation = world_to_camera_transformation * camera_to_model_transformation #Crash here
        self._transformationMatrix = world_to_model_transformation
        self.setPoseQuality(self.calculatePoseQuality())

    def setFirstBoardPosition(self, ve):
        """
        Sets the board pose to origen and calibrates VE.
        :param ve: Vision entity to calibrate
        :param q_threshold: Minimum accepted quality.
        :return: ret
        """
        self._transformationMatrix = np.matrix(np.eye(4, dtype=np.float32))
        self.setPoseQuality(1)
        ve.setCameraPose(self)
        ve.setCameraPoseQuality(1)
        return True

    def calculatePoseQuality(self):
        """
        Returns the pose quality for this board based on the tracking ves detection quality and pose quality
        :return: Pose quality
        """
        assert self._tracking_ve.getCameraPoseQuality() <= 1, "master camera camera pose quality is above 1"
        assert self._tracking_ve.getDetectionQuality()[self.ID] <= 1, "master camera detection quality is above 1"
        return self._tracking_ve.getDetectionQuality()[self.ID] * self._tracking_ve.getCameraPoseQuality()

    def setPoseQuality(self, quality):
        """
        Calculates and sets pose quality based on the vision entity's camera pose quality and pose estimation quality.
        :param master_entity:
        :return:
        """
        self._poseQuality = quality

    def getPoseQuality(self):
        return self._poseQuality

    def writeBoardToPDF(self, width=160):
        """
        Creates a printable pdf-file of this aruco board.
        :param width: Max width of this image
        :param length: Max length of this image
        :return: None
        """
        grid_size = self._board.getGridSize()
        marker_length = self._board.getMarkerLength()
        marker_separation = self._board.getMarkerSeparation()

        width = (grid_size[0] * marker_length) + (marker_separation * (grid_size[0] - 1))
        height = (grid_size[1] * marker_length) + (marker_separation * (grid_size[1] - 1))

        board_image = self._board.draw((int(width*12), int(height*12))) # About 300 dpi
        cv2.imwrite("arucoBoard.png", board_image)

        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.image("arucoBoard.png", w=width, h=height)
        pdf.image("images/arrow.png", x=20, y=height+20, w=30)
        pdf.output("arucoBoard.pdf")

    def getIds(self):
        """
        Retrieves the Ids of this boards markers.
        :return: Ids of this boards markers.
        """
        return copy.copy(self._board.ids)

    def getBoardImage(self, size):
        """
        :param size: Size of drawn image in pixels
        :return: cv2 image array of board.
        """
        if isinstance(self._board, cv2.aruco_GridBoard):
            return self._board.draw(size)
        elif isinstance(self._board, cv2.aruco_Board):
            return np.zeros((size[0], size[0], 3), np.uint8)
        else:
            return None

    def getTrackingEntity(self):
        """
        Returns the vision entity that is currently tracking this board.
        :return: the vision entity that is currently tracking this board.
        """
        return self._tracking_ve

    def setTrackingEntity(self, ve):
        """
        Sets the vision entity that has the responsibility for tracking this board.
        :param ve: the vision entity that is currently tracking this board.
        :return:
        """
        self._tracking_ve = ve

    def interpolateObstructedIds(self):
        self.__corners, self.__ids, self.__rejected, recovered = cv2.aruco.refineDetectedMarkers()

    def getObjPoints(self):
        """
        Returns a copy of the arucoboards obj-points.
        :return: an array of size nx4x3 for n markers in the board, containing relative cartesian coordinates of
        points
        """
        return copy.copy(self._board.objPoints)

    def getTransformationMatrix(self):
        """
        Returns a copy of this boards transformation matrix
        :return: A homogenous transformation matrix describing this boards relation to world
        """
        return copy.copy(self._transformationMatrix)

    def getTransformedPoints(self, transformationMatrix):
        """
        Returns a transformed object point list from this board.
        :return: This boards transformed object points.
        """
        objpoints = np.array(self.getObjPoints())
        transformed_points = np.zeros(objpoints.shape, dtype=np.float32)
        for i, marker in enumerate(objpoints):
            for j, corner in enumerate(marker):
                transformed_points[i][j] = transformPointHomogeneous(corner, transformationMatrix)
        return transformed_points
