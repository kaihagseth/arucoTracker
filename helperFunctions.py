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