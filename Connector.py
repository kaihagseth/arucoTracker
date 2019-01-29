from CameraGroup import CameraGroup


class Connector():
    '''
    Connect the UI with rest of the application.
    '''

    def __init__(self):
        self.cg = CameraGroup()


    def addCamera(self, cam):
        self.cg.addSingleCam(cam)

    def getConnectedCams(self):
        return self.cg.findConnectedCams()

    def initConnectedCams(self, includeDefaultCam):
        self.cg.initConnectedCams(includeDefaultCam)

    def getImgFromSingleCam(self, camId):
        return self.cg.getSingleImg(camId)