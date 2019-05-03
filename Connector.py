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

class Connector(Thread):
    '''
    Connect the UI with rest of the application.
    Start the GUI.
    '''

    def __init__(self):#ui_string):
        Thread.__init__(self)
        self.logging_setup()
        self.GUIupdaterFunction = None
        self.GUIstreamFunction = None
        self.PE = PoseEstimator()
        self._newBoard = None
        self._resetExtrinsic = None
        self._stopCommand = None
        self._collectGUIVEs = None

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
        self.PE.stopThreads()

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
        return self.PE.getVEById(index)

    def logging_setup(self,path='config\logging.json'):
        path = 'config\logging_config'
        with open(path) as f:
            config = json.load(f)
        logging.config.dictConfig(config)

    def getConnectedCams(self):
        camlist = []
        for VE in self.PE.VisionEntityList:
            i = VE.getCam().getSrc()
            camlist.append(i)
        return camlist

    # Set class variables:
    def setCameraIndex(self, ci):
        if ci == -1:
            self.PE.setAutoTracker(True)
        else:
            self.PE.routeDisplayFunction(ci)
            self.PE.setAutoTracker(False)

    def addBoard(self, board):
        self.PE.addBoard(board)

    def setResetExtrinsic(self, reset):
        self._resetExtrinsic = reset
        self.PE.resetExtrinsicMatrices()


    def setStopCommand(self, sc):
        self._stopCommand = sc

    def setCollectGUIVEs(self, var):
        self._collectGUIVEs = var

    def collectGUIVEs(self, VElist):
        self.PE.setVisionEntityList(VElist)
        self.setCollectGUIVEs(True) # Ready to be included

    def setGUIupdaterFunction(self, updaterFX):
        logging.info("GUIupdaterFx is set!")
        self.GUIupdaterFunction = updaterFX

    def setGUIStreamerFunction(self, streamerFX):
        self.GUIstreamFunction = streamerFX

    def doFindPoseStreamer(self):
        """" This is NOT a connector function. It's just a connector variable that keeps a reference
        to GUIApplication function! This variable is given a function in 'setGUIStreamerFunction' """
        self.GUIstreamFunction()

    def updateFields(self, poses, frame, boardPose_quality):
        """
        Ask GUI to update fieldsa in GUI class. 
        :param poses: 
        :param frame: 
        :param boardPose_quality: 
        :return: 
        """"""
        This is NOT a connector function. It's just a connector variable that keeps a reference 
        to GUIApplication function!  This variable is given a function in 'setGUIupdaterFunction'"""
        #logging.debug("Running updateFields in Connector")
        self.GUIupdaterFunction(poses, frame, boardPose_quality)

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

if __name__ == '__main__':
    # logging_setup()
    l = logging.getLogger()
    l.info('Hello')