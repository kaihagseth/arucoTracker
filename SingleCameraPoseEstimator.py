import numpy as np
import exceptions as exc
import random, time, logging

'''
Class for doing all analysis and filtering on a single-OTcam image stream.
Thus, all analysis involving images from more than one camera, is not done here.

'''

class SingleCameraPoseEstimator():

    # Camera to reference frame transform matrix
    _ref = None

    def __init__(self, model_param=None):
        '''
        :param model_param: The location of on-model bullets, given in homogenus model coordinates. Given as a 4x3 matrix. If not
        specified, default parameters is used. Default: [[1,0,0,0],[0,1,0,0],[0,0,1,0], [1,1,1,1]]
        '''


        if model_param is None:
            self._model_param = np.matrix([[130, 0, 0], [0, 118, 0], [0, 0, 138], [1, 1, 1]], dtype=float)
        else:
            self._model_param = model_param


    def _estimateModelPose(self, intr_cam_matrix, image_points, x0=None):
        '''
        Estimate the model pose from a single image.
        :param intr_cam_matrix: the intrinsic camera matrix of the camera the image points is gathered from
        :param image_points: Image coordinates of the point location, given in number of pixels. Order is not essential. Given as 4x2 matrix. If
        point is not found, its x's and y's are set to -1. Image origo is top left, +y is downwards.
        :param x0: Initial guess of object pose. NB! y can not be set to 0 as this will cause divide by 0 exception.
        :return: pose of the object with respect to the camera 6x1 matrix object [ax; ay; az; tx; ty; tz]
        and the object to camera transformation matrix 4x4
        '''

        if x0 is None:
            x0 = np.matrix([0,0,0,0,0,1], dtype=float).T


        # checking if all image points are present in input
        print('Image_points: ', image_points)
        for i in range(3):
            for j in range(2):
                if image_points[i, j] == -1:
                    logging.error('One or more image points not found, cannot estimate pose')
                    raise exc.MissingImagePointException('One or more image points not found, cannot estimate pose')


        # Points in image (y0)
        y0 = image_points.T

        # points in model coordinate system
        pm = self._model_param

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
            # TODO: fikse dårlig slicing under
            ax, ay, az, tx, ty, tz = x[0], x[1], x[2], x[3], x[4], x[5]
            tM = np.vstack((tx, ty))
            tM = np.vstack((tM, tz))

            # Rotation Matrix R from model pose
            Rx = np.matrix([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]], dtype=float)
            Ry = np.matrix([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]], dtype=float)
            Rz = np.matrix([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]], dtype=float)
            #Rzy = np.matmul(Rz, Ry)
            #R = np.matmul(Rzy, Rx)
            R = Rz*Ry*Rx

            # Extrinsic camera matrix
            mExt = np.hstack((R, tM))

            # Points to project
            #ph = np.matmul(K, mExt)
            #ph = np.matmul(ph, pm)
            ph = K*mExt*pm

            # Divide Through 3rd elements
            ph[0, :] = np.divide(ph[0, :], ph[2, :])
            ph[1, :] = np.divide(ph[1, :], ph[2, :])
            ph = ph[0:2, :]

            p = np.matrix(np.reshape(ph, (-1, 1), order='F'), dtype=float)

            # Homogenus transformation matrix
            transform_matrix = np.vstack((mExt, np.matrix([[0, 0, 0, 1]], dtype=float)))
            return p, transform_matrix

        for i in range(0, 100):

            # Predicted image points
            y, _ = fProject(x, pm, intr_cam_matrix)

            # Jakobian
            e = 0.000001
            j = np.matrix(np.empty((6, 6)))
            j[:, 0] = np.divide((fProject(x + np.matrix([[e], [0], [0], [0], [0], [0]], dtype=float), pm, intr_cam_matrix)[0] - y), e)
            j[:, 1] = np.divide((fProject(x + np.matrix([[0], [e], [0], [0], [0], [0]], dtype=float), pm, intr_cam_matrix)[0] - y), e)
            j[:, 2] = np.divide((fProject(x + np.matrix([[0], [0], [e], [0], [0], [0]], dtype=float), pm, intr_cam_matrix)[0] - y), e)
            j[:, 3] = np.divide((fProject(x + np.matrix([[0], [0], [0], [e], [0], [0]], dtype=float), pm, intr_cam_matrix)[0] - y), e)
            j[:, 4] = np.divide((fProject(x + np.matrix([[0], [0], [0], [0], [e], [0]], dtype=float), pm, intr_cam_matrix)[0] - y), e)
            j[:, 5] = np.divide((fProject(x + np.matrix([[0], [0], [0], [0], [0], [e]], dtype=float), pm, intr_cam_matrix)[0] - y), e)

            # reshaping to match y so we can find dY
            y0 = np.reshape(y0, (-1, 1), order='c')
            dy = y0 - y

            # dX from pseudo inverse of jakobian
            #dx = np.matmul(np.linalg.pinv(j), dy)
            dx = np.linalg.pinv(j)*dy

            # stop if no changes in parameter
            if abs(np.divide(np.linalg.norm(dx), np.linalg.norm(x))) < 0.000001:
                break

            # updating pose estimate
            x = x + dx

        # getting  translation matrix and pose
        _, transformMatrix = fProject(x, pm, intr_cam_matrix)
        pose = x

        return pose, transformMatrix

    def _inverseTransform(self, transformMatrix):
        '''
        Find the inverse of the transformation matrix by transposing the rotation and subtracting
        the translation.
        :param transformMatrix: Transformation matrix for system B represented in system A
        :return: Transformation matrix for system A represented in system B
        '''
        Rab = transformMatrix[0:3, 0:3].T
        Pbaorg = -Rab*transformMatrix[0:3, 3]
        Tab = np.vstack((np.hstack((Rab, Pbaorg)), np.matrix([[0, 0, 0, 1]], dtype=float)))
        return Tab

    def _tansformMatrixToPose(self, transformMatrix):
        '''
        Calculate the 6DOF pose [ax; ay; az; tx; ty; tz] from 4x4 transformation matrix.
        cos(ay) can not be 0 (angle 90/180 deg) as this will cause divide by 0 exception
        :param transformMatrix:
        :return: Pose [ax; ay; az; tx; ty; tz]
        '''

        T = transformMatrix

        ay = np.arctan2(-T[2, 0], np.sqrt(np.square(T[0, 0])+np.square(T[1, 2])))
        az = np.arctan2(T[1, 0]/np.cos(ay), T[0, 0]/np.cos(ay))
        ax = np.arctan2(T[2, 1] / np.cos(ay), T[2, 2] / np.cos(ay))

        pose = np.matrix([ax, ay, az, T[0, 3], T[1, 3], T[2, 3]], dtype=float).T

        return pose

    def setReference(self, intr_cam_matrix, image_points):
        '''
        Set reference frame to the current model pose. Takes an image of the current model position
        and calculates the inverse of the model to camera transformation matrix.
        :param intr_cam_matrix: the intrinsic camera matrix of the camera the image points is gathered from
        :param image_points: Image coordinates of the point location, given in number of pixels. Order is not essential. Given as 4x2 matrix. If
        point is not found, its x's and y's are set to -1. Image origo is top left, +y is downwards.
        '''
        logging.info("Setting reference frame.")
        _, transform_matrix = self._estimateModelPose(intr_cam_matrix, image_points)
        self._ref = self._inverseTransform(transform_matrix)



    def setModelParams(self, model_params):
        '''
        Set model parameters
        :param model_params: New model parameters
        '''
        self._model_param = model_params

    def getPose(self, intr_cam_matrix, image_points, guess_pose=None):
        '''
        Get the pose of current model position relative to reference frame. NB! angles in radians
        :return: Pose relative to reference
        '''
        print('Intrinsic cam matrix: ', intr_cam_matrix)
        if self._ref is not None:
            try:
                if guess_pose is None:
                    _, transform_matrix = self._estimateModelPose(intr_cam_matrix, image_points)
                else:
                    _, transform_matrix = self._estimateModelPose(intr_cam_matrix, image_points, guess_pose)
                # Getting model pose relative to reference
                #pose = self._tansformMatrixToPose(transform_matrix * self._ref)
                pose = self._tansformMatrixToPose(self._ref*transform_matrix)
                return pose
            except exc.MissingIntrinsicCameraParametersException as intErr:
                print(intErr.msg)
            except exc.MissingImagePointException as imgErr:
                print(imgErr.msg)
        else:
            raise exc.MissingReferenceFrameException('Reference frame not set')


#if __name__ == '__main__':
    # Test functions:
    #img_point =