import numpy as np
import cv2
import math



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


    def estimateModelPos(self, imagePoints, intrCamMtrx, modelParam=None, x0=None):
        '''
        Estimate the model pose from a single image.
        :param imagePoints: Image coordinates of the point location, given in number of pixels. Order is not essential. Given as 4x2 matrix. If
        point is not found, it's x's and y's are set to -1. Image origo is top left, +y is downwards.
        :param intrCamMtrx: The intrinsic camera matrix. Given as: [[fx, 0, cx],[0, fy, cy],[0,0,1]]
        :param modelParam: The location of on-model bullets, given in homogenus model coordinates. Given as a 4x3 matrix. If not
        specified, default parameters is used. Default: [[1,0,0,0],[0,1,0,0],[0,0,1,0], [1,1,1,1]]
        :param x: Initial guess of object pose
        :return: pose of the object with respect to the camera 6x1 matrix object.
        '''
        if modelParam is None:
            modelParam = np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 1, 1]])

        if x0 is None:
            x0 = np.matrix([0,0,0,0,0,0]).T

        # Points in image (y0)
        y0 = imagePoints.T

        # points in model coordinate system
        pm = modelParam

        # Setting pose to guess pose
        x = x0


        def fProject(x, pm, K):
            '''
            Project 3D points pm  in model coordinates to image points p
            :param x: Model to camera pose parameters
            :param pm: Points in homogenus 3D coordinates 4xN matrix
            :param K: Intrinsic camera matrix
            :return: Projected image coordinates in nx1 matrix object
            '''

            # Model Pose
            ax, ay, az, tx, ty, tz = x[0], x[1], x[2], x[3], x[4], x[5]
            tM = np.vstack((tx, ty))
            tM = np.vstack((tM, tz))

            # Rotation Matrix R
            Rx = np.matrix([[1, 0, 0], [0, math.cos(ax), -math.sin(ax)], [0, math.sin(ax), math.cos(ax)]])
            Ry = np.matrix([[math.cos(ay), 0, math.sin(ay)], [0, 1, 1], [-math.sin(ay), 0, math.cos(ay)]])
            Rz = np.matrix([[math.cos(az), -math.sin(az), 0], [math.sin(az), math.cos(az), 0], [0, 0, 1]])
            Rzy = np.matmul(Rz, Ry)
            R = np.matmul(Rzy, Rx)

            # Extrinsic camera matrix
            mExt = np.hstack((R, tM))

            # Points to project
            ph = np.matmul(K, mExt)
            ph = np.matmul(ph, pm)

            # Divide Through 3rd elements
            ph[0, :] = np.divide(ph[0, :], ph[2, :])
            ph[1, :] = np.divide(ph[1, :], ph[2, :])
            ph = ph[0:2, :]

            p = np.matrix.reshape(ph, (-1, 1), order='F')

            return p

        for i in range(0, 10):

            # Predicted image points
            y = fProject(x, pm, intrCamMtrx)


            # Jakobian
            e = 0.000001
            j = np.asmatrix(np.empty((8, 6)))
            j[:, 0] = np.divide((fProject(x + np.matrix([[e], [0], [0], [0], [0], [0]]), pm, intrCamMtrx) - y), e)
            j[:, 1] = np.divide((fProject(x + np.matrix([[0], [e], [0], [0], [0], [0]]), pm, intrCamMtrx) - y), e)
            j[:, 2] = np.divide((fProject(x + np.matrix([[0], [0], [e], [0], [0], [0]]), pm, intrCamMtrx) - y), e)
            j[:, 3] = np.divide((fProject(x + np.matrix([[0], [0], [0], [e], [0], [0]]), pm, intrCamMtrx) - y), e)
            j[:, 4] = np.divide((fProject(x + np.matrix([[0], [0], [0], [0], [e], [0]]), pm, intrCamMtrx) - y), e)
            j[:, 5] = np.divide((fProject(x + np.matrix([[0], [0], [0], [0], [0], [e]]), pm, intrCamMtrx) - y), e)

            # reshaping to match y so we can find dY
            y0 = np.reshape(y0, (8, 1), order='c')
            dy = y0 - y

            # dX from pseudo inverse of jakobian
            dx = np.matmul(np.linalg.pinv(j), dy)

            # stop if no changes in parameter
            if abs(np.divide(np.linalg.norm(dx), np.linalg.norm(x))) < 0.000001:
                break

            # updating pose estimate
            x = x + dx

        return x




