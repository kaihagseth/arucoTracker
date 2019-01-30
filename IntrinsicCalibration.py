import numpy as np
import cv2
import glob
from exceptions import FailedCalibrationException
images = glob.glob('*.jpg')



cv2.destroyAllWindows()



class IntrinsicCalibration():
    '''
    Do intrinsic calibration on cameras.
    '''

    def __init__(self):
        pass
    def calibCamDefault(self, frame=None, useDemo=False, showImg=False):
        '''
        Doing checkboard calib:
        '''''

        if not useDemo:
            img = frame
            cv2.imwrite('images/raw.jpg', img)
        else:
            img = cv2.imread('images/img.jpg')

        #showImg = True
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((7 * 5, 3), np.float32)
        objp[:, :2] = np.mgrid[0:7, 0:5].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.
#        size_frame = [len(img[1]), len(img)]

        print('Inside')
        # img = cv2.imread(fname)
        print(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (7, 5), None)
        cv2.imwrite('images/img.jpg', img)

        # If found, add object points, image points (after refining them)
        if ret == True:
            print('Inside')
            objpoints.append(objp)

            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (7, 5), corners2, ret)
            if showImg:
                cv2.imshow('img', img)
                cv2.waitKey(0)
            cv2.imwrite('images/imgcorners.jpg', img)
            import time
            # time.sleep(10)
        #cv2.destroyAllWindows()
        print('Calibrate')
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        img = cv2.imread('images/raw.jpg')
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        # undistort
        print('Img: ', img)
        print('Gray: ', gray)
        print('Undistort')
        mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
        dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
        print('Dist: ', dst)
        # crop the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]
        cv2.imwrite('images/calibresult.png', dst)

        #print(img, mtx, dist, None, newcameramtx)
        #dst = cv2.undistort(gray, mtx, dist, None, newcameramtx)
        #print('First dst: ', dst)
        # crop the image
        #x, y, w, h = roi
        #print('ROI: ', roi)
        #dst = dst[y:y + h, x:x + w]
        #print('Last dst: ', dst)
        cv2.imshow('Calib pic', dst)
        cv2.imshow('Original', frame)
        cv2.waitKey(0)
        cv2.imwrite('images/calibresult.png', dst)
    def undistortImg(self):
        pass
    def calibCamVeg(self, frame):
        try:
            cv2.imwrite('images/img.jpg', frame)
            # termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

            # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
            objp = np.zeros((7 * 5, 3), np.float32)
            objp[:, :2] = np.mgrid[0:5, 0:7].T.reshape(-1, 2)

            # Arrays to store object points and image points from all the images.
            objpoints = []  # 3d point in real world space
            imgpoints = []  # 2d points in image plane.

            images = ['images/img.jpg']  # glob.glob('*.jpg')
            gray = None
            for fname in images:
                img = cv2.imread(fname)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (5, 7), None)

                # If found, add object points, image points (after refining them)
                if ret == True:
                    objpoints.append(objp)

                    cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    imgpoints.append(corners)

                    # Draw and display the corners
                    cv2.drawChessboardCorners(img, (5, 7), corners, ret)
                    cv2.imshow('img', img)
                    cv2.waitKey(500)

            cv2.destroyAllWindows()

            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

            img = cv2.imread('images/img.jpg')
            h, w = img.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

            # undistort
            dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
            arr = np.array(dst)
            if not dst.any(): #dst is empty, no calib result is found.
                raise FailedCalibrationException(msg='Failed to do cv2.undistort(). Try with new picture.')
            # crop the image
            x, y, w, h = roi
            dst = dst[y:y + h, x:x + w]
            #cv2.imshow('Calib res', dst)
            #cv2.waitKey(0)
            cv2.imwrite('images/calibresult.png', dst)
  #          np.savez('B', ret=ret, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)
        except cv2.error:
            print('OpenCV failed. ')
            raise FailedCalibrationException(msg='Calib failed')

if __name__ == "__main__":
    ic = IntrinsicCalibration()
    ic.calibCamDefault(useDemo=True)