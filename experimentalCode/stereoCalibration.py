import cv2
import numpy as np
import matplotlib.pyplot as plt

class VE:
    def __init__(self, stream, intrinsic, dist):
        self.stream = stream
        self.intrinsic = intrinsic
        self.dist = dist
        self.ret = False
        self.frame = None
        self.corners = None
        self.ids = None
        self.rejected = None

def repackCorners(board, ids):
    """
    Converts a corner list created from findArucoMarkers into  corner nx2 numpy array with corners sorted by marker id.
    :param board: original corner list
    :param ids: ids of aruco markers
    :return: list of repacked and sorted corners.
    """
    corners = np.zeros((len(board) * 4, 2))
    i = 0
    for id, square in zip(ids, board):
        index = id*4
        i = 0
        for corner in square[0]:
            corners[index + i] = corner
            print(corners)
            i += 1
    return corners

def repackAndFilterCorners(boards, ids):
    """
    Finds corresponding points in two lists of arucocorners, repacks and sorts them, then returns them.
    :param boards:
    :param ids:
    :return:
    """
    highestID = max(ids)
    commonIds = []
    for i in range(0, highestID+1):
        if i in ids[0] and i in ids[1]:
            commonIds.append(i)
    corners = []
    for i, board in enumerate(boards):
        corners.append(repackCorners(board, ids[i]))
    filteredCorners = [[],[]]
    for id in commonIds:
        for i in range(0, 4):
            filteredCorners[0].append(corners[0][id*4+i])
            filteredCorners[1].append(corners[1][id*4+i])
    return filteredCorners, commonIds


def drawlines(img1, img2, lines, pts1, pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r, c, d = img1.shape
    for r, pt1, pt2 in zip(lines, pts1, pts2):
        color = tuple(np.random.randint(0, 255, 3).tolist())
        x0, y0 = map(int, [0, -r[2]/r[1]])
        x1, y1 = map(int, [c, -(r[2]+r[0]*c)/r[1]])
        img1 = cv2.line(img1, (x0, y0), (x1, y1), color, 1)
        img1 = cv2.circle(img1, tuple(pt1), 5, color, -1)
        img2 = cv2.circle(img2, tuple(pt2), 5, color, -1)
    return img1, img2

cams = [None]*2
C = [None]*2
cams[0] = cv2.VideoCapture(0)
cams[1] = cv2.VideoCapture(1)
C[0] = np.load('A1calib.npz')
C[1] = np.load('A1calib.npz')
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
boardS = 3
markerSize = 40
markerGap = 5
margin = 10
resolution = 1
board = cv2.aruco.GridBoard_create(boardS, boardS, markerSize, markerGap, dictionary)
sizeInPixels = (((boardS * markerSize) + (markerGap * (boardS - 1)))*resolution) + (margin * 2)

boardImage = board.draw((sizeInPixels, sizeInPixels), margin, margin)
cv2.imwrite('board.jpg', boardImage)

boardCorners, boardIds, boardRejected = cv2.aruco.detectMarkers(boardImage, dictionary)
boardCorners = repackCorners(boardCorners, boardIds)
pxSize = 10
realSize = 40
boardCorners = np.append(boardCorners, np.zeros((len(boardCorners),1)), axis=1)
# boardCorners = tuple(map(tuple, boardCorners))

cameras = []

for i, cam in enumerate(cams):
    camera = VE(cam, C[i]['mtx'], C[i]['dist'])
    camera.ret, camera.frame = camera.stream.read()
    cameras.append(camera)

for camera in cameras:
    camera.corners, camera.ids, camera.rejected = cv2.aruco.detectMarkers(camera.frame, dictionary)
    camera.ret, camera.frame = camera.stream.read()
    camera.corners = repackCorners(camera.corners, camera.ids)

calibration = cv2.stereoCalibrate([boardCorners.astype('float32')], [cameras[0].corners.astype('float32')],
                                  [cameras[1].corners.astype('float32')], cameras[0].intrinsic,
                                  cameras[0].dist, cameras[1].intrinsic, cameras[1].dist, (640, 480))

retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = calibration


# Find epilines corresponding to points in right image (second image) and
# drawing its lines on left image
pts1 = cameras[0].corners.astype(int)
pts2 = cameras[1].corners.astype(int)
img1 = cameras[0].frame
img2 = cameras[1].frame
lines1 = cv2.computeCorrespondEpilines(pts2.reshape(-1, 1, 2), 2, F)
lines1 = lines1.reshape(-1, 3)
img5, img6 = drawlines(img1, img2, lines1, pts1, pts2)

# Find epilines corresponding to points in left image (first image) and
# drawing its lines on right image
lines2 = cv2.computeCorrespondEpilines(pts1.reshape(-1,1,2), 1,F)
lines2 = lines2.reshape(-1,3)
img3,img4 = drawlines(img2, img1, lines2, pts2, pts1)

plt.subplot(121), plt.imshow(img5)
plt.subplot(122), plt.imshow(img3)
plt.show()

