import numpy as np
import cv2





class StereoVision:
    '''
    Class for using 2D imagepoints from multiple cameras to triangulate 3D position and orientation
    '''


    def _get3DPoints(self, intrinsic1, intrinsic2, extrinsic1, extrinsic2, imagePoints1, imagePoints2,
                    distortion1=None, distortion2=None, imageSize=None):
        '''
        TODO: ???
        :param intrinsic1: Intrinsic matrix of camera 1
        :param intrinsic2: Intrinsic matrix of camera 2
        :param extrinsic1: World origin relative to camera 1
        :param extrinsic2: World origin relative to camera 2
        :param distortion1: Distortion coefficients of camera 1
        :param distortion2: Distortion coefficients of camera 1
        :param imageSize: Size of image
        :param imagePoints1:
        :param imagePoints2:
        :return:
        '''

        # Getting the transformation matrix of camera 2 w.r.t camera 1
        transform = np.matrix(extrinsic1)*np.linalg.pinv(np.matrix(extrinsic2))
        R = transform[0:3, 0:3]
        T = transform[0:3, 3]

        # Get the rectified projection matrices of both cameras and the rectified image points
        #_, _, P1, P2 = cv2.stereoRectify(cameraMatrix1=intrinsic1, cameraMatrix2=intrinsic2, distCoeffs1=distortion1,
        #                                 distCoeffs2=distortion2, R=R, T=T, imageSize=imageSize, flags=0)

        # get the projection matrices (intrinsic*extrinsic)
        P1 = np.matrix(intrinsic1)*np.matrix(extrinsic1)
        P2 = np.matrix(intrinsic2)*np.matrix(extrinsic2)

        # get the homogeneous 3D coordinates by triangulation
        coord = cv2.triangulatePoints(projMatr1=P1, projMatr2=P2, projPoints1=imagePoints1, projPoints2=imagePoints2)

        return coord

    def getPose(self, intrinsic1, intrinsic2, extrinsic1, extrinsic2, imagePoints1, imagePoints2,
                distortion1=None, distortion2=None, imageSize=None):
        '''
        Get the 6 DOF pose of the object
        :param self:
        :param intrinsic1:
        :param intrinsic2:
        :param extrinsic1:
        :param extrinsic2:
        :param imagePoints1:
        :param imagePoints2:
        :param distortion1:
        :param distortion2:
        :param imageSize:
        :return:
        '''

        ''' 
        TODO: get the 3D points corresponding to the markers on front and back of model to create directional
        vector and use this to get the euler angles (ikke så lett som man skulle ha trodd viser det seg)    
        '''

