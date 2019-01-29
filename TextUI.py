



class TextUI():
    '''
    Recieve and snd text commands from user.
    '''
    def __init__(self, connector):
        self.connector = connector
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
    def configCameras(self):
        print('\n'
              'Please make your choice: \n'
              '1. Add new camera \n'
              '2. List cameras \n'
              '3. Import cameras \n'
              '4. Calibrate cameras \n'
              )