import cv2
import numpy as np
import time
import threading
from VisionEntityClasses.ArucoBoard import ArucoBoard
from VisionEntityClasses.helperFunctions import *

class Merger:
    """
    The merger class merges several aruco boards to one, by looking at the relationship between the main board and
    each of the sub boards.
    """
    def __init__(self, dictionary, main_board=None, sub_boards=None):
        self.main_board = main_board
        self.sub_boards = sub_boards
        self.linkQualityDisplayFX = None
        self.running = False
        self.dictionary = dictionary
        self.merged_board = None
        self.displayFunction = None

    @staticmethod
    def mergerCostFunction(main_board, sub_board):
        """
        The over all  quality of the link is decided by the minimum quality of the two compared boards
        :return: Board quality weight.
        """
        link_quality = min(main_board.getPoseQuality(), sub_board.getPoseQuality())
        return link_quality

    def mergeBoards(self):
        """
        Creates the new merged board after all boards have calculated
        :return: None
        """
        ids = self.main_board.getIds()
        obj_points = self.main_board.getObjPoints()
        for sub_board in self.sub_boards:
            ids = np.concatenate((ids, sub_board.getIds()))
            assert (sub_board.link_matrix is not None), "Can't finish merging boards before all sub boards has" \
                                                        " at least one reference to main board"

            transformed_points = sub_board.getTransformedPoints(sub_board.link_matrix)
            obj_points = np.concatenate((obj_points, transformed_points))
        self.dictionary = self.main_board.dictionary
        print("Merger creating merged board")
        self.merged_board = ArucoBoard(board=cv2.aruco.Board_create(obj_points, self.dictionary, ids),
                                       dictionary=self.dictionary)

    def runMerge(self):
        """
        Threaded loop responsible for running the merger.
        :return: None
        """
        while self.running:
            main_trans_matrix = self.main_board.getTransformationMatrix()
            if main_trans_matrix is not None:
                for sub_board in self.sub_boards:
                    sub_trans_matrix = sub_board.getTransformationMatrix()
                    potential_link_quality = self.mergerCostFunction(self.main_board, sub_board)
                    if sub_board.link_quality < potential_link_quality:
                        print("link quality updated, for board new quality: " + str(potential_link_quality))
                        sub_board.link_quality = potential_link_quality
                        sub_board.link_matrix = invertTransformationMatrix(main_trans_matrix) * \
                                                    sub_trans_matrix
            if self.displayFunction:
                self.displayFunction(self.getQualityList())
            time.sleep(.1)

    def startMerge(self):
        """
        Initializes and starts the merger.
        :return: None
        """
        for sub_board in self.sub_boards:
            sub_board.link_quality = 0
            sub_board.link_matrix = None
            sub_board.meanTransformationMatrixFinder = IterativeMeanTransformationFinder()
        self.running = True
        th = threading.Thread(target=self.runMerge)
        th.start()

    def finishMerge(self):
        """
        Stops the merger and returns the merged board.
        :return: merged board
        """
        self.running = False
        self.mergeBoards()
        print("Merging completed")
        return self.merged_board

    def getQualityList(self):
        """
        Returns a list describing the link quality between the main board and the sub boards.
        :return: List of values describing link quality between boards.
        """
        qualityList = []
        for board in self.sub_boards:
            qualityList.append(board.link_quality)
        return qualityList

    def getBoards(self):
        """
        Returns all  boards used by this merger.
        :return: Main board followed by sub boards in a single list.
        """
        boards = dict()
        boards["merged_board"] = self.merged_board
        boards["main_board"] = self.main_board
        boards["sub_boards"] = self.sub_boards
        return boards

    def setDisplayFunction(self, dispFX):
        """
        Sets the display function to use for diplaying this mergers quality list.
        :param dispFX:
        :return: None
        """
        self.displayFunction = dispFX
