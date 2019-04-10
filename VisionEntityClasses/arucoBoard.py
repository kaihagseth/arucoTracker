import cv2
import numpy as np
import logging
import copy
from fpdf import FPDF
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.helperFunctions import *


class arucoBoard:
    # TODO: first_marker should only be updated when board is added to tracking list.
    first_marker = 0

    def __init__(self, board_width, board_height, marker_size, marker_gap,
                 dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)):
        self._tracking_ve = None # The vision entity that is currently responsible for tracking this board
        self.ID = None
        self.dictionary = dictionary
        self._board = cv2.aruco.GridBoard_create(board_width, board_height, marker_size, marker_gap, dictionary,
                                                 self.first_marker)
        self._transformationMatrix = None # World -> Model transformation
        self._poseQuality = 0 # How good the current estimated pose is from a scale from 0 to 1.
        self.board_height = board_height
        self.board_width = board_width
        arucoBoard.first_marker = self.first_marker + (self.board_height * self.board_width)



    def getGridBoardSize(self):
        return self._board.getGridSize()

    def getGridBoard(self):
        return self._board

    def getRvecTvec(self):
        """
        Returns pose in rvec, tvec-format
        :return: rvec, tvec
        """
        return transMatrixToRvecTvec(self._transformationMatrix)

    def getTransformationMatrix(self):
        """
        Retuns board pose transformation matrix
        :return: board pose transformation matrix
        """
        return self._transformationMatrix

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
        return np.reshape(self._board.ids, -1)

    def getBoardImage(self, size):
        """
        :param size: Size of drawn image in pixels
        :return: cv2 image array of board.
        """
        return self._board.draw(size)

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

    @staticmethod
    def mergeBoards(main_board, sub_boards):
        """
        Merges a list of arucoboard to a single board. This function should be called every time a higher quality scan
        of the boards have been done.
        TODO: TEST ME
        :param boards: A list of the arucoboards that should be merged.
        :return: The merged board.
        """

        dictionary = main_board.getDictionary()
        ids = []
        obj_points = []
        ids.append(main_board.getIds())
        obj_points.append(main_board.getObjpoints())
        for sub_board in sub_boards:        # For each board to add
            ids.append(sub_board.getIds())  # Add ids to a list.
            sub_board_pose = sub_board.getTransformationMatrix()
            main_board_pose = main_board.getTransformationMatrix()
            inv_main_board_pose = invertTransformationMatrix(main_board_pose)
            relative_sub_board_pose = sub_board_pose * inv_main_board_pose
            sub_board_obj_points = sub_board.getObjPoints()
            new_board_obj_points = copy.copy(sub_board_obj_points)
            for markeridx, marker in enumerate(sub_board_obj_points):
                newMarker = []
                for corneridx, corner in enumerate(marker):
                    newCorner = transformPointHomogeneous(corner, relative_sub_board_pose)
                    newMarker.append(newCorner)
                obj_points.append(newMarker)
            obj_points.append(new_board_obj_points)
        mergedBoard = cv2.aruco.Board_create(obj_points, dictionary, ids)
        return mergedBoard

    def interpolateObstructedIds(self):
        self.__corners, self.__ids, self.__rejected, recovered = cv2.aruco.refineDetectedMarkers()

    def getObjPoints(self):
        """
        Returns a copy of the arucoboards obj-points.
        :return: an array of size nx4x3 for n markers in the board, containing relative cartesian coordinates of
        points
        """
        return copy.copy(self._board.objPoints)
