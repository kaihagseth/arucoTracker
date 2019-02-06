import logging

import numpy as np
import cv2
import glob
from exceptions import FailedCalibrationException
images = glob.glob('*.jpg')



cv2.destroyAllWindows()



class IntrinsicCalibrator:
    '''
    Do intrinsic calibration on cameras.
    Returns a
    # TODO: Refactoring: Remove all references to parent camera.
    '''

    def __init__(self, parr_cam=None):
        self._curr_ret = None
        self._curr_rvecs = None
        self._curr_tvecs = None
        self._curr_camera_matrix = None
        self._curr_dist_coeff = None
        self._curr_newcamera_mtx = None
        self._curr_roi = None
        self._parr_cam = parr_cam
    def loadSavedValues(self, filename='IntriCalib.npz'):
        '''
        Load values to be used in calibration.
        This procvess is just needed if you don't want to do a new calibration,
        but use old values instead.
        :param filename: Filename to get values from.
        :return: None
        '''
        print('Loading old parameters from file ', filename)
        npzfile = np.load(filename)
        self._curr_camera_matrix = npzfile['mtx']
        self._curr_dist_coeff = npzfile['dist']
        self._curr_newcamera_mtx = npzfile['newcameramtx']
        self._curr_roi = npzfile['roi']

    def calibCam(self, frames):
        '''
        Calibrate the camera lens.
        :param frames: List of frames to use in calibration.
        :return: None
        '''

        #Save the images to a distinct camera folder
        i = 1
        cb_n_width = 7
        cb_n_height = 9
        camID = 0
        ''' Make sure we don't use invalid ID.  '''
        if self._parr_cam is None:
            camID = '0'
            logging.error('CameraID not found!')
        else:
            camID = self._parr_cam._ID
        ''' Add all images in folder ''' #TODO: Fix this
        for frame in frames:
            path = 'images/cam_{0}/calib_img{1}.png'.format(camID, i)
            cv2.imwrite(path, frame)
            i = i+1
        # Termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,4,0)
        objp = np.zeros((cb_n_width * cb_n_height, 3), np.float32)
        objp[:, :2] = np.mgrid[0:cb_n_height, 0:cb_n_width].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.
        try: # If cv2 fails, raise FailedCalibrationException
            gray = None
            img = frames[0]
            ''' For each frame in list, find cb-corners and add object and image points in a list. '''
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (cb_n_height, cb_n_width), None)

                ''' If found, add object points, image points (after refining them) '''
                if ret == True:
                    objpoints.append(objp)
                    cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    imgpoints.append(corners)
                    ''' Draw and display the corners '''
                    cv2.drawChessboardCorners(frame, (cb_n_height, cb_n_width), corners, ret)
                    cv2.imshow('img', frame)
                    cv2.waitKey(500)
            cv2.destroyAllWindows()
            '''Do the calibration:'''
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            h, w = img.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
            '''Undistort the image: '''
            dst = cv2.undistort(gray, mtx, dist, None, newcameramtx)
            if not dst.any(): #dst is empty, no calib result is found.
                raise FailedCalibrationException(msg='Failed to do cv2.undistort(). Try with new picture.')
            # crop the image
            x, y, w, h = roi
            dst = dst[y:y + h, x:x + w]
            #cv2.imshow('Calib res', dst)
            #cv2.waitKey(0)
            '''Only write image if list is more a single frame.'''
            if len(frames) >= 2:
                cv2.imwrite('images/calibresult.png', dst)
            '''Save latest values to a file.'''
            filename = 'IntriCalib{0}'.format(camID)
            np.savez(filename, ret=ret, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs, newcameramtx=newcameramtx, roi=roi)
            '''Update class with latest numbers.'''
            self._parr_cam.set_intrinsic_params(mtx)
            self._curr_ret = ret
            self._curr_camera_matrix = mtx
            self._curr_dist_coeff = dist
            self._curr_rvecs = rvecs
            self._curr_tvecs = tvecs
            self._curr_newcamera_mtx = newcameramtx
            self._curr_roi = roi

        except IndexError:
            pass#cv2.error as e:
         #   print('OpenCV failed. ')
          #  print('MSG: ', e)
           # raise FailedCalibrationException(msg=e)
    def printCurrParams(self):
        print('_curr_ret : ', self._curr_ret)
        print('_curr_mtx : ', self._curr_camera_matrix)
        print('_curr_dist : ', self._curr_dist_coeff)
        print('_curr_rvecs : ', self._curr_rvecs)
        print('_curr_newcameramtx : ', self._curr_newcamera_mtx)
        print('_curr_roi : ', self._curr_roi)

    def undistort_image(self, image):
        img =  cv2.undistort(image, self._curr_camera_matrix, self._curr_dist_coeff,
                             newCameraMatrix=self._curr_newcamera_mtx)
        logging.debug('Image: ', img)
        x, y, w, h = self._curr_roi
        dst = img[y:y + h, x:x + w]
        return dst
        # def undistort_image(self, image):
        #return cv2.undistort(image, self.camera_matrix, self.dist_coeffs,
        #                     newCameraMatrix=self.new_camera_matrix)
    def undistortImage(self, img):
        '''
        Goal: Insert a distored image and get a undistorted image back.
        :param img: Distorted image
        :return: A undistorted image.
        '''
        try:
            logging.debug('Inside undistortImage()')
            dst = cv2.undistort(img, self._curr_camera_matrix, self._curr_dist_coeff, None, self._curr_newcamera_mtx)
            logging.debug(dst)
        except cv2.error: # Not successfull
            raise FailedCalibrationException
        if not dst.any():  # dst is empty, no calib result is found.
            raise FailedCalibrationException(msg='Failed to do cv2.undistort(). Try with new picture.')
        # crop the image
        logging.debug('Past dst')
        x, y, w, h = self._curr_roi
        dst = dst[y:y + h, x:x + w]
        return dst
if __name__ == "__main__":
    '''
    For debug only
    '''
    ic = IntrinsicCalibration()
    ic.loadSavedValues()
    ic.pri
    #ic.calibCam([cv2.imread('images/img.jpg')])

    ''' print('Hello')
    ic = IntrinsicCalibration()
    ic.loadSavedValues('IntriCalib.npz')
    #ic.calibCamDefault(useDemo=True)
    print('Hi')
    img = cv2.imread('images/img.jpg')
    print('OK')
    imgd = None
    try:
        print('Inside imgd')
        imgd = ic.undistortImage(img)
    except FailedCalibrationException:
        print('Unsuccesfull')
    print('Img: ', imgd)
    cv2.imshow('Undistort',imgd)
    cv2.imwrite('images/imgd.jpg', imgd)
    cv2.waitKey(7000)'''