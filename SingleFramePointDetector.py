import logging
from heapq import nlargest
import cv2
import imutils
import numpy as np
import time


def callback(x):
    pass


class SingleFramePointDetector:
    '''
    Detect a number of points in a single frame.
    '''
    def __init__(self):
        self.lower_hue = 0
        self.lower_saturation = 0
        self.lower_value = 0
        self.upper_hue = 180
        self.upper_saturation = 255
        self.upper_value = 255
        self.NUMBER_OF_POINTS = 3

    def setHSVValues(self, lower_values, upper_values):
        """
        :param lower_values: List of lower bound hsv values.
        :param upper_values:  List of upper bound hsv values.
        :return: None
        """
        self.lower_hue = lower_values(0)
        self.lower_saturation = lower_values(1)
        self.lower_value = lower_values(2)
        self.upper_hue = upper_values(0)
        self.upper_saturation = upper_values(1)
        self.upper_value = upper_values(2)

    def saveHSVValues(self):
        filename = 'HSVValues'
        np.savez(filename, lh=self.lower_hue, uh=self.upper_hue, ls=self.lower_saturation, us=self.upper_saturation, lv=self.lower_value, uv=self.upper_value)

    def loadHSVValues(self):
        filename = 'HSVValues.NPZ'
        print('Loading old parameters from file ', filename)
        npzfile = np.load(filename)
        self.lower_hue = npzfile['lh']
        self.lower_saturation = npzfile['ls']
        self.lower_value = npzfile['lv']
        self.upper_hue = npzfile['uh']
        self.upper_saturation = npzfile['us']
        self.upper_value = npzfile['uv']

    def calibrate(self, camera):
        """
        :param cap: Videocapture-stream from camera to be calibrated
        :return: None
        """
        cv2.namedWindow('image')
        cv2.createTrackbar('lowH', 'image', self.lower_hue, 179, callback)
        cv2.createTrackbar('highH', 'image', self.upper_hue, 179, callback)

        cv2.createTrackbar('lowS', 'image', self.lower_saturation, 255, callback)
        cv2.createTrackbar('highS', 'image', self.upper_saturation, 255, callback)

        cv2.createTrackbar('lowV', 'image', self.lower_value, 255, callback)
        cv2.createTrackbar('highV', 'image', self.upper_value, 255, callback)

        while (True):
            # grab the frame
            #ret, frame = cap.read()
            frame = camera.getSingleFrame()
            frame = camera.getSingleFrame()
            frame = camera.getSingleFrame()
            # get trackbar positions
            self.lower_hue = cv2.getTrackbarPos('lowH', 'image')
            self.upper_hue = cv2.getTrackbarPos('highH', 'image')
            self.lower_saturation = cv2.getTrackbarPos('lowS', 'image')
            self.upper_saturation = cv2.getTrackbarPos('highS', 'image')
            self.lower_value = cv2.getTrackbarPos('lowV', 'image')
            self.upper_value = cv2.getTrackbarPos('highV', 'image')

            if self.lower_hue < self.upper_hue:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_hsv = np.array([self.lower_hue, self.lower_saturation, self.lower_value])
                higher_hsv = np.array([self.upper_hue, self.upper_saturation, self.upper_value])
            else:
                hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
                lower_hsv = np.array([self.lower_hue - 90, self.lower_saturation, self.lower_value])
                higher_hsv = np.array([self.upper_hue + 90, self.upper_saturation, self.upper_value])
            mask = cv2.inRange(hsv, lower_hsv, higher_hsv)

            image = cv2.bitwise_and(frame, frame, mask=mask)

            # show thresholded image
            cv2.imshow('image', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def findBallPoints(self, frame):
        """" Finds center points and radii of the largest circles in the image.
        :param frame: BGR-image to analyze
        :param lower_bounds: hsv lower bounds np array ex(170, 100, 100) for red
        :param upper_bounds: hsv lower bounds np array ex(40, 255, 255) for red
        :return: numpy array of size (3, 4) with x, y coordinate and radius of the
        4 largest circles in the frame. In cases where less circles are detected,
        remaining rows will returns with -1 """
        logging.info('Running findBallPoints()')
        cv2.imshow('frame', frame)
        cv2.waitKey(0)
        #print('Frame: ', frame)
        # blur image to remove hf-noise
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        if self.lower_hue < self.upper_hue:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_bounds = np.array([self.lower_hue, self.lower_saturation, self.lower_value])
            upper_bounds = np.array([self.upper_hue, self.upper_saturation, self.upper_value])
        else:
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            lower_bounds = np.array([self.lower_hue - 90, self.lower_saturation, self.lower_value])
            upper_bounds = np.array([self.upper_hue + 90, self.upper_saturation, self.upper_value])

        # construct a mask for the color, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, lower_bounds, upper_bounds)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cv2.imwrite('mask.jpg',mask)
        cv2.imshow('frame',mask)
        cv2.waitKey(0)
#        time.sleep(0, 1)
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # only proceed if at least one contour was found
        enclosed_circles = np.ones((self.NUMBER_OF_POINTS, 3)) * -1
        if len(contours) == 0:
            return enclosed_circles
        all_circles = []
        # Check each blob if it is circular enough.
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            area = cv2.contourArea(contour)
            if perimeter == 0:
                break
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            if 0.0 < circularity < 5:
                all_circles.append(contour)
        # find the largest circles in the mask, then use
        # it to compute the minimum enclosing circles and
        # centroids
        if len(all_circles) == 0:
            return enclosed_circles
        elif len(all_circles) > self.NUMBER_OF_POINTS:
            largest_circles = nlargest(self.NUMBER_OF_POINTS, all_circles, key=cv2.contourArea)
        else:
            largest_circles = [0]*len(all_circles)
            for (num, circle) in enumerate(all_circles):
                largest_circles[num] = circle
        for (num, circle) in enumerate(largest_circles):
            ((x, y), radius) = cv2.minEnclosingCircle(circle)
            enclosed_circles[num, :] = x, y, radius
        return enclosed_circles

    def getHSVValues(self):
        """
        :return: lower HSV values and upper HSV values used to threshold image segmentation
        """
        lower_values = (self.lower_hue, self.lower_saturation, self.lower_value)
        upper_values = (self.upper_hue,  self.upper_saturation, self.upper_value)
        return lower_values, upper_values


if __name__ == '__main__':
    sfpd = SingleFramePointDetector()
    cap = cv2.VideoCapture(1)
    #
    sfpd.calibrate(cap)
    ret, frame = cap.read()
    points = sfpd.findBallPoints(frame)
    print('Points: ', points)
    cv2.imshow('Frame',frame)
    cv2.waitKey(0)
    cv2.imwrite('images\\boat_axiscross.jpg', frame)