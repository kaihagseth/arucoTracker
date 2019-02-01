import numpy as np
import math
import exceptions as exc
import Camera


'''
Class for doing all analysis and filtering on a single-OTcam image stream.
Thus, all analysis involving images from more than one camera, is not done here.
'''

class SingleCameraPoseEstimator():

    # Camera to reference frame transform matrix
    ref = None
    # bounds for image analysis
    lower_bounds = None
    upper_bounds = None

    def __init__(self, otcam, modelParam=None):
        '''
        :param otcam: The camera taking images.
        :param modelParam: The location of on-model bullets, given in homogenus model coordinates. Given as a 4x3 matrix. If not
        specified, default parameters is used. Default: [[1,0,0,0],[0,1,0,0],[0,0,1,0], [1,1,1,1]]
        '''
        self.OTCam = otcam
        self.intrCamMtrx = self.OTCam._intri_cam_mtrx
        if modelParam is None:
            self.modelParam = np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 1, 1]])
        else:
            self.modelParam = modelParam

    def estimateModelPose(self, imagePoints, x0=None):
        '''
        Estimate the model pose from a single image.
        :param imagePoints: Image coordinates of the point location, given in number of pixels. Order is not essential. Given as 4x2 matrix. If
        point is not found, its x's and y's are set to -1. Image origo is top left, +y is downwards.
        :param x0: Initial guess of object pose
        :return: pose of the object with respect to the camera 6x1 matrix object [ax; ay; az; tx; ty; tz]
        and the object to camera transformation matrix 4x4
        '''

        if x0 is None:
            x0 = np.matrix([0,0,0,0,0,0]).T

        # checking if all image points are present in input
        for i in range(4):
            for j in range(2):
                if imagePoints[i,j] == -1:
                    raise exc.MissingImagePointException('One or more image points not found, cannot estimate pose')

        # Points in image (y0)
        y0 = imagePoints.T

        # points in model coordinate system
        pm = self.modelParam

        # Setting pose to guess pose
        x = x0


        def fProject(x, pm, K):
            '''
            Project 3D points pm  in model coordinates to image points p
            :param x: Model to camera pose parameters
            :param pm: Model points in homogenus 3D coordinates 4xN matrix represented in model coordinates
            :param K: Intrinsic camera matrix
            :return: Projected image coordinates in nx1 matrix object and transformation matrix of model
            pose relative to camera
            '''

            # Model Pose relative to camera
            ax, ay, az, tx, ty, tz = x[0], x[1], x[2], x[3], x[4], x[5]
            tM = np.vstack((tx, ty))
            tM = np.vstack((tM, tz))

            # Rotation Matrix R from model pose
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

            # Homogenus transformation matrix
            tMtx = np.vstack(mExt, np.matrix([[0, 0, 0, 1]]))
            return p, tMtx

        for i in range(0, 10):

            # Predicted image points
            y, _ = fProject(x, pm, self.intrCamMtrx)

            # Jakobian
            e = 0.000001
            j = np.matrix(np.empty((8, 6)))
            j[:, 0] = np.divide((fProject(x + np.matrix([[e], [0], [0], [0], [0], [0]]), pm, self.intrCamMtrx)[0] - y), e)
            j[:, 1] = np.divide((fProject(x + np.matrix([[0], [e], [0], [0], [0], [0]]), pm, self.intrCamMtrx)[0] - y), e)
            j[:, 2] = np.divide((fProject(x + np.matrix([[0], [0], [e], [0], [0], [0]]), pm, self.intrCamMtrx)[0] - y), e)
            j[:, 3] = np.divide((fProject(x + np.matrix([[0], [0], [0], [e], [0], [0]]), pm, self.intrCamMtrx)[0] - y), e)
            j[:, 4] = np.divide((fProject(x + np.matrix([[0], [0], [0], [0], [e], [0]]), pm, self.intrCamMtrx)[0] - y), e)
            j[:, 5] = np.divide((fProject(x + np.matrix([[0], [0], [0], [0], [0], [e]]), pm, self.intrCamMtrx)[0] - y), e)

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

        # getting  translation matrixand pose
        _, transformMatrix = fProject(x, pm, self.intrCamMtrx)
        pose = x

        return pose, transformMatrix

    def inverseTransform(self, transformMatrix):
        '''
        TODO: Skrive forklaring fra Introduction to Robotics av John J. Craig s36
        :param transformMatrix: Transformation matrix for system B represented in system A
        :return: Transformation matrix for system A represented in system B
        '''

        Rab = transformMatrix[0:3, 0:3].T
        Pbaorg = -Rab*transformMatrix[0:3, 3]
        Tab = np.vstack(np.hstack(Rab, Pbaorg), [[0, 0, 0, 1]])

        return Tab


    def compoundTransformations(self, transformMatrixA, transformMatrixB):
        '''
        TODO: Skrive forklaring fra Introduction to Robotics av John J. Craig s35
        :param transformMatrixA: Transformation matrix for system B represented in system A
        :param transformMatrixB: Transformation matrix for system C represented in system B
        :return: The compounded transformation matrix for system C represented in system A
        '''

        Tca = transformMatrixA*transformMatrixB

        return Tca

    def tansformMatrixToPose(self, transformMatrix):
        '''
        TODO: Skrive forklaring
        :param transformMatrix:
        :return: Pose [ax; ay; az; tx; ty; tz]
        '''

        T = transformMatrix

        ay = np.arctan2(-T[2, 0], np.sqrt(np.square(T[0, 0])+np.square(T[1, 2])))
        az = np.arctan2(T[1, 0]/np.cos(ay), T[0, 0]/np.cos(ay))
        ax = np.arctan2(T[2, 1] / np.cos(ay), T[2, 2] / np.cos(ay))

        pose = np.matrix([ax, ay, az, T[0, 3], T[1, 3], T[2, 3]]).T

        return pose

    def setReference(self):
        '''
        Set reference to the current model pose
        '''

        A = self.OTCam.findBallPoints(self.OTCam.getSingleFrame, self.lower_bounds, self.upper_bounds)
        imgPts = np.matrix(A[:, 0:2])
        _, tMtx = self.estimateModelPose(imgPts)
        self.ref = self.inverseTransform(tMtx)

    def GetPose(self):
        '''

        :return: Pose relative to reference
        '''

        # Getting model pose relative to camera
        A = self.OTCam.findBallPoints(self.OTCam.getSingleFrame, self.lower_bounds, self.upper_bounds)
        imgPts = np.matrix(A[:, 0:2])
        _, tMtx = self.estimateModelPose(imgPts)
        # Getting model pose relative to reference
        pose = self.tansformMatrixToPose(tMtx*self.ref)

        return pose


