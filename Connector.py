import json
import logging
from logging.config import dictConfig
import time
from PoseEstimator import PoseEstimator
from GUI.GUI import GUIApplication
from GUI.GUILogin import GUILogin
import json
import logging
import time
from logging.config import dictConfig

from GUI.GUI import GUIApplication
from GUI.GUILogin import GUILogin
from PoseEstimator import PoseEstimator
from threading import Thread

class Connector():
    '''
    Connect the UI with rest of the application.
    Start the GUI.
    '''

    def __init__(self):#ui_string):
        self.logging_setup()
        self.PE = PoseEstimator()

    def run(self):
        self.startApplication()

    def startApplication(self, qualityDisplayFX, imageDisplayFX, poseDisplayFX):
        '''
        Start the UI, and communicate continuous with the GUI while loop is running in separate threads.
        '''
        self.PE.initialize(qualityDisplayFX=qualityDisplayFX, imageDisplayFX=imageDisplayFX, poseDisplayFX=poseDisplayFX)

    def setBoardIndex(self, bi):
        """
        Tells PoseEstimator which board to track.
        :return: None
        """
        self.PE.trackedBoardIndex = bi

    def startPoseEstimation(self, imageDisplayFX, poseDisplayFX, qualityDisplayFX):
        """
        Starts the pose estimator.
        :return: None
        """
        self.PE.initialize(imageDisplayFX=imageDisplayFX, poseDisplayFX=poseDisplayFX, qualityDisplayFX=qualityDisplayFX)

    def stopPoseEstimation(self):
        """
        Stops the pose estimator.
        :return: None
        """
        logging.debug("Stopping pose estimator")
        self.PE.stopPoseEstimation()

    def initConnectedCams(self):
        '''
        Initialise cams connected to PC.
        Send the camlist and create a VisionEntities. for each camera.
        :param includeDefaultCam: If True, include the inbuilt webcam.
        :return: List of cams connected
        '''
        camlist = self.PE.createVisionEntities()
        return camlist

    def getVEFromCamIndex(self, index):
        return self.PE.getVE(index)

    def logging_setup(self,path='config\logging.json'):
        path = 'config\logging_config'
        with open(path) as f:
            config = json.load(f)
        logging.config.dictConfig(config)

    def getConnectedCams(self):
        camlist = []
        for VE in self.PE.VisionEntityList.items():
            i = VE.getCam().getSrc()
            camlist.append(i)
        return camlist

    # Set class variables:
    def setCameraIndex(self, ci):
        if ci == -1:
            logging.debug("Activated auto tracking")
            self.PE.setAutoTracker(True)
        else:
            logging.debug("Switching to camera " + str(ci))
            self.PE.routeDisplayFunction(ci)
            self.PE.setAutoTracker(False)

    def addBoard(self, board):
        """
        Adds a board to the Pose Estimator
        :param board: board to track
        :return:
        """
        self.PE.addBoard(board)

    def resetExtrinsic(self,):
        """
        Resets the extrinsic matrices of all cameras.
        :return: None
        """
        self.PE.resetExtrinsicMatrices()

    def addVisionEntities(self, VElist):
        """
        Adds vision entities to the pose estimator.
        :param VElist: Vision entities to create
        :return: None
        """
        self.PE.setVisionEntityList(VElist)


    def removeVEFromPEListByIndex(self, camID):
        """
        Remove from running PE.
        :param camID: ID of cam.
        :return:
        """
        self.PE.removeVEFromListByIndex(camID)

    def startMerge(self, main_board_index, sub_boards_index, qualityDisplayFX, imageDisplayFX):
        """
        Starts merging of boards
        :param main_board: main board to merge
        :param sub_boards: sub boards to merge
        :param displayFx: the function used to display board quality in UI
        :return:
        """
        self.PE.startMerge(main_board_index, sub_boards_index, qualityDisplayFX, imageDisplayFX)

    def finishMerge(self):
        """
        Finishes merging of boards
        :return: None
        """
        self.PE.finishMerge()

    def getMergerBoards(self):
        """
        Returns the boards from the merger
        :return: A dictionary containing all the merger boards.
        """
        print("connecter requested to return merger boards")
        print(self.PE.getMergerBoards())
        return self.PE.getMergerBoards()

    def setPoseDisplayFunction(self, poseDisplayFX):
        """
        Passes a function that displays pose to the pose estimator.
        :param poseDisplayFX: Function that displays pose
        :return: None
        """
        self.PE.setPoseDisplayFunction(poseDisplayFX)

    def setImageDisplayFunction(self, imageDisplayFX):
        """
        Passes a function that displays an image from a vision entity to the GUI
        :param imageDisplayFX: Function that displays image
        :return: None
        """
        self.PE.setImageDisplayFunction(imageDisplayFX)

    def startGraphing(self, displayGraphFX):
        """
        Starts graphing
        :param displayGraphFX: Function to use to display the graph data.
        :param updateGraphFX: Function to use to update the graph data.
        :param loggedBoards: List over the ids of the boards that should be logged and graphed.
        :return: None
        """
        self.PE.startGraphing(displayGraphFX)

    def startLogging(self, updateLogFX, loggedBoards):
        """
        Starts logging the position of the selected boards.
        :param updateLogFX: Function used to log data.
        :param loggedBoards: Identifiers of boards to log.
        :return: None
        """
        self.PE.startLogging(updateLogFX, loggedBoards)

    def stopLogging(self):
        """
        Stops the logging of positions for all boards.
        :return: None
        """
        self.PE.stopLogging()

if __name__ == '__main__':
    # logging_setup()
    l = logging.getLogger()
    l.info('Hello')