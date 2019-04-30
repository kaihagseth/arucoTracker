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
        print("Merger initializing")
        self.main_board = main_board
        self.sub_boards = sub_boards
        self.running = False
        self.dictionary = dictionary
        self.mergedBoard = None

    def mergerCostFunction(self, transformationmatrices):
        """
        Calculates a weight for a set of transformation-matrices based on the angle of the board as seen from the camera.
        This function is logarithmic in order to preserve the strongest measurements and discard the weakest.
        :return: Board quality weight.
        """
        minCos = 0
        for matrix in transformationmatrices:
            minCos = min(minCos, findCosineToBoard(matrix))
        weight = np.power(10, minCos*10)
        return weight

    def mergeBoards(self):
        """
        Creates the new merged board after all boards have calculated
        :return: None
        """
        ids = self.main_board.getIds()
        obj_points = self.main_board.getObjPoints()
        for sub_board in self.sub_boards:
            ids = np.concatenate((ids, sub_board.getIds()))
            transformed_points = sub_board.getTransformedPoints(sub_board.link_matrix)
            obj_points = np.concatenate((obj_points, transformed_points))
        self.dictionary = self.main_board.dictionary
        self.mergedBoard = ArucoBoard(arucoBoard=cv2.aruco.Board_create(obj_points, self.dictionary, ids),
                                      dictionary=self.dictionary)

    def runMerge(self):
        """
        Threaded loop responsible for running the merger.
        :return: None
        """
        while self.running:
            if self.main_board.transformationMatrix is not None:
                for sub_board in self.sub_boards:
                    if sub_board.transformationMatrix is not None:
                        link_matrix = invertTransformationMatrix(self.main_board.transformationMatrix) * \
                                                    sub_board.transformationMatrix
                        weight = self.mergerCostFunction([self.main_board.transformationMatrix,
                                                          sub_board.transformationMatrix])
                        sub_board.meanTransformationMatrixFinder.update(link_matrix, weight)
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
        print("Starting merger thread")
        th = threading.Thread(target=self.runMerge)
        th.start()

    def finishMerge(self):
        """
        Stops the merger and returns the merged board.
        :return: merged board
        """
        self.running = False
        for sub_board in self.sub_boards:
            sub_board.link_matrix = sub_board.meanTransformationMatrixFinder.get()
        self.mergeBoards()
        print("Merging completed")
        return self.mergedBoard

    def getQualityList(self):
        """
        Returns a list describing the link quality between the main board and the sub boards.
        :return: List of values describing link quality between boards.
        """
        qualityList = []
        for board in self.sub_boards:
            qualityList.append(board.meanTransformationMatrixFinder.getCumWeights())
        return qualityList

    def getBoards(self):
        """
        Returns a list of all boards used as input for this merger.
        :return: Main board followed by sub boards in a single list.
        """
        return [self.main_board] + self.sub_boards