
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
            tvec, evec = self.PE.collectPoses()
            try:
                assert (tvec is not None and len(tvec) == 3), "Tvec format error."
                assert (evec is not None and len(evec) == 3), "Evec format error."
                self.PE.writeCsvLog(tvec, evec)
            except AssertionError:
                logging.ERROR("Raw pose was returned in an invalid format.")
            # Display the pose(s).
            dispResFx((tvec, evec))
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

        camlist = self.cg.initConnectedCams(includeDefaultCam)
        return camlist

    def initSCPEs(self, camlist):
        self.PE.initSCPEs(camlist)
        self.PE.createVisionEntities()

    def getImgFromSingleCam(self, camId):
        return self.PE.getCamById(camId).getSingleImg()

    def getVEFromCamIndex(self, index):
        return self.PE.getVEById(index)

    def logging_setup(self,path='config\logging.json'):
        path = 'config\logging_config'
        # l = logging.getLogger()
        # l.debug('HELLO DEBUG')
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