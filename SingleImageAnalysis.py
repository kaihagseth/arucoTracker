import numpy as np




'''
Class for doing all analysis and filtering on a single-OTcam image.
Thus, all analysis involving images from more than one camera, is not done here.
'''

class SingleImageAnalysis():
    def __init__(self, otcamParent):
        '''
        :param otcamParent: The camera taking images.
        '''
        self.OTCam = otcamParent


    def estimateModelPos(self, imagePoints, distKoeff, modellParam, intrCamMtrx=None):
        '''
        Estimate the model pose from a single image.
        :param imagePoints: Image coordinates of the point location, given in number of pixels. Order is not essential. Given as 4x2 matrix. If
        point is not found, it's x's and y's are set to -1. Image origo is top left, +y is downwards.
        :param distKoeff: Distortion coefficients of the lense. Given as [coeff_x, coeff_y]
        :param intrCamMtrx: The intrinsic camera matrix. Given as: [[fx, 0, cx],[0, fy, cy],[0,0,1]]
        :param modellParam: The location of on-model bullets, given in model coordinates. Given as a 4x3 matrix. If not
        specified, default parameters is used. Default: [[1,0,0],[0,1,0],[0,0,1], [0,0,0]]
        :return: Extrinsic matrix describing pose and position of camera. Given as 3x4 matrix.
        '''
        if intrCamMtrx is None:
            intrCamMtrx = np.matrix([[1,0,0],[0,1,0],[0,0,1], [0,0,0]])

    def findBallPoints(self):
        pass
