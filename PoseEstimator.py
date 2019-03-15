import csv
import logging
import queue
import threading
import time

import cv2
import numpy as np
from VisionEntityClasses.helperFunctions import rotationMatrixToEulerAngles
from VisionEntityClasses.helperFunctions import toMatrix
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.arucoBoard import arucoBoard

class PoseEstimator():
    """
    Collect pose and info from all cameras, and find the best estimated pose possible.
    """
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    def __init__(self):
        self.VisionEntityList = []  # List for holding VEs
        self.threadInfoList = []  # List for reading results from VEs.
        self._writer = None
        self._log_start_time = None
        self._arucoBoards = []  # List of aruco boards to track.
        self.createArucoBoard(3, 3, 40, 5)
        self._master_entity = None

    def createArucoBoard(self, board_width, board_height, marker_size, marker_gap):
        """
        Adds an aruco board to track
        :param board_width: Width of board
        :param board_height: Height of board
        :param marker_size: Size of each marker in mm
        :param marker_gap: Gap between each marker in mm
        :return:
        """
        self._arucoBoards.append(arucoBoard(board_width, board_height, marker_size, marker_gap))

    def createVisionEntities(self):
        cam_list = self.findConnectedCamIndexes()
        for cam_index in cam_list:
            VE = VisionEntity(cam_index)
            self.VisionEntityList.append(VE)
        return cam_list

    def findConnectedCamIndexes(self, wantedCams=None):
        '''
        Find all cams connected to system.  
        :return: 
        '''  # TODO: Find new algorithm, this thing is sloooow.
        #return [1] #A hack
        if wantedCams is None:
            unwantedCams = [2,3,4]  # Index of the webcam we dont want to use, if any.
        else: # Wanted cams specified in GUI.
            pass
        logging.info('Inside findConnectedCams()')
        #logging.info('Using a hack. Hardcoded index list in return.')
        num_cams = 5
        ilist = []
        for i in range(num_cams):
            if i not in unwantedCams:
                ilist.append(i)
                msg = 'Webcam on index {0} included.'.format(i)
                logging.info(msg)
            else:
                msg = 'Webcam on index {0} not included.'.format(i)
                logging.info(msg)
        return ilist

    def runPoseEstimator(self):
        '''
        Do poseestimation for every VisionEntity.
        Start threads for every VE. Save the pose in a thread-safe variable, and add it all to a list.
        :return: None
        '''
        logging.info('Starting runPoseEstimator()')
        for VE in self.VisionEntityList:
            print('VE start')
            singlecam_curr_pose = [0.0,0.0,0.0],[0.0,0.0,0.0]
            #Create a thread-safe variable to save pose to.
            singlecam_curr_pose_que = queue.LifoQueue() # LifoQueue because last written variable is most relevant.
            singlecam_curr_pose_que.put(singlecam_curr_pose)
            frame_que = queue.LifoQueue(maxsize=1) # Thread-safe variable for passing cam frames to GUI.
            logging.debug('Passing queue.Queue()')
            # Create thread, with target findPoseResult(). All are daemon-threads.
            th = threading.Thread(target=VE.runThreadedLoop, args=[self.dictionary, self._arucoBoards], daemon=True)
            logging.debug('Passing thread creation.')
            self.threadInfoList.append([VE, th, singlecam_curr_pose_que, frame_que])
            print()
            print('ThreadInfoList: ', self.threadInfoList)
            th.start()

    def removeVEFromListByIndex(self, index):
        '''
        Remove the camera given by index from list of VEs.
        :param index: Index of VE cam
        :return:
        '''
        VE = self.getVEById(index)
        self.VisionEntityList.remove(VE)

    def writeCsvLog(self, tvec, evec):
        """
        Writes a row to the logging csv-file. Overwrites previous file if a new session is started.
        :param tvec: Translation vector. Numpy array with x y and z-coordinates to log.
        :param evec: Euler rotation vector.  Numpy array with roll, pitch and yaw to log.
        :return: None
        """
        if tvec is None:
            tvec = ['-', '-', '-']
        if evec is None:
            evec = ['-', '-', '-']
        if not self._writer:
            with open('logs/position_log.csv', 'w') as csv_file:
                fieldnames = ['x', 'y', 'z', 'roll', 'pitch', 'yaw', 'time']
                self._log_start_time = time.time()
                self._writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', dialect='excel')
                self._writer.writerow(fieldnames)
                self._writer.writerow([tvec[0], tvec[1], tvec[2], evec[0], evec[1], evec[2],
                                       (time.time() - self._log_start_time)])
        else:
            with open('logs/position_log.csv', 'a') as csv_file:
                self._writer = csv.writer(csv_file, delimiter=',', lineterminator='\n',  dialect='excel')
                self._writer.writerow([tvec[0], tvec[1], tvec[2], evec[0], evec[1], evec[2],
                                       (time.time() - self._log_start_time)])

    def getVEById(self, camID):
        """
        :param camID: OpenCV camera ID
        :return: Vision entity to be returned.
        """
        for VE in self.VisionEntityList:
            cam = VE.getCam()
            if cam._src is camID:
                wantedVE = VE
                return wantedVE
        # If not found, log error.
        logging.error('Camera not found on given index, VE returned None. ')

    def getVisionEntityList(self):
        return self.VisionEntityList

    def updateBoardPoses(self):
        """
        Writes a new pose to each board in board list.
        :return: None
        """
        print("updateboardPoses running")
        for board in self._arucoBoards:
            print("board found")
            board.isVisible = False
            for ve in self.getVisionEntityList():
                ve.grabFrame()
            for ve in self.getVisionEntityList():
                # Collecting frame and detecting markers for each camera.
                if board.getRvec() is None and ve.Mrvec is not None:
                    print("Setting first position")
                    board.setFirstBoardPosition(ve)
                    board.isVisible = True
                    self._master_entity = ve

            # If the master cam failed to calculate a pose, another camera is set as master.
            if self._master_entity is None or self._master_entity.Mrvec is None:
                self._master_entity = self.findNewMasterCam()
                continue
            else:
                # Update board position if the board is masterCams frame
                board.updateBoardPosition(self._master_entity)
                outFrame = self._master_entity.getFrame()

            # Set camera world positions if they are not already set and both the camera and the master camera can see the frame
            for ve in self.getVisionEntityList():
                if self._master_entity is None:
                    break
                if ve.Crvec is None and ve.Mrvec is not None and self._master_entity.Mrvec is not None and ve is not \
                        self._master_entity:
                    ve.setCameraPosition(board)

            # If the master camera cannot see the board, but another calibrated camera can, the calibrated camera becomes
            # the new master camera
            for ve in self.getVisionEntityList():
                if ve.Mrvec is not None and ve.Crvec is not None and self._master_entity.Mrvec is None:
                    self._master_entity = ve
                    break

    def getEulerPoses(self):
        """
        Returns poses from all boards. list of tuples of tuple Nx2x3
        :return:list of tuples of tuple Nx2x3 Board - tvec(x, y, z)mm - evec(roll, yaw, pitch)deg
        """
        poses = []
        for board in self._arucoBoards:
            try:
                tvec = np.array(board.getTvec(), dtype=int)
                evec = np.rad2deg(rotationMatrixToEulerAngles(toMatrix(board.getRvec()))).astype(int)
            except TypeError:
                tvec = None
                evec = None
            pose = tvec, evec
            poses.append(pose)
        return poses


    def findNewMasterCam(self):
        """
        Sets the master cam to a camera that is calibrated and has the board in sight.
        :param cams:
        :return: master cam
        """
        for ve in self.getVisionEntityList():
            if ve.Mrvec is not None and ve.Crvec is not None:
                return ve
        return None

    def getPosePreviewImg(self):
        """
        Returns a pose preview image from master camera.
        :return: Frame drawn with axis cross, corners, and poses
        """
        if self._master_entity is not None and self._master_entity.corners is not None and\
                self._master_entity.Mrvec is not None:
            ret, out_frame = self._master_entity.retrieveFrame()
            out_frame = cv2.aruco.drawDetectedMarkers(out_frame, self._master_entity.corners, self._master_entity.ids)
            out_frame = self._master_entity.drawAxis(out_frame)
        else:
            out_frame = self.getVisionEntityList()[0].getFrame()
            ret = True
        if ret:
            cv2.imshow('test', out_frame)
            cv2.waitKey(1)
        return ret, out_frame
