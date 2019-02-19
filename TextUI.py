import cv2
from exceptions import FailedCalibrationException
import time
import logging
import numpy as np
class TextUI():
    '''
    Recieve and snd text commands from user.
    '''
    def __init__(self, connector):
        self.DEBUG = False # If True, do some obvious things for fast forward initialisation.
        self.c = connector

    '''
    Launching the UI.
    '''
    def start(self):
        stopProgram = False
        while not stopProgram:
            if self.DEBUG:
                ''' DEBUG MODE: Fast forward with obvious things like initialisation. '''
                camlist = self.c.initConnectedCams(includeDefaultCam=True)
                #self.calibCameras()
                #cam = self.c.getCamFromIndex(0)
                #cam.loadSavedCalibValues()
                #self.c.initSCPEs(camlist)
                print('\n DEBUG MODE. Cameras initialised.')
            print('\n SHIP POSE ESTIMATOR @ NTNU 2019 \n'
                  'Please make your choice: \n'
                  '1. Start application \n'
                  '2. Change model parameters \n'
                  '3. Configure cameras \n'
                  '4. Exit'
                  )
            choice = int(input('Type: '))
            if choice is 1:
                self.startApplication()
            if choice is 2:
                pass
            if choice is 3:
                self.configCameras()
            elif choice is 4:
                stopProgram = True
    def startApplication(self):
        logging.info('Starting application')
        runApp = True
        self.c.startApplication(self.dispContiniusResults, self.doAbortApp)
    def doAbortApp(self):
        intext = True
        if intext is 'Q':
            print('doAbortFx is True')
            return True
        else:
            #print('dpAbortApp() is False')
            return False

    def dispContiniusResults(self, result):
        try:
            print("#####  Display current result:  ######")
            print(result)
            print("Rotation x - roll: ", result[0]*180.0/np.pi)
            print("Rotation y - pitch: ", result[1]*180.0/np.pi)
            print("Rotation z - yaw: ", result[2]*180.0/np.pi)
            print("Translation x: ", result[3], ' mm')
            print("Translation y: ", result[4], ' mm')
            print("Translation z: ", result[5], ' mm')
        except Exception:
            print("Could not print.")
    def abortFunction(self):
        pass
    def configCameras(self):
        print('\n'
              'Please make your choice: \n'
              '1. Initialise connected cameras \n'
              '2. Initialise connected cameras except screencam \n'
              '3. List cameras \n'
              '4. Import cameras \n'
              '5. Calibrate cameras \n'
              '6. Test cameras \n'
              '7. Videotest cameras \n'
              '8. Show current calib params, index 0 \n'
              '9. Fix HSV-calibration \n'
              '10. Load HSV-values \n'
              '11. Go back.'
              )
        choice = int(input('Type: '))
        if choice is 1:
            self.c.initConnectedCams(includeDefaultCam=True)
        elif choice is 2:
            self.c.initConnectedCams(includeDefaultCam=False)

        elif choice is 3:
            print('Cameras is on index: ', self.c.getConnectedCams())
            print('Number of cameras: ', len(self.c.getConnectedCams()))
        elif choice is 5:
            self.calibCameras()
        elif choice is 6:
            self.testCameras()
        elif choice is 7:
            self.videoTest(0)
        elif choice is 8:
            print('Printing parameters')
            self.c.getCamFromIndex(0)._IC.printCurrParams()
        elif choice is 9:
            self.doHSVCalib()
        elif choice is 10:
            self.loadHSVValues()
        elif choice is 11:
            self.start()
        else: #Invalid typing
            print('Bad typing. Try again.')
            self.configCameras()
    def calibCameras(self):
        '''
        Menu for selecting what cameras to calibrate.
        '''
        print('\n'
              'Please make your choice: \n'
              '1. Calibrate a desired camera \n'
              '2. Calibrate all cameras one by one \n'
              '3. Abort and go back.'
              )
        choice = int(input('Type:'))
        if choice is 1:
            print('ID of wanted camera, example 0:')
            IDchoice = int(input('Type:'))
            print(' How many calibration images do you want to take? Recommended is 10.')
            numbImg = int(input('Type:'))
            self._calibSingleCam(ID=IDchoice, numbImg=numbImg)
        elif choice is 2:
            print(' How many calibration images do you want to take? Recommended is 10 per cam.')
            numbImg = int(input('Type:'))
            print('Calibration process started.')
            camIDs = self.c.getConnectedCams()
            for ID in camIDs:
                self._calibSingleCam(ID, numbImg)
        elif choice is 3:
            self.start()
        else:
            print('Wrong typing')
            self.calibCameras()

    def _calibSingleCam(self, ID, numbImg):
        '''
        Calibrate a single camera, based on ID. Take n images and send them to the calib-algorithm. Only send the frames
        that gives a decent result.
        :param ID: ID of camera to calibrate.
        :param numbImg: Number of images to take in with calibration.
        :return: None
        '''
        notFinished = True
        frames = []

        while notFinished: #Hasn't got decent calib result for cam yet
            try:
                cam = self.c.getVEFromCamIndex(ID).getCam()
                frame = cam.getSingleFrame()
                frame = cam.getSingleFrame()
                cv2.imshow('Calibrate cam', frame)
            except cv2.error as e:
                print('Cam capture failed. Trying again.')
                print(str(e))
                #raise FailedCalibrationException(msg='Couldn\'t acces camera.')
            key = cv2.waitKey(20)
            if key == 32:  # exit on Space
                try: # Catch error with calib algo / bad picture
                    # cam.calibrateCam([frame])
                    frames.append(frame)
                    print('Captured, image nr {0} of {1}'.format(len(frames), numbImg))
                except FailedCalibrationException:
                    print('Calibration failed, trying again.')

                if len(frames) >= numbImg:
                    try:  # Try calibration with all images, catch failure
                        cam.calibrateCam(frames)
                        cv2.destroyWindow('Calibrate cam')
                        print('Calibration of cam ', ID, 'is finished.')
                        notFinished = False  # Calibration was successful, go to next cam.
                    except FailedCalibrationException:
                        #frames = []
                        print('Calibration failed, trying again.')
                #else:
                 #   notFinished = True


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

    def videoTest(self, ID):
        cam = self.c.getCamFromIndex(ID)
        #cam.activateSavedValues('IntriCalib.npz')
        notFinished = True
        while notFinished:  #
            try:
                print('Inside')
                frame = cam.getSingleFrame()
                undisFrame = cam.undistort(frame)
                cv2.imshow('Raw', frame)
                cv2.imshow('Undistorted', undisFrame)
                print('Before waitkey')
                key = cv2.waitKey(0)
                if key == 27:  # exit on Esc
                    break
            except cv2.error:
                print('OpenCV failed. Trying again.')

    def doHSVCalib(self):
        print('What camera to calibrate? Camera index')
        choice = int(input('Type:'))
        VE = self.c.getVEFromCamIndex(choice)
        # Do HSV calibration
        #cv2.VideoCapture(choice)
        VE.calibratePointDetector()
        VE.saveHSVValues()
    def loadHSVValues(self):
        print('What camera to get values for? Camera index')
        choice = int(input('Type:'))
        VE = self.c.getVEFromCamIndex(choice)
        # Do HSV calibration
        #cv2.VideoCapture(choice)
        VE.loadHSVValues()

