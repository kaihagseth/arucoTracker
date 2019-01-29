import cv2
import os
import time



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

    def calibrateCamsAllPos(self, numbCbPositions=1, timeBetwFrames=3):
        for i in range(numbCbPositions):
            cb_frames = self.takeSimultaneousImg()
            time.sleep(timeBetwFrames)

    #def addCamCalib(self):

