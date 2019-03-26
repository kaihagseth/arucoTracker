import csv
import logging
import threading
import time

import cv2
import numpy as np
from VisionEntityClasses.helperFunctions import rotationMatrixToEulerAngles
from VisionEntityClasses.helperFunctions import invertTransformationMatrix
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.arucoBoard import arucoBoard
from sklearn.preprocessing import normalize

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
        """
        Creates vision entities based on connected cameras.
        :return:
        """
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
                if board.getModelWrtWorld() is None and ve.getModelWrtCam() is not None:
                    print("Setting first position")
                    board.setFirstBoardPosition(ve)
                    board.isVisible = True
                    self._master_entity = ve

            # If the master cam failed to calculate a pose, another camera is set as master.
            if self._master_entity is None or self._master_entity.getModelWrtCam() is None:
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
                if ve.getCamWrtWorld() is None and ve.getModelWrtCam() is not None and self._master_entity.getModelWrtCam() is not None and ve is not \
                        self._master_entity:
                    ve.setCameraPosition(board)

            # If the master camera cannot see the board, but another calibrated camera can, the calibrated camera becomes
            # the new master camera
            for ve in self.getVisionEntityList():
                if ve.getModelWrtCam() is not None and ve.getCamWrtWorld() is not None and self._master_entity.getModelWrtCam() is None:
                    self._master_entity = ve
                    break

    def getStereoVisionPosition(self):
        """
        Generates 3D positions with regard to world origin for multiple aruco markers by using images from 2
        cameras
        :return: positions of markers 3xN numpy array and aruco marker ids 1xN numpy array
        """

        imagepoints1 = np.array([])# Image points camera 1
        imagepoints2 = np.array([])# Image points camera 2
        idlist = np.array([])
        ve = self.getVisionEntityList()
        if ve[0].getIds() is not None and ve[1].getIds() is not None:
            for i in range(len(ve[0].getIds())):
                for j in range(len(ve[1].getIds())):
                    if ve[0].getIds()[i] == ve[1].getIds()[j]:
                        imagepoints1 = np.hstack((imagepoints1, ve[0].getCorners()[i][0, 3, 0:2].reshape(-1, 1))) \
                            if imagepoints1.size else ve[0].getCorners()[i][0, 3, 0:2].reshape(-1, 1)
                        imagepoints2 = np.hstack((imagepoints2, ve[1].getCorners()[j][0, 3, 0:2].reshape(-1, 1))) \
                            if imagepoints2.size else ve[1].getCorners()[j][0, 3, 0:2].reshape(-1, 1)
                        idlist = np.hstack((idlist, ve[0].getIds()[i])) if idlist.size else \
                            ve[0].getIds()[i]

        intrinsic1 = ve[0].intrinsic_matrix
        intrinsic2 = ve[1].intrinsic_matrix

        # Calculate projection matrix for camera 1
        if ve[0].getCamWrtWorld() is not None:
            extrinsic1 = invertTransformationMatrix(ve[0].getCamWrtWorld())
            extrinsic1 = extrinsic1[0:3, :]
            projection1 = intrinsic1 * extrinsic1  # Projection matrix camera 1
        else:
            projection1 = None

        # Calculate projection matrix for camera 2
        if ve[0].getCamWrtWorld() is not None:
            extrinsic2 = invertTransformationMatrix(ve[1].getCamWrtWorld())
            extrinsic2 = extrinsic2[0:3, :]
            projection2 = intrinsic2 * extrinsic2  # Projection matrix camera 2
        else:
            projection2 = None

        if imagepoints1.size and projection1 is not None and projection2 is not None:
            positions_wrt_cam = cv2.triangulatePoints(projection1, projection2, imagepoints1, imagepoints2)

            # Remove scaling
            positions_wrt_cam[0, :] = np.divide(positions_wrt_cam[0, :], positions_wrt_cam[3, :])
            positions_wrt_cam[1, :] = np.divide(positions_wrt_cam[1, :], positions_wrt_cam[3, :])
            positions_wrt_cam[2, :] = np.divide(positions_wrt_cam[2, :], positions_wrt_cam[3, :])
            positions_wrt_cam[3, :] = np.divide(positions_wrt_cam[3, :], positions_wrt_cam[3, :])


            # Transformation from camera coordinates to world coordinates
            #cam1_wrt_world = ve[0].getCamWrtWorld()
            #hom_positions = np.zeros((4, np.size(positions_wrt_cam, 1)), dtype=float)
            #for i in range(np.size(positions_wrt_cam, 1)):
            #    hom_positions[:, i] = np.matmul(cam1_wrt_world, positions_wrt_cam[:, i])
            #
            #positions = hom_positions[0:3, :]

            # non-homogeneous coordinates
            positions = positions_wrt_cam[0:3, :]

            # TODO: This is just for testing with display, remove when no longer needed
            for i in range(np.size(idlist)):
                # Find 3DoF coord of bottom right corner of marker N
                if idlist[i] == 6: # N = 6
                    origin = positions[:, i]
                    break
                else:
                    origin = np.array([])

            # Return 3DoF positions and corresponding marker ids
            return positions, idlist, origin

        else:
            return np.array([]), np.array([]), np.array([])

    def getStereoPose(self, positions, ids):
        """
        TODO: use positions of known points on model to determine euler angles by creating 2 or more directional vectors
        :return:
        """
        m_0 = np.array([])
        m_6 = np.array([])
        m_8 = np.array([])
        for i in range(np.size(ids)):
            if ids[i] == 0:
                m_0 = positions[:, i].reshape(-1, 1)
            if ids[i] == 6:
                m_6 = positions[:, i].reshape(-1, 1)
            if ids[i] == 0:
                m_8 = positions[:, i].reshape(-1, 1)
        if m_0.size and m_6.size and m_8.size:
            vec_x = normalize(np.subtract(m_8, m_6), axis=0)
            vec_y = normalize(np.subtract(m_0, m_6), axis=0)
            vec_z = normalize(np.cross(vec_x.reshape(1, -1), vec_y.reshape(1, -1)).reshape(-1, 1), axis=0)

            #model_wrt_world = self._arucoBoards[0].getModelWrtWorld()[0:3, 0:3]
            rot = np.matrix(np.zeros((3, 3)))
            rot[:, 0] = np.asmatrix(vec_x)
            rot[:, 1] = np.asmatrix(vec_y)
            rot[:, 2] = np.asmatrix(vec_z)

            euler = np.rad2deg(rotationMatrixToEulerAngles(rot))

            return euler
        else:
            return np.array([])



    def getEulerPoses(self):
        """
        Returns poses from all boards. list of tuples of tuple Nx2x3
        :return:list of tuples of tuple Nx2x3 Board - tvec(x, y, z)mm - evec(roll, yaw, pitch)deg
        """
        poses = []
        for board in self._arucoBoards:
            try:
                #tvec = np.array(board.getTvec(), dtype=int)
                #evec = np.rad2deg(rotationMatrixToEulerAngles(toMatrix(board.getRvec()))).astype(int)
                T = board.getModelWrtWorld()
                tvec = np.asarray(T[0:3,3]).reshape(-1).astype(int)
                evec = np.rad2deg(rotationMatrixToEulerAngles(T[0:3, 0:3])).reshape(-1).astype(int)
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
            if ve.getModelWrtCam is not None and ve.getCamWrtWorld is not None:
                return ve
        return None

    def getPosePreviewImg(self):
        """
        Returns a pose preview image from master camera. If no master camera is present, returns a frame from camera on
        index 0.
        :return: Frame drawn with axis cross, corners, and poses
        """

        if self._master_entity is not None and self._master_entity.getCorners() is not None and\
                self._master_entity.getModelWrtCam() is not None:
            out_frame = self._master_entity.drawAxis()
            e = self.getEulerPoses()
            cv2.putText(out_frame, str(e[0]), (10, 100), cv2.FONT_HERSHEY_SIMPLEX, .6,
                        (0, 0, 255), 2)
            positions, ids, origo = self.getStereoVisionPosition()
            euler = self.getStereoPose(positions, ids)
            pose = np.hstack((origo, euler))
            if pose is not None:
                cv2.putText(out_frame, str(pose.astype(int)), (10, 200), cv2.FONT_HERSHEY_SIMPLEX, .6,
                            (0, 0, 255), 2)
            ret = True
        else:
            out_frame = self.getVisionEntityList()[0].getFrame()
            ret = True

        cv2.imshow('demo', out_frame)
        cv2.waitKey(1)
        return ret, out_frame

    def stopThreads(self):
        """
        Sets stop flag for all threads in order to terminate program safely.
        :return:
        """
        for VE in self.getVisionEntityList():
            VE.runThread = False

