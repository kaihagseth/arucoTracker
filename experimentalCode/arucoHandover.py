import cv2
import numpy as np
import math


class VE:
    def __init__(self, stream):
        """
        Initialize Vision entity
        :param stream: VideoStream
        """
        self.stream = stream
        self.intrinsic_matrix = None
        self.distortion_coeff = None
        self.Mrvec = None # Model - camera rvec
        self.Mtvec = None # Model camera tvec
        self.Crvec = None # Camera world rvec
        self.Ctvec = None # Camera world tvec
        self.frame = None
        self.corners = None
        self.ids = None
        self.rejected = None

    def reset(self):
        """
        Set model pose to None.
        :return:
        """
        self.Mtvec = None
        self.Mrvec = None

    def setCameraPosition(self, board):
        """
        Sets the camera position in world coordinates
        :param board: The aruco board seen from cam.
        :param cam: Camera to be calibrated.
        :return:
        """
        self.Crvec, self.Ctvec = cv2.composeRT(-board.rvec, board.tvec, -self.Mrvec, -self.Mtvec,)[0:2]


class board:
    def __init__(self, grid_board):
        self.rvec = None # Model World rvec
        self.tvec = None # Model World tvec
        self.isVisible = True
        self.grid_board = grid_board

    def updateBoardPosition(self, cam):
        """
        Sets boards pose in world coordinates from a calibrated camera.
        :param cam: The camera spotting the board.
        :return:
        """
        self.rvec = cv2.composeRT(cam.Crvec, cam.Ctvec, cam.Mrvec, cam.Mtvec)[0]
        self.getRelativeTranslation(cam)

    def setFirstBoardPosition(self, cam):
        """
        Sets the board to origo and calibrates camera.
        :param board:
        :param cam:
        :return:
        """
        self.rvec = np.array([0, 0, 0], dtype=np.float32)
        self.tvec = np.array([0, 0, 0], dtype=np.float32)
        cam.setCameraPosition(self)

    def getRelativeTranslation(self, cam):
        """
        Gets translation from model to camera.
        :param cam: camera that sees model.
        :return: None
        """
        self.tvec = toMatrix(cam.Crvec) * np.matrix(cam.Ctvec + cam.Mtvec)


def rotationMatrixToEulerAngles(R):
    '''https://www.learnopencv.com/rotation-matrix-to-euler-angles/'''
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


def toMatrix(rvec):
    """
    Transform rvec to matrix
    :param rvec: Rotation Vector
    :return:
    """
    matrix = np.matrix(cv2.Rodrigues(rvec)[0])
    return matrix


def drawAxis(frame, vision_entity):
    """
    Draws axis cross on image frame
    :param frame: Image frame to be drawn on
    :param vision_entity: Vision entity the frame came from.
    :return:
    """
    return cv2.aruco.drawAxis(frame, vision_entity.intrinsic_matrix, vision_entity.distortion_coeff,
                              vision_entity.Mrvec, vision_entity.Mtvec, 200)


def findNewMasterCam(cams):
    """
    Sets the master cam to a camera that is calibrated and has the board in sight.
    :param cams:
    :return: master cam
    """
    for cam in cams:
        if cam.Mrvec is not None and cam.Crvec is not None:
            return cam
    return None

# Initialize cameras and board.
cam0 = VE(cv2.VideoCapture(0))
cam1 = VE(cv2.VideoCapture(1))
A1 = np.load("A1calib.npz")
A2 = np.load("A2calib.npz")
cam0.intrinsic_matrix = A1["mtx"]
cam1.intrinsic_matrix = A2["mtx"]
cam0.distortion_coeff = A1["dist"]
cam1.distortion_coeff = A2["dist"]
cam0.master = True
cams = [cam0, cam1]
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
markerSize = 40
markerGap = 5
masterCam = None
board = board(cv2.aruco.GridBoard_create(3, 3, markerSize, markerGap, dictionary))
outFrame = None

while True:
    # Resets the boards visible status.
    board.isVisible = False
    for cam in cams:
        cam.stream.grab()
        cam.reset()
    for cam in cams:
        ret, cam.frame = cam.stream.retrieve()
        cam.corners, cam.ids, cam.rejected = cv2.aruco.detectMarkers(cam.frame, dictionary)
        # Collecting frame and detecting markers for each camera.
        if len(cam.corners) > 0:
            _, cam.Mrvec, cam.Mtvec = cv2.aruco.estimatePoseBoard(cam.corners, cam.ids, board.grid_board,
                                                                  cam.intrinsic_matrix, cam.distortion_coeff)
            # When the board is spotted for the first time by a camera and a pose is calculated successfully, the boards
            # pose is set to origen, and the camera is set as the master cam.
            if board.rvec is None and (cam.Mrvec is not None):
                board.setFirstBoardPosition(cam)
                board.isVisible = True
                masterCam = cam

    # If the master cam failed to calculate a pose, another camera is set as master.
    if masterCam is None or masterCam.Mrvec is None:
        masterCam = findNewMasterCam(cams)
        continue
    else:
        # Update board position if the board is masterCams frame
        board.updateBoardPosition(masterCam)
        outFrame = masterCam.frame

    # Set camera world positions if they are not already set and both the camera and the master camera can see the frame
    for cam in cams:
        if masterCam is None:
            break
        if cam.Crvec is None and cam.Mrvec is not None and masterCam.Mrvec is not None and cam is not masterCam:
            cam.setCameraPosition(board)

    # If the master camera cannot see the board, but another calibrated camera can, the calibrated camera becomes the
    # new master camera
    for cam in cams:
        if cam.Mrvec is not None and cam.Crvec is not None and masterCam.Mrvec is None:
            masterCam = cam
            break

    if outFrame is None:
        continue
    # Draw image to show
    outFrame = cv2.aruco.drawDetectedMarkers(outFrame, masterCam.corners, masterCam.ids)
    outFrame = drawAxis(outFrame, masterCam)
    x, y, z = np.array(board.tvec, dtype=int)
    roll, yaw, pitch = np.rad2deg(rotationMatrixToEulerAngles(toMatrix(board.rvec))).astype(int)
    outFrame = drawAxis(outFrame, masterCam)
    f, fscale, color, thickness = cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2
    cv2.putText(outFrame, 'x = ' + str(x), (0, 100), f, fscale, color, thickness)
    cv2.putText(outFrame, 'y = ' + str(y), (0, 130),  f, fscale, color, thickness)
    cv2.putText(outFrame, 'z = ' + str(z), (0, 160), f, fscale, color, thickness)
    cv2.putText(outFrame, 'pitch = ' + str(pitch), (0, 190), f, fscale, color, thickness)
    cv2.putText(outFrame, 'yaw = ' + str(yaw), (0, 220), f, fscale, color, thickness)
    cv2.putText(outFrame, 'roll = ' + str(roll), (0, 250), f, fscale, color, thickness)
    cv2.imshow('out', outFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()