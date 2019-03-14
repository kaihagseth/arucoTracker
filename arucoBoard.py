import cv2
import numpy as np
from helperFunctions import toMatrix

class arucoBoard:
    def __init__(self, board_width, board_height, marker_size, marker_gap,
                 dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)):
        self.board = cv2.aruco.GridBoard_create(board_width, board_height, marker_size, marker_gap, dictionary)
        self.rvec = None # Model World rvec
        self.tvec = None # Model World tvec
        self.isVisible = True

    def updateBoardPosition(self, vision_entity):
        """
        Sets boards pose in world coordinates from a calibrated vision entity.
        :param cam: The camera spotting the board.
        :return:
        """
        self.rvec = cv2.composeRT(vision_entity.Crvec, vision_entity.Ctvec, vision_entity.Mrvec, vision_entity.Mtvec)[0]
        self.getRelativeTranslation(vision_entity)

    def setFirstBoardPosition(self, ve):
        """
        Sets the board pose to origen and calibrates VE.
        :param ve: Vision entity to calibrate
        :return:
        """
        self.rvec = np.array([0, 0, 0], dtype=np.float32)
        self.tvec = np.array([0, 0, 0], dtype=np.float32)
        ve.setCameraPosition(self)

    def getRelativeTranslation(self, ve):
        """
        Gets translation from model to vision entity.
        :param ve: Vision entity that has board in sight.
        :return: None
        """
        self.tvec = toMatrix(ve.Crvec) * np.matrix(ve.Ctvec + ve.Mtvec)