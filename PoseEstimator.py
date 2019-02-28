from SingleCameraPoseEstimator import SingleCameraPoseEstimator
import threading, queue, logging
import time
import csv
from VisionEntity import VisionEntity


class PoseEstimator():
    """
    # TODO: This class will control a collection of vision entities, and will take over most jobs of today's camera
    # TODO: group class
    Collect pose and info from all cameras, and find the best estimated pose possible.
    """

    def __init__(self):
        self.VisionEntityList = [] # List for holding VEs
        self.threadInfoList = [] # List for reading results from VEs.
        self._writer = None

    def createVisionEntities(self):
        cam_list = self.findConnectedCamIndexes()
        for cam_index in cam_list:
            VE = VisionEntity(cam_index, 3, 3, 50, 5)
            self.VisionEntityList.append(VE)

    def findConnectedCamIndexes(self):
        '''
        Find all cams connected to system.  
        :return: 
        '''  # TODO: Find new algorithm, this thing is sloooow.
        #return [1] #A hack
        unwantedCams = [0,2,3,4]  # Index of the webcam we dont want to use, if any.
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
            singlecam_curr_pose_que = queue.Queue()
            singlecam_curr_pose_que.put(singlecam_curr_pose)
            logging.debug('Passing queue.Queue()')
            # Create thread, with target findPoseResult(). All are daemon-threads.
            th = threading.Thread(target=VE.runThreadedLoop, args=[singlecam_curr_pose, singlecam_curr_pose_que], daemon=True)
            logging.debug('Passing thread creation.')
            self.threadInfoList.append([VE, th, singlecam_curr_pose_que])
            print()
            print('ThreadInfoList: ', self.threadInfoList)
            th.start()

    def collectPoses(self):
        '''
        Get all output from the poseestimation here.
        If only single cam used, return tuple with tvec and rvec.
        Solution for multiple cams not implemented.
        :return: tvec, rvec (single cam)
        '''
        time.sleep(0.02)
        try:
            useSingleCam = True
            if useSingleCam is True:
                poseque = self.threadInfoList[0][2]  # Get list of the threadsafe variables
                pose = poseque.get()
                tvec, rvec = pose[0], pose[1]
                return rvec, tvec
            else:
                posequelist = self.threadInfoList[:][2]  # Get list of the threadsafe variables
                poselist = []
                # Create list for poses
                for poseque in posequelist:
                    poselist.append(poseque.get())
                return poselist
        except IndexError as e:
            logging.error(str(e))
            return []
        except TypeError as e:
            logging.error(str(e))
            return []

    def getCamById(self, camID):
        for VE in self.VisionEntityList:
            cam = VE.getCam()
            if cam._src is camID:
                wantedCam = cam
                return wantedCam
        # If not found, log error.
        logging.error('Camera not found on given index. ')

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
        if not self._writer:
            with open('position_log.csv', 'w') as csv_file:
                fieldnames = ['x', 'y', 'z', 'roll', 'pitch', 'yaw']
                self._writer = csv.writer(csv_file, delimiter=',', lineterminator='\n', dialect='excel')
                self._writer.writerow(fieldnames)
                self._writer.writerow([tvec[0], tvec[1], tvec[2], evec[0], evec[1], evec[2]])
        else:
            with open('position_log.csv', 'a') as csv_file:
                self._writer = csv.writer(csv_file, delimiter=',', lineterminator='\n',  dialect='excel')

                self._writer.writerow([tvec[0], tvec[1], tvec[2], evec[0], evec[1], evec[2]])

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
