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

def invertTransformationMatrix(RT):
    """
    Returns an inverse transformation matrix
    :param RT: Transformation matrix to be inverted
    :return: Inverted transformation matrix
    """
    R0 = RT[0:3, 0:3]  # Get rotation matrix
    R1 = R0.T  # Transpose rotation matrix to find inverse rotation
    T0 = RT[0:3, 3]  # Get translation vector
    T1 = -(R1 * T0)  # Find opposite direction of translation vector
    RT = np.matrix(np.eye(4, 4))
    RT[0:3, 0:3] = R1
    RT[0:3, 3] = T1 #Compose new matrix
    return RT