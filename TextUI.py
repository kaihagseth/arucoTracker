import cv2



class TextUI():
    '''
    Recieve and snd text commands from user.
    '''
    def __init__(self, connector):
        self.c = connector
    def start(self):
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
              '6. Initialise connected cameras except screencam'
              '2. List cameras \n'
              '3. Import cameras \n'
              '4. Calibrate cameras \n'
              '5. Test cameras'
              )
        choice = int(input('Type: '))
        if choice is 1:
            self.c.initConnectedCams(includeDefaultCam=True)
        if choice is 6:
            self.c.initConnectedCams(includeDefaultCam=False)

        elif choice is 2:
            print('\n'
                  'Cameras is on index: '
                 )
            print(self.c.getConnectedCams())
            print('Number of cameras: ', len(self.c.getConnectedCams()))
            #print(cam.name, '\n') for cam in self.c.getCamList()
            #choice = int(input('Type: '))
        elif choice is 5:
            self.testCameras()

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
            cv2.imshow('Test', img)
            cv2.waitKey(0)

