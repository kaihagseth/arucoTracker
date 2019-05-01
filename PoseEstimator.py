import threading, queue, logging
import time
import csv
import inspect
import logging
import threading
import time
import copy

import cv2
import numpy as np
from VisionEntityClasses.helperFunctions import rotationMatrixToEulerAngles
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.ArucoBoard import ArucoBoard
from VisionEntityClasses.arucoBoardMerger import Merger
import inspect
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
        self._arucoBoards = dict()  # List of aruco boards to track.

        self.worldCoordinatesIsSet = False
        self.merger = None

    def createArucoBoard(self, board_width, board_height, marker_size, marker_gap):
        """
        Adds an aruco board to track
        :param board_width: Width of board
        :param board_height: Height of board
        :param marker_size: Size of each marker in mm
        :param marker_gap: Gap between each marker in mm
        :return:
        """
        board = ArucoBoard(board_width=board_width, board_height=board_height, marker_size=marker_size,
                           marker_gap=marker_gap)
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

    def setVisionEntityList(self, VElist):
        """
        Add VEs to the VisionEntityList.
        :param VElist: List of new VEs to add to PoseEstimator.
        :return: None
        """
        for VE in VElist:
            if VE not in self.VisionEntityList: # Don't add double
                VE.addBoards(self.getBoards())
                self.VisionEntityList.append(VE)
                logging.info("VE with camsource "+str(VE.getCam().getSrc())+" added.")
            else:
                logging.info("Duplicate found! VE with camera index " + str(VE.getCam().getSrc())+" is duplicated and not added.")

    def findConnectedCamIndexes(self, wantedCamIndexes=([0])):
        '''
        Find all cams connected to system.  
        :return: List of indexes of wanted cameras.
        '''  # TODO: Find new algorithm, this thing is sloooow.
        for i in wantedCamIndexes:
                msg = 'Webcam on index {0} included.'.format(i)
                logging.info(msg)
        return wantedCamIndexes

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

    def resetExtrinsicMatrices(self):
        '''
        Create a new starterpoint for pose estimation.

        :return: None
        '''
        for VE in self.VisionEntityList:
            VE.resetExtrinsicMatrix()

    def getVEById(self, camID):
        """
        :param camID: OpenCV camera ID
        :return: Vision entity to be returned.
        """
        print("Print in 'getVEbyID': Length of VE-list: "+ str(len(self.VisionEntityList)))
        for VE in self.VisionEntityList:
            cam = VE.getCam()
            if cam._src is camID:
                wantedVE = VE
                return wantedVE
        # If not found, log error.
        logging.error('Camera not found on given index: '+str(camID)+', VE returned None. Parent caller: ' + str(inspect.stack()[2][3]))

    def getVisionEntityList(self):
        """
        Returns list of all Vision entities.
        :return:
        """
        return self.VisionEntityList

    def getVisionEntityIndexes(self):
        """
        Returns a list of all camera IDs of Vision Entities.
        :return: List of all indexes of Vision entities.
        """
        indexList = []
        for ve in self.getVisionEntityList():
            indexList.append(ve.getCameraID())
        return indexList

    def updateBoardPoses(self):
        """
        Writes a new pose to each board in board list.
        :return: None
        """
        for _, board in self._arucoBoards.items():
            for ve in self.getVisionEntityList():
                # Collecting frame and detecting markers for each camera
                poses = ve.getPoses()
                model_pose = poses[board.ID]
                # Idea: Set a flag in pose estimator when the first board is detected.
                if (not self.worldCoordinatesIsSet) and ve.getDetectionQuality()[board.ID] >= self.QTHRESHOLD:
                    self.worldCoordinatesIsSet = True
                    board.setFirstBoardPosition(ve)
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
                    potentialCameraPoseQuality = ve.calculatePotentialCameraPoseQuality(board)
                    if potentialCameraPoseQuality > currentCameraPoseQuality:
                        ve.setCameraPose(board)
                        ve.setCameraPoseQuality(potentialCameraPoseQuality)

    def getEulerPoses(self):
        """
        Returns poses from all boards. list of tuples of tuple Nx2x3
        :return:list of tuples of tuple Nx2x3 Board - tvec(x, y, z)mm - evec(roll, yaw, pitch)deg
        """
        poses = []
        logging.debug("Length of aruco list: " +str(len(self._arucoBoards)))
        for board in self._arucoBoards.values():
            try:
                rvec, tvec = board.getRvecTvec()
                tvec = tvec.astype(float).reshape(-1)
                evec = np.rad2deg(rotationMatrixToEulerAngles(board.getTransformationMatrix())).astype(float)
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

    def getPosePreviewImg(self, cameraIndex, boardIndex, autoTrack):
        """
        Returns a pose preview image from master camera. If no master camera is present, returns a frame from camera on
        index 0.
        :param autoTrack Bool that decides if auto tracking is active.
        :param ID. The ID of the board to track, or the cam to use.
        :return: Frame drawn with axis cross, corners, and poses
        """
        if autoTrack:
            boards = self.getBoards()
            board = boards[boardIndex]
            tracking_entity = board.getTrackingEntity()
            if tracking_entity is None:
                logging.debug("Tracking entity is none, asking to first vision entity in vision entity list. ")
                vision_entity = copy.copy(self.getVisionEntityList()[0])
            else:
                vision_entity = copy.copy(tracking_entity)
        else:
            vision_entity = self.getVEById(cameraIndex)

        if vision_entity is not None and vision_entity.getCornerDetectionAttributes()[0] is not None and\
                vision_entity.getPoses() is not None:
            out_frame = vision_entity.drawAxis()
        else:
            if vision_entity is None:
                out_frame = self.getVisionEntityList()[0].getFrame()
            else:
                out_frame = vision_entity.getFrame()
        return out_frame

    def getCameraPositionQuality(self, camID=-1):
        '''
        Get the quality/reliability , of the pose of a cam from world origo.
        :param camID: Cam to select
        :return: Quality, number between 0 and 1, where 1 is complete accurate pose.
        '''
        if camID == -1:
            #If no master camera is present, select first index.
            if self._master_entity is None:
                vision_entity = copy.copy(self.getVEById(0))
            else:
                vision_entity = copy.copy(self._master_entity)
        else:
            logging.error("CamID: " + str(camID))
            vision_entity = self.getVEById(camID)
        quality = vision_entity.getCameraPoseQuality()
        return quality

    def getBoardPositionQuality(self, boardIndex=0):
        '''
        Get the quality/reliability, of the pose estimation of given board.
        :param boardIndex: Board to select
        :return: Quality, number between 0 and 1, where 1 is complete accurate pose.
        '''
        board = self._arucoBoards[boardIndex]
        quality = board.getPoseQuality()
        return quality

    def getBoardPositionQualityWrtCam(self, boardIndex=0, camID=-1):
        ''' TEST FUNCTION YET
        Get the quality/reliability, of the pose estimation of given board, from a desired camera.
        :param boardIndex: Board to select
        :return: Quality, number between 0 and 1, where 1 is complete accurate pose.
        '''
        #Find cam
        if camID == -1:
            #If no master camera is present, select first index.
            if self._master_entity is None:
                vision_entity = copy.copy(self.getVEById(0))
            else:
                vision_entity = copy.copy(self._master_entity)
        else:
            vision_entity = self.getVEById(camID)
        board = self._arucoBoards[boardIndex]
        quality = board.getPoseQuality()
        return quality

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
        #self.VisionEntityList = []

    def addBoard(self, board):
        """
        Adds a board to the tracking list.
        :param board: arucoboard to track
        :return: None
        """
        logging.debug("attempting to add board to vision entities")
        key = board.ID
        self._arucoBoards[key] = board
        for ve in self.getVisionEntityList():
            ve.addBoards(board)
            logging.debug("Board with id "+ str(key) + " added to vision entity")

    def removeBoard(self, board):
        """
        Removes a board from the tracking list.
        :param board: The board to be removed
        :return: None
        """
        logging.debug("attempting to remove board from vision entities")
        key = board.ID
        del self._arucoBoards[key]
        for ve in self.getVisionEntityList():
            ve.removeBoard(board)
            logging.debug("board added to vision entity")

    def getBoards(self):
        """
        returns list of aruco boards
        :return: list of arucoboards
        """
        return self._arucoBoards

    def startMerge(self, main_board_index, sub_boards_indeces, displayFx):
        """
        Starts a merger that will merge several arucoboards to one.
        :param main_board: The main board will be the reference the sub boards are connected to.
        :param sub_boards: The boards that will be merged into the main board.
        :return: None
        """
        main_board = self.getBoards()[main_board_index]
        sub_boards = []
        for index in sub_boards_indeces:
            sub_boards.append(self.getBoards()[index])
        self.merger = Merger(self.dictionary, main_board, sub_boards)
        self.merger.startMerge()
        self.merger.setDisplayFunction(displayFx)

    def finishMerge(self):
        """
        Finishes the merge process. The main and sub boards will be replaced with the merged board, and this board will
        be tracked by this pose estimator in.
        :param merger: The merger that should be finished.
        :param index: The index of the merger that should be finished.
        :return: None
        """
        if self.merger is None:
            logging.error("Attempted to finish merge while no merger was running")
        newBoard = self.merger.finishMerge()
        boardsToRemove = self.merger.getBoards()
        for ve in self.getVisionEntityList():
            for board in boardsToRemove:
                ve.removeBoard(board)
            ve.addBoards(newBoard)
        self.merger = None

    def getMergerStatus(self):
        """
        Returns a list of the link quality for each sub board.
        :param mergerID: the ID of the requested merger.
        :return:
        """
        return self.merger.getQualityList()
