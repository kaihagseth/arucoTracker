import cv2
import os
import time
from Camera import Camera


class CameraGroup():
    def __init__(self):
        self.camReg = []



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
            print('No cam found.')
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
    def findConnectedCams(self):
        index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
            cap.release()
            index += 1
            if index < 10:
                break
        return arr
    #def addCamCalib(self):

    def initConnectedCams(self, includeDefaultCam=False):
        conCams = self.findConnectedCams()
        if not includeDefaultCam:
            if conCams[0] is 0: # Defaulkt cam is in list. We want to remove it.
                conCams.remove(0)
                print(conCams)
        for i in conCams:
            cam = Camera(('Cam',i),i,i)
            self.addSingleCam(cam)

    def getSingleImg(self, index):
        cam = self.getCamByID(index)
        frame = cam.getSingleFrame()
        return frame

