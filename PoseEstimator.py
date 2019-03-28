import csv
import logging
import threading
import time
import copy

import cv2
import numpy as np
from VisionEntityClasses.helperFunctions import rotationMatrixToEulerAngles
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.arucoBoard import arucoBoard

class PoseEstimator():
    """
    Collect pose and info from all cameras, and find the best estimated pose possible.
    """
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    QTHRESHOLD = 1  # How good the quality of the first frame has to be in order to be set as the first camera
    def __init__(self):
        self.VisionEntityList = []  # List for holding VEs
        self.threadInfoList = []  # List for reading results from VEs.
        self._writer = None
        self._log_start_time = None
        self._arucoBoards = []  # List of aruco boards to track.
        self.createArucoBoard(3, 3, 40, 5)
        self.worldCoordinatesIsSet = False

    def createArucoBoard(self, board_width, board_height, marker_size, marker_gap):
        """
        Adds an aruco board to track
        :param board_width: Width of board
        :param board_height: Height of board
        :param marker_size: Size of each marker in mm
        :param marker_gap: Gap between each marker in mm
        :return:
        """
        board = arucoBoard(board_width, board_height, marker_size, marker_gap)
        self.addBoard(board)

    def createVisionEntities(self):
        """
        Creates vision entities based on connected cameras.
        :return:
        """
        cam_list = self.findConnectedCamIndexes()
        for cam_index in cam_list:
            VE = VisionEntity(cam_index)
            self.VisionEntityList.append(VE)
            VE.addBoards(self.getBoards())
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
        Start Vision Entity threads for pose estimation.
        :return: None
        '''
        logging.info('Starting runPoseEstimator()')
        for VE in self.VisionEntityList:
            print('VE start')
            VE.runThread = True
            th = threading.Thread(target=VE.runThreadedLoop, args=[self.dictionary, self._arucoBoards], daemon=True)
            logging.debug('Passing thread creation.')
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

    def writeCsvLog(self, poses):
        """
        Writes a row to the logging csv-file. Overwrites previous file if a new session is started.
        #TODO: rewrite to accommodate for more than one pose
        :param tvec: Translation vector. Numpy array with x y and z-coordinates to log.
        :param evec: Euler rotation vector.  Numpy array with roll, pitch and yaw to log.
        :return: None
        """
        if poses:
            for pose in poses:
                evec, tvec = pose
        else:
            evec, tvec = None, None
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
        for board in self._arucoBoards:
            for ve in self.getVisionEntityList():
                # Collecting frame and detecting markers for each camera
                model_pose = ve.getPoses()[board.ID]
                # Idea: Set a flag in pose estimator when the first board is detected.
                if not self.worldCoordinatesIsSet and model_pose is not None:
                    self.worldCoordinatesIsSet = board.setFirstBoardPosition(ve, self.QTHRESHOLD)
                    board.setTrackingEntity(ve)

            board.setTrackingEntity(self.chooseMasterCam(board))
            tracking_entity = board.getTrackingEntity()
            if tracking_entity is not None and tracking_entity.getPoses() is not None:
                board.updateBoardPose()
            # Set camera world positions if they are not already set and both the camera and the master camera can see the frame
            for ve in self.getVisionEntityList():
                if tracking_entity is None:
                    break
                if ve.getPoses() is not None and tracking_entity.getPoses() is not None:
                    currentCameraPoseQuality = ve.getCameraPoseQuality()
                    potentialCameraPoseQuality = ve.getDetectionQuality()[board.ID] * board.getPoseQuality()
                    if potentialCameraPoseQuality > currentCameraPoseQuality:
                        ve.setCameraPose(board, 0)

    def getEulerPoses(self):
        """
        Returns poses from all boards. list of tuples of tuple Nx2x3
        :return:list of tuples of tuple Nx2x3 Board - tvec(x, y, z)mm - evec(roll, yaw, pitch)deg
        """
        poses = []
        for board in self._arucoBoards:
            try:
                rvec, tvec = board.getRvecTvec()
                tvec = tvec.astype(int).reshape(-1)
                evec = np.rad2deg(rotationMatrixToEulerAngles(board.getTransformationMatrix())).astype(int)
            except (TypeError, AttributeError):
                tvec = None
                evec = None
            pose = evec, tvec
            poses.append(pose)
        return poses


    def chooseMasterCam(self, board):
        """
        Chooses a master vision entity based on the potential board positional quality they can deliver
        :return: master cam
        """
        highest_potential_board_quality = 0
        master_ve = None
        for ve in self.getVisionEntityList():
            potential_board_quality = ve.getCameraPoseQuality() * ve.getDetectionQuality()[board.ID]
            if potential_board_quality > highest_potential_board_quality:
                highest_potential_board_quality = potential_board_quality
                master_ve = ve
        return master_ve

    def getPosePreviewImg(self, ID, autoTrack):
        """
        Returns a pose preview image from master camera. If no master camera is present, returns a frame from camera on
        index 0.
        :param autoTrack Bool that decides if auto tracking is active.
        :param ID. The ID of the board to track, or the cam to use.
        :return: Frame drawn with axis cross, corners, and poses
        """
        if autoTrack:
            print("Autotrack active, tracking board: " + str(ID))
            boards = self.getBoards()
            board = boards[ID]
            tracking_entity = board.getTrackingEntity()
            if tracking_entity is None:
                vision_entity = copy.copy(self.getVEById(0))
            else:
                vision_entity = copy.copy(tracking_entity)
        else:
            print("Autotrack not active, showing cam: " + str(ID))
            vision_entity = self.getVEById(ID)

        if vision_entity is not None and vision_entity.getCornerDetectionAttributes()[0] is not None and\
                vision_entity.getPoses() is not None:
            out_frame = vision_entity.drawAxis()
            board = self._arucoBoards[0]
            bp_string = "{0:.2f}".format(board.getPoseQuality())
            cv2.putText(out_frame, "Quality: " + bp_string, (15, 15), cv2.FONT_HERSHEY_SIMPLEX, .6,
                        (0, 0, 255), 2)
        else:
            if vision_entity is None:
                out_frame = self.getVEById(0).getFrame()
            else:
                out_frame = vision_entity.getFrame()
        return out_frame

    def getRawPreviewImage(self, camID):
        '''
        Get a raw, unfiltered image from the camera on selected ID.
        :return: Raw, unfiltered image. Return None if unsuccessful, or camera used elsewhere.
        '''
        VE = self.getVEById(camID)
        frame = VE.getFrame()
        return frame

    def stopThreads(self):
        """
        Sets stop flag for all threads in order to terminate program safely.
        :return:
        """
        for VE in self.getVisionEntityList():
            VE.runThread = False
        self.VisionEntityList = []

    def addBoard(self, board):
        """
        Adds a board to the tracking list.
        :param board: arucoboard to track
        :return: None
        """
        logging.debug("attempting to add board to vision entities")
        index = len(self._arucoBoards)
        board.ID = index
        self._arucoBoards.append(board)
        for ve in self.getVisionEntityList():
            ve.addBoards(board)
            logging.debug("board added to vision entity")

    def getBoards(self):
        """
        returns list of aruco boards
        :return: list of arucoboards
        """
        return self._arucoBoards