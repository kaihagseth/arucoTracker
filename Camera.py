import numpy as np
from WebcamVideoStream import WebcamVideoStream
import cv2
from IntrinsicCalibration import IntrinsicCalibration
import imutils
from heapq import nlargest
from math import pi
import time

'''
Class for Object Tracking Camera.
'''
class Camera():
    def __init__(self,camName="Cam0", camID=0, srcIndex=0, cam_loca=False, cam_pose_mtrc=None, aov=False, intri_cam_mtrx=None):
        '''Create a cam '''
        print("Creating OTCam")
        self._ID = camID # A distinct number for each camera.
        self._name = camName
        self._intri_cam_mtrx = intri_cam_mtrx
        self._cam_loca = cam_loca
        self._cam_pose = cam_pose_mtrc
        self.src = srcIndex
        self.vidCap = cv2.VideoCapture(self.src)
        self._aov = aov
        self._IC = IntrinsicCalibration(self)

    def startVidStream(self):
        '''
        Start threaded vidstream. Needs more work.
        :return:
        '''
        self._vidstreamthread = WebcamVideoStream(src=0,camName=self._name)
        self._vidstreamthread.start()
    def getFrame(self):
        '''Get frame from vidthread.'''
        self._vidstreamthread.read()

    def set_intrinsic_params(self, new_mtrx):
        '''Set intrinsic params for the camera'''
        self._intri_cam_mtrx = new_mtrx

    def set_dist_coeff(self, new_dist_coeff):
        self._dist_coeff = new_dist_coeff


    def calibrateCamera(self):
        '''
        Calibrate the camera.
        Take a image, find the
        :return:
        '''
    def getSingleFrame(self):
        '''Get non-threaded camera frame.'''
        grabbed, frame = self.vidCap.read()
        return frame

    def calibrateCam(self, cbFrames):
        '''
        Calibrate the camera in the IC-section.
        :param cbFrame:
        :return:
        '''
        self._IC.calibCam(cbFrames)
    def loadSavedCalibValues(self):
        self._IC.loadSavedValues()

    def undistort(self, img):
        '''Return a undistorted version of a distorted image. '''
        self._IC.undistort_image(img)
    def activateSavedValues(self, filename='IntriCalib.npz'):
        '''Load and use the earlier saved intrinsic parameters from a file.
        :param filename: Name of file to get params from.
        '''
        self._IC.loadSavedValues(filename)

    # Code based upon this guide: https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
    # import the necessary packages

    def findBallPoints(self, frame, lower_bounds, upper_bounds):
        # frame - BGR-image to analyze
        # lower bounds - hsv lower bounds np array
        # upper bounds - hsv lower bounds np array

        # construct the argument parse and parse the arguments
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)

        # Hack to bypass inRange's limitation of looping around 0 in the H-channel in HSV.
        if lower_bounds[0] < upper_bounds[0]:
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        else:
            lower_bounds[0] -= 90
            upper_bounds[0] += 90
            hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)

        # construct a mask for the color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, lower_bounds, upper_bounds)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        contours = imutils.grab_contours(contours)
        cv2.drawContours(blurred, contours, -1, (0, 255, 0), 3)
        cv2.imshow('mask', blurred)

        # only proceed if at least one contour was found
        if len(contours) > 0:
            circles = []
            # Check each blob if it is circular enough.
            for contour in contours:
                perimeter = cv2.arcLength(contour, True)
                area = cv2.contourArea(contour)
                if perimeter == 0:
                    break
                circularity = 4 * pi * (area / (perimeter * perimeter))
                if 0.7 < circularity < 1.2:
                    circles.append(contour)

            # find the largest circles in the mask, then use
            # it to compute the minimum enclosing circles and
            # centroids
            if len(circles) == 0:
                return []
            elif len(circles) > 3:
                largest_circles = nlargest(3, circles, key=cv2.contourArea)
            else:
                largest_circles = nlargest(len(circles), circles, key=cv2.contourArea)
            enclosed_circles = np.zeros((len(largest_circles), 3))
            for (num, circle) in enumerate(largest_circles):
                ((x, y), radius) = cv2.minEnclosingCircle(circle)
                enclosed_circles[num, :] = x, y, radius
            return enclosed_circles
        return []

#otc1 = OTCam()
#otc2 = OTCam(camName="Cam2",srcIndex=1)
#time.sleep(1)
#frame = otc1.getFrame()
#print(frame)
#cv2.imshow("Hello",frame)
#cv2.waitKey(0)