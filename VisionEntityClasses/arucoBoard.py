import cv2
import numpy as np
from fpdf import FPDF

from VisionEntityClasses.helperFunctions import toMatrix


class arucoBoard():
    # TODO: Maybe loosen up coupling by removing links to vision entity.
    first_marker = 0

    def __init__(self, board_width, board_height, marker_size, marker_gap,
                 dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)):
        self.dictionary = dictionary
        self._board = cv2.aruco.GridBoard_create(board_width, board_height, marker_size, marker_gap, dictionary,
                                                 self.first_marker)
        self._certainty = None
        self._ModelWrtWorld = None  # Transformation model --> world
        self.board_height = board_height
        self.board_width = board_width
        self.isVisible = True # Truth value to tell if this board is visible to at least one vision entity
        self.first_marker = self.first_marker + (self.board_height * self.board_width)

    def getGridBoard(self):
        return self._board

    def getModelWrtWorld(self):
        """
        Returns model to world transformation
        :return:
        """
        return self._ModelWrtWorld

    def updateBoardPosition(self, vision_entity):
        """
        Sets boards pose in world coordinates from a calibrated vision entity.
        :param cam: The camera spotting the board.
        :return:
        """
        self._ModelWrtWorld = vision_entity.getCamWrtWorld()*vision_entity.getModelWrtCam()

    def setFirstBoardPosition(self, ve):
        """
        Sets the board pose to origen and calibrates VE.
        :param ve: Vision entity to calibrate
        :return:
        """
        self._ModelWrtWorld = np.matrix(np.identity(4))
        ve.setCameraPosition(self)

    def setCertainty(self, certainty):
        self._certainty = certainty

    def getCertainty(self):
        return self._certainty

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