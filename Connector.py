import os
import json
import logging
from logging.config import dictConfig
import time
from PoseEstimator import PoseEstimator
import threading
from GUI import GUIApplication

class Connector():
    '''
    Connect the UI with rest of the application.
    Start the GUI.
    # TODO: Refactor connector and GUI classes.
    #
    hello
    '''

    def __init__(self):
        self.logging_setup()
        self.PE = PoseEstimator()
        self.UI = GUIApplication()


    def startApplication(self):
        '''
        Start the UI, and communicate continuous with the GUI while loop is running in separate threads.
        '''
        self.PE.runPoseEstimator()  # Create all threads and start them
        while not doAbort:
            userInputs = self.UI.readUserInputs()
            run_pose
            if not stopApp:
                self.PE.updateBoardPoses()
                self.PE.getPosePreviewImg(userInputs['camId'])
                poses = self.PE.getEulerPoses()
                frame = self.PE.getOutputFrame()
                # Get the pose(s) from all cams.
                self.PE.writeCsvLog(poses)
                # Check if we want to abort, function from GUI.
                stopApp = userInputs['stopApp']
                self.UI.updateFields(poses, frame)  # Write relevant information to UI-thread.
            else:
                time.sleep(0.1)
        self.PE.stopThreads()
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


if __name__ == '__main__':
    # logging_setup()
    l = logging.getLogger()
    l.info('Hello')