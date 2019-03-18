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
        self._rvec = None # Model World rvec
        self._tvec = None # Model World tvec
        self.board_height = board_height
        self.board_width = board_width
        self.isVisible = True # Truth value to tell if this board is visible to at least one vision entity
        self.first_marker = self.first_marker + (self.board_height * self.board_width)

    def getGridBoard(self):
        return self._board

    def setRvec(self, rvec):
        """
        Sets rvec field for this object
        :param rvec: new rvec
        :return: None
        """
        self._rvec = rvec


    def getRvec(self):
        """
        Retuns objects rvec-field
        :return: rvec
        """
        return self._rvec

    def setTvec(self, tvec):
        """
        Sets tvec field for this object
        :param rvec: new rvec
        :return: None
        """
        self._tvec = tvec

    def getTvec(self):
        """
        Retuns objects tvec-field
        :return: tvec
        """
        return self._tvec

    def updateBoardPosition(self, vision_entity):
        """
        Sets boards pose in world coordinates from a calibrated vision entity.
        :param cam: The camera spotting the board.
        :return:
        """
        Mrvec, Mtvec = vision_entity.getPoses()
        Crvec, Ctvec = vision_entity.getCameraPose()
        self._rvec = cv2.composeRT(Crvec, Ctvec, Mrvec, Mtvec)[0]
        self.setRelativeTranslation(vision_entity)

    def setFirstBoardPosition(self, ve):
        """
        Sets the board pose to origen and calibrates VE.
        :param ve: Vision entity to calibrate
        :return:
        """
        self._rvec = np.array([0, 0, 0], dtype=np.float32)
        self._tvec = np.array([0, 0, 0], dtype=np.float32)
        ve.setCameraPosition(self)

    def setRelativeTranslation(self, ve):
        """
        Gets translation from model to vision entity.
        :param ve: Vision entity that has board in sight.
        :return: None
        """
        Mrvec, Mtvec = ve.getPoses()
        Crvec, Ctvec = ve.getCameraPose()
        self._tvec = toMatrix(Crvec) * np.matrix(Ctvec + Mtvec)

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