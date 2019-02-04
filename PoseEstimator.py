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

    def initSCPEs(self, cams):
        for cam in cams:
            SCPE = SingleCameraPoseEstimator(cam)
            self.SCPEs.append(SCPE)
    def getPoseFromCams(self):
        logging.info('Starting getPoseFromCams()')
        for SCPE in self.SCPEs:
            print('SCPE start')
            singlecam_curr_pose = 10
            singlecam_curr_pose_que = queue.Queue()
            th = threading.Thread(target=SCPE.findPoseResult_th, args=[singlecam_curr_pose, singlecam_curr_pose_que])
            self.threadInfoList.append([SCPE, th, singlecam_curr_pose])
            print('ThreadInfoList: ', self.threadInfoList)
            th.start()

    def collectPoses(self):
        print(self.threadInfoList)
        #singlecam_poses = self.threadInfoList[:,2]
        #print(singlecam_poses)
        time.sleep(1)
        return self.threadInfoList