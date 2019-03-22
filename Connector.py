import os
import json
import logging
from logging.config import dictConfig
import time
from PoseEstimator import PoseEstimator
import threading
from GUILogin import GUILogin

class Connector():
    '''
    Connect the UI with rest of the application.
    Start the GUI.
    hello
    '''

    def __init__(self):
        self.logging_setup()
        self.PE = PoseEstimator()


    def startApplication(self, dispResFx, stopAppFx):
        '''
        Start the application, and communicate continius with the GUI while loop is running in seperate threads.
        #TODO: Would it be better to return pose and pass stop message in function call?
        :param dispResFx: Function to display result with
        :param doAbortFx: Function to abort the application
        '''
        self.PE.runPoseEstimator() # Create all threads and start them
        logging.info('Running startApplication()')
        stopApp = False
        doAbort = False
        msg = 'Thread: ', threading.current_thread().name
        logging.info(msg)
        while not doAbort:
            if not stopApp:
                # Get the pose(s) from all cams.
                self.PE.updateBoardPoses()
                poses = self.PE.getEulerPoses()
                for pose in poses:
                    tvec, evec = pose # TODO: Get more poses
                try:
                    self.PE.writeCsvLog(tvec, evec)
                except (AttributeError, TypeError):
                    raise AssertionError("Raw pose was returned in an invalid format.")
                # Display the pose(s).
                dispResFx()
                # Check if we want to abort, function from GUI.
                stopApp = stopAppFx()
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

    def getPose(self):
        return self.PE.getEulerPoses()

    def getOutputImage(self, camID=-1):
        """
        Return image with overlay from pose estimator. Select cam with camID, or set camID to -1 for automatic switching
        between cameras.
        :param camID:
        :return:
        """
        return self.PE.getPosePreviewImg(camID)


if __name__ == '__main__':
    # logging_setup()
    l = logging.getLogger()
    l.info('Hello')