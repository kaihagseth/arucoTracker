# Collection of user defined exceptions

class FailedCalibrationException(Exception):
    def __init__(self, msg):
        self.msg = msg
    '''Raised when calibration algorithm is unable to find a decent result.'''
