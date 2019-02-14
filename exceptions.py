# Collection of user defined exceptions


class MissingImagePointException(Exception):
    ''' Raised when image point is missing (x or y value set to -1) when you try to estimate pose'''
    def __init__(self, msg):
        self.msg = msg


class FailedCalibrationException(Exception):
    def __init__(self, msg):
        self.msg = msg
    '''Raised when calibration algorithm is unable to find a decent result.'''


class MissingIntrinsicCameraParametersException(Exception):
    ''' Raised when camera is not calibrated and you try to estimate pose'''
    def __init__(self, msg):
        self.msg = msg


class MissingReferenceFrameException(Exception):
    ''' Raised when your try reference frame for pose is not set'''
    def __init__(self, msg):
        self.msg = msg