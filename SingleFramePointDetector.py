from heapq import nlargest
import cv2
import imutils
import numpy as np


class SingleFramePointDetector:
    '''
    Detect points in a single frame.
    '''
    def __init__(self):
        pass

    @staticmethod
    def findBallPoints(frame, lower_bounds=([46, 79, 60]), upper_bounds=([179, 255, 226])):
        """" Finds center points and radii of the largest circles in the image.
        :param frame: BGR-image to analyze
        :param lower_bounds: hsv lower bounds np array ex(170, 100, 100) for red
        :param upper_bounds: hsv lower bounds np array ex(40, 255, 255) for red
        :return: numpy array of size (3, 4) with x, y coordinate and radius of the
        4 largest circles in the frame. In cases where less circles are detected,
        remaining rows will returns with -1 """
        # blur image to remove hf-noise
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        lower_bounds = np.array(lower_bounds)
        upper_bounds = np.array(upper_bounds)
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
        cv2.imshow('Mask',mask)

        cv2.waitKey(27)
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)

        # only proceed if at least one contour was found
        enclosed_circles = np.ones((4, 3)) * -1
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
            if 0.7 < circularity < 1.2:
                all_circles.append(contour)
        # find the largest circles in the mask, then use
        # it to compute the minimum enclosing circles and
        # centroids
        if len(all_circles) == 0:
            return enclosed_circles
        elif len(all_circles) > 4:
            largest_circles = nlargest(4, all_circles, key=cv2.contourArea)
        else:
            largest_circles = [0]*len(all_circles)
            for (num, circle) in enumerate(all_circles):
                largest_circles[num] = circle
        for (num, circle) in enumerate(largest_circles):
            ((x, y), radius) = cv2.minEnclosingCircle(circle)
            enclosed_circles[num, :] = x, y, radius
        return enclosed_circles

if __name__ == '__main__':
    sfpd = SingleFramePointDetector()
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    points = sfpd.findBallPoints(frame)
    print('Points: ', points)
    cv2.imshow('Frame',frame)
    cv2.waitKey(0)
    cv2.imwrite('images\\boat_axiscross.jpg', frame)