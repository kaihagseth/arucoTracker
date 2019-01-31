import cv2
from exceptions import FailedCalibrationException
import time

class TextUI():
    '''
    Recieve and snd text commands from user.
    '''
    def __init__(self, connector):
        self.DEBUG = False
        self.c = connector
    def start(self):
        if self.DEBUG:
            self.c.initConnectedCams(includeDefaultCam=True)
            print('DEBUG MODE. Cameras initialised.')
        print('SHIP POSE ESTIMATOR @ NTNU 2019 \n'
              'Please make your choice: \n'
              '1. Start application \n'
              '2. Change model parameters \n'
              '3. Configure cameras \n'
              '4. Exit'
              )
        choice = int(input('Type: '))
        if choice is 3:
            self.configCameras()
        self.start()
    def configCameras(self):
        print('\n'
              'Please make your choice: \n'
              '1. Initialise connected cameras \n'
              '6. Initialise connected cameras except screencam \n'
              '2. List cameras \n'
              '3. Import cameras \n'
              '4. Calibrate cameras \n'
              '5. Test cameras \n'
              '7. Videotest cameras'

              )
        choice = int(input('Type: '))
        if choice is 1:
            self.c.initConnectedCams(includeDefaultCam=True)
        if choice is 6:
            self.c.initConnectedCams(includeDefaultCam=False)

        elif choice is 2:
            print('\n'
                  'Cameras is on index: ', self.c.getConnectedCams()
                 )
            print('Number of cameras: ', len(self.c.getConnectedCams()))
            #print(cam.name, '\n') for cam in self.c.getCamList()
            #choice = int(input('Type: '))
        elif choice is 4:
            self.calibCameras()
        elif choice is 5:
            self.testCameras()
        elif choice is 7:
            self.videoTest(0)

    def calibCameras(self):
        '''
        Calib cameras.
        '''
        print('\n'
              'Please make your choice: \n'
              '1. Calibrate a desired camera \n'
              '2. Calibrate all cameras one by one \n'
              )
        choice = int(input('Type:'))
        if choice is 1:
            print('Running calib on 1.')
            ID = 1
            notFinished = True
            cam = self.c.getCamFromIndex(ID)
            while notFinished:
                frame = cam.getSingleFrame()
                cv2.imshow('Calibrate cam', frame)
                key = cv2.waitKey(20)
                if key == 32:  # exit on Space
                    cam.saveFrameToCalib(frame)
                    cv2.destroyWindow('Calibrate cam')
                    break
            print('Not yet supported.')
        elif choice is 2:
            print('Calibration process started.')
            camIDs = self.c.getConnectedCams()
            for ID in camIDs:
                self._calibSingleCam(ID)

    def _calibSingleCam(self, ID):
        notFinished = True
        cam = self.c.getCamFromIndex(ID)
        while notFinished: #Hasn't got decent calib result for cam yet
            frame = cam.getSingleFrame()
            cv2.imshow('Calibrate cam', frame)
            key = cv2.waitKey(20)
            if key == 32:  # exit on Space
                try: # Catch error with calib algo / bad picture
                    cam.saveFrameToCalib(frame)
                    cv2.destroyWindow('Calibrate cam')
                    print('Calibration of cam ', ID, 'is finished.')
                    notFinished = False # Calibration was successful, go to next cam.
                except FailedCalibrationException:
                    print('Calibration failed, trying again.')


    def testCameras(self):
        print('\n'
                'Please make your choice: \n'
                'Type the index you want to test, or type 10 for all.'
                )
        choice = int(input(''))
        if choice is 10:
            print('Sorry, not supported yet.')
        camIndexs = self.c.getConnectedCams()
        if choice in camIndexs:
            img = self.c.getImgFromSingleCam(choice)
            text = 'Test: Cam src: ', str(choice)
            cv2.imshow('Raw', img)
            cv2.waitKey(0)

    def videoTest(self, ID2):
        cam = self.c.getCamFromIndex(ID)
        #cam.activateSavedValues('IntriCalib.npz')
        notFinished = True
        while notFinished:  #
            print('Inside')
            frame = cam.getSingleFrame()
            undisFrame = cam.undistort(frame)
            cv2.imshow('Raw', frame)
            cv2.imshow('Undistorted', undisFrame)
            print('Before waitkey')
            key = cv2.waitKey(0)
            if key == 27:  # exit on Esc
                break