import logging

import cv2
import numpy as np

from exceptions import FailedCalibrationException

"""
This module handles camera calibration.
"""

def calibCam(self, frames, showCalibration=False, cb_square_size=1):
    '''
    Calibrate the camera lens.
    :param frames: List of frames to use in calibration.
    :return: None
    '''
    cb_n_width = 5
    cb_n_height = 7
    #Save the images to a distinct camera folder

    ''' Make sure we don't use invalid ID.  '''
    if self._parr_cam is None:
        camID = '0'
        logging.error('CameraID not found!')
    else:
        camID = self._parr_cam.getSrc()
    # Termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,4,0)
    objp = np.zeros((cb_n_width * cb_n_height, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cb_n_height, 0:cb_n_width].T.reshape(-1, 2)*cb_square_size

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    corners = False
    try: # If cv2 fails, raise FailedCalibrationException
        gray = None
        img = frames[0]
        ''' For each frame in list, find cb-corners and add object and image points in a list. '''
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (cb_n_height, cb_n_width), None)
            ''' If found, add object points, image points (after refining them) '''
            if ret:
                objpoints.append(objp)
                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners)
                ''' Draw and d isplay the corners '''
                if showCalibration:
                    cv2.drawChessboardCorners(frame, (cb_n_height, cb_n_width), corners, ret)
                    cv2.imshow('img', frame)
                    cv2.waitKey(1)
            else:
                logging.error('findChessboardCorners could not find corners.')
        if showCalibration:
            cv2.destroyAllWindows()
        '''Do the calibration:'''
        if not objpoints:
            print('Objpoints is none!')
        if not imgpoints:
            print('Imgpoints is none!')
        logging.info('Starting calibration with ' + str(len(imgpoints)) + ' valid frames')
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        '''Update class with latest numbers.'''
        camera_parameters = {'mtx': mtx, 'ret': ret, 'dist': dist, 'rvecs': rvecs, 'tvecs': tvecs,
                             'newcameramtx': newcameramtx, 'roi': roi}
        print('Calibration done')
        return camera_parameters
    except IndexError:
        pass#cv2.error as e:
     #   print('OpenCV failed. ')
      #  print('MSG: ', e)
       # raise FailedCalibrationException(msg=e)
    except cv2.error as e:
        print('OpenCV failed. ')
        print('MSG: ', e)
        raise FailedCalibrationException(msg=e)


def getUndistortedFrame(img, camera_parameters):
    """
    Returns an undistorted frame based on the camera matrix and distortion coefficients of this object
    :param img: Distorted frame
    :param camera_parameters: Dictionary like containing camera parameters
    :return: An undistorted frame.
    """
    camera_matrix = camera_parameters['mtx']
    dist_coeff = camera_parameters['dist']
    new_camera_matrix = camera_parameters['newcameramtx']
    roi = camera_parameters['roi']
    try:
        logging.debug('Inside undistortImage()')
        dst = cv2.undistort(img, camera_matrix, dist_coeff, None, new_camera_matrix)
        logging.debug(dst)
    except cv2.error: # Not successfull
        raise FailedCalibrationException
    if not dst.any():  # dst is empty, no calib result is found.
        raise FailedCalibrationException(msg='Failed to do cv2.undistort(). Try with new picture.')
    # crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    return dst

def videoCalibration(videoName, debug=False):
    """
    Reads a video in the calibVideos-folder and outputs a calibration called "newestCalib.npz".
    :param videoName: filename of video
    :return: Camera calibration parameters in dictionary.
    """
    video_capture = cv2.VideoCapture('calibVideos/' + videoName)
    ret, image = video_capture.read()
    frames = []
    while ret:
        frames.append(image)
        ret, image = video_capture.read()
    frames = np.array(frames)[1::6]
    if debug:
        print('Videocalibration starting with ' + str(len(frames)) + ' frames')
    return calibCam(frames, debug)