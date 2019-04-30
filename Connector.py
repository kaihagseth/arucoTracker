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
        self._cameraIndex = 0
        self._boardIndex = None
        self._auto = None
        self._newBoard = None
        self._resetExtrinsic = None
        self._startCommand = None
        self._stopCommand = None
        self._collectGUIVEs = None#self.UI.readUserInputs()
        #if ui_string == "GUI":
            #self.UI = GUIApplication()
            #guil = GUILogin(mainGUI=self.UI)
            #guil.startLogin()
    def run(self):
        self.startApplication()

    def startApplication(self):
        '''
        Start the UI, and communicate continuous with the GUI while loop is running in separate threads.
        '''
        logging.info("Running StartApplication loop.")
        doAbort = False
        runApp = True
        VEsInitInGUI = True
        time.sleep(5)
        counter = 0
        # TODO: Find an automated way to wait for UI to initialize
        while not doAbort:
            counter += 1
            logging.debug("Running startApplication loop " + str(counter)+" times. ")
            if self._startCommand:
                logging.debug("startCommand received")
                if not VEsInitInGUI: # Not collected VEs from GUI, so use hardcoded method. Todo: Use flag instead
                    self.PE.createVisionEntities()

                else:
                    # Do nothing. VEs already initialised
                    pass
                self.PE.runPoseEstimator()  # Create all threads and start them
                #camlist = self.PE.getVisionEntityIndexes()
                #self.UI.updateCamlist(camlist)
                runApp = True
                self._startCommand = False
            if self._collectGUIVEs:
                VEsInitInGUI = True
            if self._stopCommand:
                logging.debug("stop command received")
                runApp = False
                doAbort = True
                self.PE.stopThreads()
            if self._newBoard:
                self.PE.addBoard(self._newBoard)
            if self._resetExtrinsic:
                # Reset the extrinsic matrix, meaning set new startposition for calculations.
                pass
            if runApp:
                logging.info("Running runApp")
                self.PE.updateBoardPoses()
                poses = self.PE.getEulerPoses()
                logging.debug("Poses: " + str(poses))
                frame = self.PE.getPosePreviewImg(self._cameraIndex, self._boardIndex, self._auto)
                boardPose_quality = self.PE.getBoardPositionQuality()
                # Get the pose(s) from all cams.
                self.PE.writeCsvLog(poses)
                # Check if we want to abort, function from GUI.
                self.updateFields(poses, frame, boardPose_quality)  # Write relevant information to UI-thread.
                self.doFindPoseStreamer()
            else:
                time.sleep(0.1)

        print('Ended')

    def initConnectedCams(self):
        '''
        Initialise cams connected to PC.
        Send the camlist and create a VisionEntities. for each camera.
        :param includeDefaultCam: If True, include the inbuilt webcam.
        :return: List of cams connected
        '''

        camlist = self.PE.createVisionEntities()
        return camlist

    def getImgFromSingleCam(self, camId):
        """
        Get raw image, if poseEstimation is not running.
        :param camId: Index number of camrea
        :return: Frame from cam on given ID. None if VE ThreadLoop is running.
        """
        return self.PE.getRawPreviewImage(camId)

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
        self._cameraIndex = ci
    def setBoardIndex(self, bi):
        self._boardIndex = bi
    def setAuto(self, auto):
        self._auto = auto
    def setNewBoard(self, nb):
        self._newBoard = nb
    def setResetExtrinsic(self, reset):
        self._resetExtrinsic = reset
        self.PE.resetExtrinsicMatrices()
    def setStartCommand(self, sc):
        self._startCommand = sc
    def setStopCommand(self, sc):
        self._stopCommand = sc
    def setCollectGUIVEs(self, var):
        self._collectGUIVEs = var
    def collectGUIVEs(self, VElist):
        self.PE.setVisionEntityList(VElist)
        self.setCollectGUIVEs(True) # Ready to be included

    def setGUIupdaterFunction(self, updaterFX):
        logging.info("GUIupdaterFx IS SET!")
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
        logging.debug("Running updateFields in Connector")
        self.GUIupdaterFunction(poses, frame, boardPose_quality)

    def removeVEFromPEListByIndex(self, camID):
        """
        Remove from running PE.
        :param camID: ID of cam.
        :return:
        """
        self.PE.removeVEFromListByIndex(camID)
if __name__ == '__main__':
    # logging_setup()
    l = logging.getLogger()
    l.info('Hello')