import logging

import cv2
import numpy as np
import math
from fpdf import FPDF


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
        self.nextMarkerId += board_length*board_width  # Next ID at 9 if 3x3
        self._R0 = None
        self._T0 = None
        # Image who shows pose and inframe-coordinate system in getPose function. Only if showImage TRUE.
        self.posPreviewImage = None



    @staticmethod
    def getRelativeTranslation(tvec, R0, T0):
        """
        :param tvec: translation vector
        :param R0: Rotation matrix from camera to reference frame
        :param T0: Translation matrix from camera to reference frame
        :return: Relative translation of object from reference frame to object.
        """
        # tvec - T0 - Translation to origo
        # Multiply with transverse rotation matrix to get back to reference coordinates.
        relative_tvec = np.matrix(R0).T * (np.matrix(tvec) - np.matrix(T0))
        return np.asarray(relative_tvec.T)[0]

    def getModelPose(self, frame, camera_matrix, dist_coeff, showFrame=False):
        """
        Analyzes frame to find six axis pose of model
        :param frame: image frame to get pose from
        :param camera_matrix:  Intrinsic camera matrix
        :param dist_coeff: Camera Distortion coefficients
        :param showFrame: set True to show analyzed frame in window.
        :return: Relative translation of model and euler angles of model as tuple of two np.arrays.
                 Tuple of two Nones if no position is found.
        """
        try:
            corners, ids, rejected = cv2.aruco.detectMarkers(frame, self.dictionary)
            msgc = "Corners: ", corners
            logging.debug(msgc)
            msgi = "Ids: ", ids
            logging.debug(msgi)
            if showFrame:
                image_copy = frame
            if len(corners) > 0:
                retval, rvec, tvec = cv2.aruco.estimatePoseBoard(corners, ids, self._board, camera_matrix, dist_coeff)
                if self._R0 is None and retval:
                    self._R0 = np.matrix(cv2.Rodrigues(rvec)[0])
                if self._T0 is None and retval:
                    self._T0 = tvec
                if rvec is not None:
                    relative_translation = self.getRelativeTranslation(tvec, self._R0, self._T0).astype(int)
                    # Multiplying with transverse ref rotation matrix to find current rotation relative to reference frame.
                    relative_rotation = self._R0.T * np.matrix(cv2.Rodrigues(rvec)[0])
                    euler_angles = np.degrees(self.rotationMatrixToEulerAngles(relative_rotation)).astype(int) % 360
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
                        self.posPreviewImage = image_copy

                    return relative_translation, euler_angles
            if showFrame:
                cv2.imshow('out', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
            return None, None
        except cv2.error as e:
            msg = str(e)
            logging.error(msg)



    def get2DPointsMarkers(self, corners, ids):
        '''
        Find and extract corners of each marker to use for stereovision.
        :param corners: All corners of all markers found in image
        :param ids: ID of all detected markers, given accordingly to order of cornerlist.
        :return: List of tuples containing (markerID, x-coord, y-coord)
        '''
        '''
        FOR REFERENCE 
       [2019-03-11 15:32:40,259 Cl:arucoPoseEstimator Fx:getModelPose Line:75 ] DEBUG: ('Corners: ', [array([[[174., 398.],
        [237., 388.],
        [245., 453.],
        [181., 464.]]], dtype=float32), array([[[244., 388.],
        [306., 378.],
        [315., 441.],
        [252., 451.]]], dtype=float32), array([[[313., 376.],
        [372., 367.],
        [383., 429.],
        [322., 439.]]], dtype=float32), array([[[168., 331.],
        [229., 322.],
        [236., 381.],
        [173., 391.]]], dtype=float32), array([[[236., 320.],
        [295., 312.],
        [304., 370.],
        [243., 380.]]], dtype=float32), array([[[302., 311.],
        [359., 302.],
        [370., 360.],
        [311., 369.]]], dtype=float32), array([[[228., 260.],
        [285., 252.],
        [294., 305.],
        [235., 314.]]], dtype=float32), array([[[163., 270.],
        [221., 261.],
        [227., 315.],
        [167., 323.]]], dtype=float32), array([[[292., 251.],
        [347., 243.],
        [358., 295.],
        [301., 304.]]], dtype=float32)])
       [2019-03-11 15:32:40,261 Cl:arucoPoseEstimator Fx:getModelPose Line:77 ] DEBUG: ('Ids: ', array([[6],
       [7],
       [8],
       [3],
       [4],
       [5],
       [1],
       [0],
       [2]], dtype=int32))
        '''
        idlist = []
        for n in ids:
            idlist.append(n[0])
        cornerlist = []
        for v in corners: # Iterate through all markers, each marker with 4 tuples for each corn coord.
            cornerlist.append(v[0])
        idcornerslist = []
        # Create the complete list:
        for i in range(len(ids)):
            idcornerslist.append((idlist[i],cornerlist[i][0],cornerlist[i][1]))
        return idcornerslist

    def getPosePreviewImage(self):
        return self.posPreviewImage

    def writeBoardToPDF(self, width=160):
        """
        Creates a printable pdf-file of this aruco board.
        :param width: Max width of this image
        :param length: Max length of this image
        :return: None
        """
        grid_size = self._board.getGridSize()
        marker_length = self._board.getMarkerLength()
        marker_separation = self._board.getMarkerSeparation()

        width = (grid_size[0] * marker_length) + (marker_separation * (grid_size[0] - 1))
        height = (grid_size[1] * marker_length) + (marker_separation * (grid_size[1] - 1))

        board_image = self._board.draw((int(width*12), int(height*12))) # About 300 dpi
        cv2.imwrite("arucoBoard.png", board_image)

        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.image("arucoBoard.png", w=width, h=height)
        pdf.image("images/arrow.png", x=20, y=height+20, w=30)
        pdf.output("arucoBoard.pdf")