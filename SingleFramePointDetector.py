import logging
from heapq import nlargest
import cv2
import imutils
import numpy as np
import time
import warnings


def callback():
    pass

class SingleFramePointDetector:
    '''
    Detect a number of points in a single frame.
    '''
    def __init__(self):
        self._lower_hue = 0
        self._lower_saturation = 0
        self._lower_value = 0
        self._upper_hue = 180
        self._upper_saturation = 255
        self._upper_value = 255
        self._hsv_is_calibrated = False
        self.NUMBER_OF_POINTS = 3

    def setHSVValues(self, lower_values, upper_values):
        """
        :param lower_values: List of lower bound hsv values.
        :param upper_values:  List of upper bound hsv values.
        :return: None
        """
        self._lower_hue = lower_values[0]
        self._lower_saturation = lower_values[1]
        self._lower_value = lower_values[2]
        self._upper_hue = upper_values[0]
        self._upper_saturation = upper_values[1]
        self._upper_value = upper_values[2]
        self._hsv_is_calibrated = True

    def saveHSVValues(self):
        """
        Save the current HSV values to a file.
        :return: None
        """
        filename = 'HSVValues'
        lower_values, upper_values = self.getHSVValues()
        np.savez(filename, lh=lower_values[0], uh=upper_values[0], ls=lower_values[1], us=upper_values[1],
                 lv=lower_values[2], uv=upper_values[2],)

    def loadHSVValues(self):
        """
        Load HSV values from the saved file
        :return: None
        """
        filename = 'HSVValues.NPZ'
        try:
            print('Loading old parameters from file ', filename)
            npzfile = np.load(filename)
        except FileNotFoundError as e:
            print("HSVValues.NPZ was not found. Create the file before loading it.")
            return
        self.setHSVValues((npzfile['lh'], npzfile['ls'], npzfile['lv']), (npzfile['uh'], npzfile['us'], npzfile['uv']))


    def calibrate(self, camera):
        """
        :param cap: Videocapture-stream from camera to be calibrated
        :return: None
        """
        cv2.namedWindow('image')
        cv2.createTrackbar('lowH', 'image', 0, 179, callback)
        cv2.createTrackbar('highH', 'image', 179, 179, callback)
        cv2.createTrackbar('lowS', 'image', 0, 255, callback)
        cv2.createTrackbar('highS', 'image', 255, 255, callback)
        cv2.createTrackbar('lowV', 'image', 0, 255, callback)
        cv2.createTrackbar('highV', 'image', 255, 255, callback)

        while (True):
            # grab the frame
            frame = camera.getSingleFrame()
            # get trackbar positions
            lower_values = (cv2.getTrackbarPos('lowH', 'image'), cv2.getTrackbarPos('lowS', 'image'),
                            cv2.getTrackbarPos('lowV', 'image'))
            upper_values = (cv2.getTrackbarPos('highH', 'image'), cv2.getTrackbarPos('highS', 'image'),
                            cv2.getTrackbarPos('highV', 'image'))
            self.setHSVValues(lower_values, upper_values)
            mask = self.getHSVmask(frame)
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
        # blur image to remove hf-noise)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        # construct a mask for the color, then perform morphology to remove noise
        mask = self.getHSVmask(blurred)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
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
        # TODO: Beware of the cirularity check! Currently disabled
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
        :return: lower HSV values and upper HSV values used to threshold image segmentation in a numpy array
        """
        if not self._hsv_is_calibrated:
            warnings.warn("HSV-values has not been calibrated or imported! No mask is applied.", UserWarning)
        lower_values = np.array((self._lower_hue, self._lower_saturation, self._lower_value))
        upper_values = np.array((self._upper_hue,  self._upper_saturation, self._upper_value))
        return lower_values, upper_values

    def getHSVmask(self, frame):
        """
        Returns a binary mask from a BGR-image and this objects hsv-thresholds
        :param frame: BGR-image
        :return: Binary mask based on input and this objects hsv-values
        """
        ((lower_hue, lower_saturation, lower_value), (upper_hue, upper_saturation, upper_value)) = self.getHSVValues()
        # This code block allows looping around the hue channel.
        if lower_hue < upper_hue:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_hsv, higher_hsv = self.getHSVValues()
            mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
        else:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_hsv = np.array([lower_hue, lower_saturation, lower_value])
            higher_hsv = np.array([180, upper_saturation, upper_value])
            lower_hsv2 = np.array([0, lower_saturation, lower_value])
            higher_hsv2 = np.array([upper_hue, upper_saturation, upper_value])
            lower_mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
            higher_mask = cv2.inRange(hsv, lower_hsv2, higher_hsv2)
            mask = cv2.add(lower_mask, higher_mask)
        return mask

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