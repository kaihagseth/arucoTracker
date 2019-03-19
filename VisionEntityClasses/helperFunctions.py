import cv2
import numpy as np
import math

def toMatrix(rvec):
    """
    Transform rvec to matrix
    :param rvec: Rotation Vector
    :return:
    """
    matrix = np.matrix(cv2.Rodrigues(rvec)[0])
    return matrix

def rotationMatrixToEulerAngles(R):
   """
   https://www.learnopencv.com/rotation-matrix-to-euler-angles/
   :param R: Rotation matrix
   :return: Euler angles
   """
   R = R[0:3, 0:3]
   sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
   singular = sy < 1e-6
   if not singular:
       x = math.atan2(R[2, 1], R[2, 2])
       y = math.atan2(-R[2, 0], sy)
       z = math.atan2(R[1, 0], R[0, 0])
   else:
       x = math.atan2(-R[1, 2], R[1, 1])
       y = math.atan2(-R[2, 0], sy)
       z = 0
   return np.array([x, y, z])

def rvecTvecToTransMatrix(rvec, tvec):
    """
    Creates a homogenous transformation matrix
    :param rvec: Rodrigues rotation vector
    :param tvec: Translation vector
    :return: Transformation-matrix
    """
    R = np.matrix(cv2.Rodrigues(rvec)[0], dtype=np.float32)
    T = np.matrix(tvec, dtype=np.float32)
    T = np.reshape(T, (1, 3))
    RT = np.eye((4, 4))
    RT[0:3, 0:3] = R
    RT[3, 0:3] = T
    return RT

def transMatrixToRvecTvec(RT):
    """
    Returns rvec and tvec from a homogenous transformation matrix
    :param RT: 4x4 Transformation Matrix
    :return: Rodrigues vectors
    """
    R = RT[0:3, 0:3]
    rvec = cv2.Rodrigues(R)[0]
    tvec = RT[3, 0:3]
    return rvec, tvec

def invertTransformationMatrix(RT):
    """
    Returns an inverse transformation matrix
    :param RT: Transformation matrix to be inverted
    :return: Inverted transformation matrix
    """
    R0 = RT[0:3, 0:3]  # Get rotation matrix
    R1 = R0.T  # Transpose rotation matrix to find inverse rotation
    T0 = RT[3, 0:3]  # Get translation vector
    T1 = -(R1 * T0)  # Find opposite direction of translation vector
    RT = np.matrix(np.eye(4, 4))
    RT[0:3, 0:3] = R1
    RT[3, 0:3] = T1 #Compose new matrix
    return RT
