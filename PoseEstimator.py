from SingleCameraPoseEstimator import SingleCameraPoseEstimator
import threading, queue, logging
import time
class PoseEstimator():
    '''
    Collect pose and info from all cameras, and find the best estimated pose possible.
    '''

    def __init__(self):
        self.SCPEs = []
        self.threadInfoList = []
        self.vision_entities = []

    def initSCPEs(self, cams):
        '''
        Create a SingleCameraPoseEstimator for every camera.
        :param cams:
        :return:
        '''
        logging.info('Running ')
        for cam in cams:
            SCPE = SingleCameraPoseEstimator(cam)

            #if cam._intr
            self.SCPEs.append(SCPE)
    def getPoseFromCams(self):
        '''
        Do poseestimation for every SCPE.
        Start threads for every SCPE. Save the pose in a thread-safe variable, and add it all to a list.
        :return: None
        '''
        logging.info('Starting getPoseFromCams()')
        logging.debug('SCPE: ',self.SCPEs)
        for SCPE in self.SCPEs:
            print('SCPE start')
            singlecam_curr_pose = 10
            #Create a thread-safe variable to save pose to.
            singlecam_curr_pose_que = queue.Queue()
            singlecam_curr_pose_que.put(singlecam_curr_pose)
            logging.debug('Passing queue.Queue()')
            # Create thread, with target findPoseResult(). All are daemon-threads.
            th = threading.Thread(target=SCPE.findPoseResult_th, args=[singlecam_curr_pose, singlecam_curr_pose_que], daemon=True)
            logging.debug('Passing thread creation.')
            self.threadInfoList.append([SCPE, th, singlecam_curr_pose_que])
            print()
            print('ThreadInfoList: ', self.threadInfoList)
            th.start()

    def collectPoses(self):
        '''
        In future: Get all output from the poseestimation here.
        :return: threadInfopList
        '''
        print(self.threadInfoList)
        print('Pose: ', self.threadInfoList[0][2].get())
        #singlecam_poses = self.threadInfoList[:,2]
        #print(singlecam_poses)
        time.sleep(1)
        return self.threadInfoList