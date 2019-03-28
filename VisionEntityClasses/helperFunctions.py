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
    if rvec is None:
        return None
    R = np.matrix(cv2.Rodrigues(rvec)[0], dtype=np.float32)
    T = np.matrix(tvec, dtype=np.float32)
    T = np.reshape(T, (3, 1))
    RT = np.matrix(np.vstack((np.hstack((R, T)), [0, 0, 0, 1])))
    return RT

def transMatrixToRvecTvec(RT):
    """
    Returns rvec and tvec from a homogenous transformation matrix
    :param RT: 4x4 Transformation Matrix
    :return: Rodrigues vectors
    """
    if RT is not None:
        R = RT[0:3, 0:3]
        rvec = cv2.Rodrigues(R)[0]
        tvec = np.asarray(RT[0:3, 3])
    else:
        rvec = None
        tvec = None

    return rvec, tvec

def invertTransformationMatrix(RT):
    """
    Returns an inverse transformation matrix
    :param RT: Transformation matrix to be inverted
    :return: Inverted transformation matrix
    """
    RT = np.matrix(RT)
    R0 = RT[0:3, 0:3]  # Get rotation matrix
    R1 = R0.T  # Transpose rotation matrix to find inverse rotation
    T0 = np.matrix(RT[0:3, 3])  # Get translation vector
    T1 = -(R1 * T0)  # Find opposite direction of translation vector
    RT1 = np.matrix(np.vstack((np.hstack((R1, T1)), [0, 0, 0, 1])))
    return RT1

def stackChecker(list):
    """
    Pops and returns first item of list, or returns False if list is empty.
    :return: First item of list, or "False" if list is empty
    """
    if list:
        out = list.pop(0)
    else:
        out = False
    return out

def extendListToIndex(list, index, fillObject=None):
    """
    Pads a list to the point where its last index is the same as the input index if the list is shorter than the
    :param list: List to extend
    :param index: Index to extend to
    :param fillObject: Object to pad list with
    :return: None
    """
    indexListLengthDifference = (index + 1) - len(list)
    if indexListLengthDifference > 0:
        list.extend([fillObject] * indexListLengthDifference)
