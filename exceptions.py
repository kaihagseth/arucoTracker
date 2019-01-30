# Collection of user defined exceptions


class MissingImagePointException(Exception):
    ''' Raised when image point is missing (x or y value set to -1)'''
    pass

class FailedCalibrationException(Exception):
    def __init__(self, msg):
        self.msg = msg
    '''Raised when calibration algorithm is unable to find a decent result.'''