import logging

import cv2
import os
import time
from Camera import Camera
import time
from infi.devicemanager import DeviceManager #DM to

class CameraGroup():
    def __init__(self):
        self.camReg = []
        self.includeDefCam = True
        dm = DeviceManager()
        dm.root.rescan()
        devices = dm.all_devices
        webcams = []
        for i in devices:
            try:
                if str(i.location).startswith('0000.0014') and "webcam" in i.friendly_name.lower():  # Only things at channel 14 is useful
                    print('\n {} : address: {}, bus: {}, location: {}'.format(i.friendly_name, i.address, i.bus_number, i.location))
                    webcams.append(i)
            except Exception:
                pass

    def addSingleCam(self, cam):
        self.camReg.append(cam)
    def getCamByID(self, ID):
        '''
        Get a cam based on number ()
        :param ID: Number of the camera
        :return: OTCam
        '''
        wantedCam = None
        for cam in self.camReg:
            if cam._ID is ID:
                wantedCam = cam
                break
        if wantedCam is None:
            logging.error('No cam found.')
        return wantedCam


    def takeSimultaneousImg(self):
        '''
        Grab a image from all cameras. 
        :return: A list with a image from each cam. 
        '''''
        frames = []
        for cam in self.camReg:
            frame = cam.getFrame()
            frames.append(frame)
        return frames

    def fastCalibrateCamsAllPos(self, numbCbPositions=1, timeBetwFrames=3):
        '''
        Fast calibration where the calib images is taken very quickly.
        :param numbCbPositions: Number of imagerounds to take with chessboard, at different positions.
        :param timeBetwFrames: Seconds between each number is taken.
        :return: None
        '''
        dataset = []
        for i in range(numbCbPositions):
            cb_frames = self.takeSimultaneousImg()
            dataset.append(cb_frames)
            time.sleep(timeBetwFrames)

    def testDevice(self, sourceNumber):
        '''
        Check if the camera with the set sourceNumber is operative.
        :return:
        '''
        cap = cv2.VideoCapture(sourceNumber)
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', sourceNumber)
    def findConnectedCams2(self):
        '''
        Find all cams connected to system.  
        :return: 
        ''' #TODO: Find new algorithm, this thing is sloooow.
        if self.includeDefCam is False:
            index = 1 # Dont include webcam at index 0.
        else:
            index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                print('Found cam at index ', index)
                arr.append(index)
            time.sleep(1)
            cap.release()
            index += 1
            time.sleep(1)
            if index < 10:
                break
        return arr

    def findConnectedCams(self):
        '''
        Find all cams connected to system.  
        :return: 
        ''' #TODO: Find new algorithm, this thing is sloooow.
        logging.info('Inside findConnectedCams()')
        if self.includeDefCam is False:
            index = 1 # Dont include webcam at index 0.
        else:
            index = 0
        arr = []
        startArr = [0, 1, 2]
        for i in startArr:
            cap = cv2.VideoCapture(i)
            ret, frame = cap.read()
            #3logging.info('Cam on index ', i, ': ', ret)
            if ret:
                arr.append(i)
            time.sleep(0.5)
        return arr

    def initConnectedCams(self, includeDefaultCam=False):
        self.includeDefCam = includeDefaultCam
        conCams = self.findConnectedCams()
        print('Connected cams: ', conCams)
        if not includeDefaultCam:
            if conCams[0] is 0: # Default cam is in list. We want to remove it.
                conCams.remove(0)
                print(conCams)
        for i in conCams:
            cam = Camera(('Cam',i),i,i)
            self.addSingleCam(cam)
        return self.camReg

    def getSingleImg(self, index):
        cam = self.getCamByID(index)
        frame = cam.getSingleFrame()
        return frame
