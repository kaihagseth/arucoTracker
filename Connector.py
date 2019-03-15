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
                ret, poseFrame = self.PE.getPosePreviewImg()
                dispResFx(poseFrame)
                # Check if we want to abort, function from GUI.
                stopApp = stopAppFx()
                msg = 'StopApp: ', stopApp
                logging.debug(msg)
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
        OMG: Not threadsafe in VisionEntity!
        :param camId:
        :return:
        """
        return self.PE.getVEById(camId).getFrame()

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
        return self.PE.runPoseEstimator().singlecam_curr_pose_que.get()

if __name__ == '__main__':
    # logging_setup()
    l = logging.getLogger()
    l.info('Hello')