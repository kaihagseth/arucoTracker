from heapq import nlargest
import cv2, imutils
import numpy as np




class SingleFramePointDetector():
    '''
    Detect points in a single frame.
    '''
    def __init__(self):
        pass

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
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
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