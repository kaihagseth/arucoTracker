from CameraGroup import CameraGroup
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
        self.cg = CameraGroup()
        self.logging_setup()
        self.PE = PoseEstimator()
    def startApplication(self, dispResFx, doAbortFx):
        self.PE.getPoseFromCams()
        logging.info('Running startApplication()')
        doAbort = doAbortFx()
        while not doAbort:
            print('Running dispResFx')
            res = self.PE.collectPoses()
            dispResFx(res)
            doAbort = doAbortFx()
        print('Ended')

    def addCamera(self, cam):
        self.cg.addSingleCam(cam)

    def getConnectedCams(self):
        return self.cg.findConnectedCams()

    def initConnectedCams(self, includeDefaultCam):
        '''
        Initialise cams connected to PC.
        Send the camlist and create a SCPE for each camera.
        :param includeDefaultCam: If True, include the inbuilt webcam.
        :return: None
        '''
        camlist = self.cg.initConnectedCams(includeDefaultCam)
        return camlist
    def initSCPEs(self, camlist):
        self.PE.initSCPEs(camlist)

    def getImgFromSingleCam(self, camId):
        return self.cg.getSingleImg(camId)

    def getCamFromIndex(self, index):
        return self.cg.getCamByID(index)

    def logging_setup(self,path='config\logging.json'):
        path = 'config\logging_config'
        #l = logging.getLogger()
        #l.debug('HELLO DEBUG')
        with open(path) as f:
            config = json.load(f)
        logging.config.dictConfig(config)


if __name__ == '__main__':
    #logging_setup()
    l = logging.getLogger()
    l.info('Hello')