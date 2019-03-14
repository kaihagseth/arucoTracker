import cv2
import numpy as np


def toMatrix(rvec):
    """
    Transform rvec to matrix
    :param rvec: Rotation Vector
    :return:
    """
    matrix = np.matrix(cv2.Rodrigues(rvec)[0])
    return matrix
