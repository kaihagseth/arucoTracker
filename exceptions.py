# Collection of user defined exceptions

class FailedCalibrationException(Exception):
    def __init__(self, msg):
        self.msg = msg
    '''Raised when calibration algorithm is unable to find a decent result.'''

class MissingExtrinsicException(Exception):
    def __init__(self, msg):
        self.msg = msg
    '''Raised when calibration algorithm is unable to find a decent result.'''

class CamNotOpenedException(Exception):
    def __init__(self, msg):
        self.msg = msg
    '''Raised when creating cam object with unsuccesfull creation of VidCap-object. Meaning no cameras found to 
    corresponding OpenCV-index.'''
