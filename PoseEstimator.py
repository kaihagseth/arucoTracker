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
    QTHRESHOLD = 0.8  # How good the quality of the first frame has to be in order to be set as the first camera
    def __init__(self):
        self.VisionEntityList = []  # List for holding VEs
        self.threadInfoList = []  # List for reading results from VEs.
        self._writer = None
        self._log_start_time = None
        self._arucoBoards = dict()  # List of aruco boards to track.
        self.worldCoordinatesIsSet = False
        self.merger = None
        self.imageDisplayFX = None # Function used to display image frame
        self.autoTracking = False # Tells if autotracking is active or not.
        self.trackedBoardIndex = None # Tells which board is being tracked.
        self.qualityDisplayFX = None # Function used to display quality of a chosen board
        self.poseDisplayFX = None # Function used to display pose of a chosen board
        self.logging = False
        self.running = False
        self.runThread = False

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

    def initialize(self, imageDisplayFX=None, poseDisplayFX=None, qualityDisplayFX=None):
        '''
        Start Vision Entity threads for pose estimation.
        :return: None
        '''
        logging.debug('Initializing pose estimator')
        self.imageDisplayFX = imageDisplayFX
        self.poseDisplayFX = poseDisplayFX
        self.qualityDisplayFX = qualityDisplayFX
        self.runThread = True
        for VE in self.VisionEntityList:
            VE.runThread = True
            th = threading.Thread(target=VE.runThreadedLoop, args=[self.dictionary, self._arucoBoards], daemon=True)
            th.start()
            logging.debug('Vision entity created.')
        th = threading.Thread(target=self.runPoseEstimationLoop)
        th.start()

    def runPoseEstimationLoop(self):
        self.running = True
        while self.runThread:
            self.updateBoardPoses()
            if self.poseDisplayFX:
                self.displayPose()
            if self.qualityDisplayFX:
                self.displayQuality()
            if self.logging:
                self.writeCsvLog()
            if self.autoTracking:
                self.autoTrack()

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
        # TODO: rewrite to accommodate for more than one pose!!
        # FIXME: This function is not working as intended.
        :param tvec: Translation vector. Numpy array with x y and z-coordinates to log.
        :param evec: Euler rotation vector.  Numpy array with roll, pitch and yaw to log.
        :return: None
        """
        if poses:
            for pose in poses.values():
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
        logging.info("Length of VE-list: "+ str(len(self.VisionEntityList)))
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
        for board in self._arucoBoards.values():
            for ve in self.getVisionEntityList():
                # Collecting frame and detecting markers for each camera
                if (not self.worldCoordinatesIsSet) and ve.getDetectionQuality()[board.ID] >= self.QTHRESHOLD:
                    self.worldCoordinatesIsSet = True
                    board.setFirstBoardPosition(ve)
                    board.setTrackingEntity(ve)
            board.setTrackingEntity(self.chooseMasterCam(board))
            tracking_entity = board.getTrackingEntity()
            if tracking_entity:
                te_poses = copy.copy(tracking_entity.getPoses())
                board.updateBoardPose(te_poses[board.ID])
            else:
                board.updateBoardPose(None)
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

    def getEulerPose(self, boardID):
        """
        Returns a pose expressed in translation and euler angles from selected board.
        :return:list of tuples of tuple 2x3 Board - tvec(x, y, z)mm - evec(roll, yaw, pitch)deg
        """
        board = self.getBoards()[boardID]
        try:
            rvec, tvec = board.getRvecTvec()
            tvec = tvec.astype(float).reshape(-1)
            evec = np.rad2deg(rotationMatrixToEulerAngles(board.getTransformationMatrix())).astype(float)
        except (TypeError, AttributeError):
            tvec = None
            evec = None
        pose = evec, tvec
        return pose

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

    def getBoardPositionQuality(self, boardIndex):
        '''
        Get the quality/reliability, of the pose estimation of given board.
        :param boardIndex: Board to select
        :return: Quality, number between 0 and 1, where 1 is complete accurate pose.
        '''
        boards = self.getBoards()
        board = boards[boardIndex]
        quality = board.getPoseQuality()
        return quality

    def stopPoseEstimation(self):
        """
        Stops the pose estimator
        :return:
        """
        self.runThread = False
        self.stopThreads()
        ves = self.getVisionEntityList()
        while True in veStatuses:
            veStatuses = [ve.running for ve in ves]
        self.running = False

    def stopThreads(self):
        """
        Sets stop flag for all threads in order to terminate program safely.
        :return:
        """
        for VE in self.getVisionEntityList():
            VE.runThread = False

    def addBoard(self, board):
        """
        Adds a board to the tracking list.
        :param board: arucoboard to track
        :return: None
        """
        logging.debug("Attempting to add board to vision entities")
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
        logging.debug("Attempting to remove board from vision entities")
        key = board.ID
        del self._arucoBoards[key]
        for ve in self.getVisionEntityList():
            ve.removeBoard(board)
            logging.debug("Board removed")

    def getBoards(self):
        """
        returns list of aruco boards
        :return: list of arucoboards
        """
        return self._arucoBoards

    def startMerge(self, main_board_index, sub_boards_indeces, qualityDisplayFX, imageDisplayFX):
        """
        Starts a merger that will merge several arucoboards to one.
        :param main_board: The main board will be the reference the sub boards are connected to.
        :param sub_boards: The boards that will be merged into the main board.
        :return: None
        """
        main_board = self.getBoards()[main_board_index]
        self.routeDisplayFunction(imageDisplayFX)
        sub_boards = []
        for index in sub_boards_indeces:
            sub_boards.append(self.getBoards()[index])
        self.merger = Merger(self.dictionary, main_board, sub_boards)
        self.merger.startMerge()
        self.merger.setDisplayFunction(qualityDisplayFX)

    def finishMerge(self):
        """
        Finishes the merge process. The main and sub boards will be replaced with the merged board, and this board will
        be tracked by this pose estimator in.
        :param merger: The merger that should be finished.
        :param index: The index of the merger that should be finished.
        :return: None
        """
        print("Finishing merge in pose estimator")
        assert not self.merger is None or not self.merger.running, "Attempted to finish merge while no merger was running"
        self.merger.finishMerge()
        merger_boards = self.merger.getBoards()
        boardsToRemove = [merger_boards["main_board"]] + merger_boards["sub_boards"]
        for board in boardsToRemove:
            self.removeBoard(board)
        newBoard = merger_boards["merged_board"]
        self.addBoard(newBoard)

    def getMergerStatus(self):
        """
        Returns a list of the link quality for each sub board.
        :param mergerID: the ID of the requested merger.
        :return:
        """
        return self.merger.getQualityList()

    def getMergerBoards(self):
        """
        Returns all used boards from the merger.
        :return:
        """
        if self.merger is None:
            return None
        else:
            return self.merger.getBoards()

    def setPoseDisplayFunction(self, poseDisplayFX):
        """
        Sets a function in this class that displays the selected boards pose
        :return: None
        """
        self.poseDisplayFX = poseDisplayFX

    def autoTrack(self):
        """
        Selects a route for the display function based on a selected board and this boards tracking entity.
        :return: None
        """
        board = self.getBoards()[self.trackedBoardIndex]
        ve = board.getTrackingEntity()
        if ve is not None:
            self.routeDisplayFunction(ve.getCameraID)

    def routeDisplayFunction(self, cameraIndex):
        """
        Routes a display function to a vision entity
        :param cameraIndex: Index of vision entity to route function to.
        :param displayFX: Display function to route.
        :return: None
        """
        for ve in self.getVisionEntityList():
            ve.setDisplayFunction(None)
        self.getVEById(cameraIndex).setDisplayFunction(self.imageDisplayFX)

    def displayPose(self):
        """
        Displays a pose in the selected pose display function
        :return: None
        """
        self.poseDisplayFX(self.getEulerPose(self.trackedBoardIndex))

    def displayQuality(self):
        """
        Displays quality of pose for the selected board.
        :return: None
        """
        self.qualityDisplayFX(self.getBoards()[self.trackedBoardIndex].getPoseQuality())

    def setAutoTracker(self, autoTrackingStatus):
        """
        Sets the auto tracking status for this pose estimator
        :param autoTrackingStatus: Boolean describing of autotracking is active or not.
        :return: None
        """
        self.autoTracking = autoTrackingStatus