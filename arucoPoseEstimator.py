import cv2
import numpy as np
import math
from fpdf import FPDF
from PIL import Image


class ArucoPoseEstimator:
    """This class handles aruco marker detection and pose estimation"""
    nextMarkerId = 0
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    def __init__(self, board_length, board_width, marker_size, marker_gap):
        """
        Creates ArucoPoseEstimator object
        :param board_length: Number of markers along length of object.
        :param board_width: Number of markers along length of object.
        :param marker_size: Size of each marker in pixels.
        :param marker_gap: Distance between each marker in pixels.
        """
        self._board = cv2.aruco.GridBoard_create(board_length, board_width, marker_size, marker_gap, self.dictionary,
                                                 self.nextMarkerId)
        self.nextMarkerId += board_length*board_width
        self._R0 = None
        self._T0 = None

    @staticmethod
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

    @staticmethod
    def getRelativeTranslation(tvec, R0, T0):
        """
        :param tvec: translation vector
        :param R0: Rotation matrix from camera to reference frame
        :param T0: Translation matrix from camera to reference frame
        :return: Relative translation of object from reference frame to object.
        """
        relative_tvec = (np.matrix(R0).T * (np.matrix(tvec) - np.matrix(T0)))
        return relative_tvec

    def getModelPose(self, frame, camera_matrix, dist_coeff, showFrame=False):
        """
        Analyzes frame to find six axis pose of model
        :param frame: image frame to get pose from
        :param camera_matrix:  Intrinsic camera matrix
        :param dist_coeff: Camera Distortion coefficients
        :param showFrame: set True to show analyzed frame in window.
        :return: Relative translation of model and euler angles of model.
        """
        #dist_coeff = np.matrix(dist_coeff)
        #print(frame)
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, self.dictionary)
        if showFrame:
            image_copy = frame
        if len(corners) > 0:
            retval, rvec, tvec = cv2.aruco.estimatePoseBoard(corners, ids, self._board, camera_matrix, dist_coeff)
            if self._R0 is None and retval:
                self._R0 = np.matrix(cv2.Rodrigues(rvec)[0])
            if self._T0 is None and retval:
                self._T0 = tvec
            if rvec is not None:
                relative_translation = np.array(self.getRelativeTranslation(tvec, self._R0, self._T0), dtype=int)
                relative_rotation = self._R0.T * np.matrix(cv2.Rodrigues(rvec)[0])
                euler_angles = np.array((180 * self.rotationMatrixToEulerAngles(relative_rotation)) / np.pi, dtype=int)
                if showFrame:
                    image_copy = cv2.aruco.drawDetectedMarkers(image_copy, corners, ids)
                    image_copy = cv2.aruco.drawAxis(image_copy, camera_matrix, dist_coeff, rvec, tvec, 200)
                    cv2.putText(image_copy, 'x = ' + str(relative_translation[0]), (0, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                .6, (0, 0, 255), 2)
                    cv2.putText(image_copy, 'y = ' + str(relative_translation[1]), (0, 130), cv2.FONT_HERSHEY_SIMPLEX,
                                .6, (0, 0, 255), 2)
                    cv2.putText(image_copy, 'z = ' + str(relative_translation[2]), (0, 160), cv2.FONT_HERSHEY_SIMPLEX,
                                .6, (0, 0, 255), 2)
                    cv2.putText(image_copy, 'roll = ' + str(euler_angles[0]), (0, 190), cv2.FONT_HERSHEY_SIMPLEX, .6,
                                (0, 0, 255), 2)
                    cv2.putText(image_copy, 'pitch = ' + str(euler_angles[1]), (0, 220), cv2.FONT_HERSHEY_SIMPLEX, .6,
                                (0, 0, 255), 2)
                    cv2.putText(image_copy, 'yaw = ' + str(euler_angles[2]), (0, 250), cv2.FONT_HERSHEY_SIMPLEX, .6,
                                (0, 0, 255), 2)
                if showFrame:
                    cv2.imshow('out', image_copy)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                return relative_translation, euler_angles

    def writeBoardToPDF(self, width=210, length=297):
        """
        Creates a printable pdf-file of this aruco board.
        :param width: Max width of this image
        :param length: Max length of this image
        :return: None
        """
        board_image = self._board.Draw(1000, 1000)
        cv2.imwrite("arucoBoard.png", board_image)
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.image("arucoBoard.png", w=width, h=length)
        pdf.output("arucoBoard.pdf")