
import os
import json
import logging
from logging.config import dictConfig
from PoseEstimator import PoseEstimator

class Connector():
    '''
    Connect the UI with rest of the application.
    hello
    '''

    def __init__(self):
        #self.cg = CameraGroup()
        self.logging_setup()
        self.PE = PoseEstimator()

    def startApplication(self, dispResFx, doAbortFx):
        '''
        Start the application, and communicate continius with the GUI while loop is running in seperate threads.
        :param dispResFx: Function to display result with
        :param doAbortFx: Function to abort the application
        '''
        self.PE.runPoseEstimator() # Create all threads and start them
        logging.info('Running startApplication()')
        doAbort = doAbortFx()
        while not doAbort:
            # Get the pose(s) from all cams.
            rawpose = self.PE.collectPoses()
            tvec = rawpose[0:3]
            evec = rawpose[3:6]
            self.PE.writeCsvLog(tvec, evec)
            # Display the pose(s).
            dispResFx(rawpose)
            # Check if we want to abort, function from GUI.
            doAbort = doAbortFx()
         #   logging.info("Running startApplication in Connector")
        print('Ended')


    def initConnectedCams(self, includeDefaultCam):
        '''
        Initialise cams connected to PC.
        Send the camlist and create a SCPE for each camera.
        :param includeDefaultCam: If True, include the inbuilt webcam.
        :return: None
        '''
        self.PE.createVisionEntities()

    def getImgFromSingleCam(self, camId):
        return self.PE.getCamById(camId).getSingleImg()

    def getVEFromCamIndex(self, index):
        return self.PE.getVEById(index)

    def logging_setup(self,path='config\logging.json'):
        path = 'config\logging_config'
        #l = logging.getLogger()
        #l.debug('HELLO DEBUG')
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
    #logging_setup()
    l = logging.getLogger()
    l.info('Hello')