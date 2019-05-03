from VisionEntityClasses.VisionEntity import VisionEntity
import logging
from tkinter import *
from exceptions import CamNotOpenedException
from threading import Thread
import os



class VECalibUnit(Thread):
    '''
    A container holding options and information about calibration  for a single VE unit.
    '''
    def __init__(self, VE, mainGUI, parent, GUI_calibPreviewImage_fx):
        Thread.__init__(self)
        self._id = VE.ID  # Camera index
        self.parent = parent
        self._VE = None
        self._mainGUI = mainGUI
        # Assign a variable to the function to call when setting preview status
        self.GUI_setPreviewImage_fx = GUI_calibPreviewImage_fx
        self._frame = Frame(self.parent,bg='#424242')  # Container for all widgets
        self._doPreviewState = False
        self._currState = 0
        self._cb_v = BooleanVar()  # Variable to hold state of
        self._cb_v.set(False)
        self._state = IntVar()
        self._stateText = StringVar()
        self.continueRunInPE = False # Whether to contniue to use VE in PE.
        self._stateText.set('Disconnected')  # Statustext of connection with cam
        # self._connectionStatusLabel = "Disconnected"
        self._label = Label(self._frame, text="Camera " +str(self._id) +":", bg="#424242", fg="white")#, font="Arial")
        self._cb = Checkbutton(self._frame, text="",#str(self._id),
                            fg="black", variable=self._cb_v, command=self.chkbox_checked, bg='#424242',width=12)  # Checkbutton
        self.cb_string_v = []  # List for telling the status of the cam on given index
        # self.cb_string = []  # Status for each index/camera on index
        self.conStatusLabel = Label(self._frame,
                                    text="Disconnected", fg="red",bg='#424242',width=20)
        self.connectBtn = Button(self._frame, text="Connect",bg='#424242',fg="white",
                                 command=self.doConnect,width=15)  # , variable=self._state, onvalue=1, offvalue=0)
        self.previewBtn = Button(self._frame, text="Preview", command=self.doPreview,bg='#424242',fg="white",
                                 state=DISABLED,width=15)  # , variable = self._state, onvalue=3, offvalue=2)

        # Dictionary with options
        path = "calibValues"
        choices = os.listdir(path)
        self.dropVar = StringVar()
        self.calibFilePopup = OptionMenu(self._frame, self.dropVar, *choices, command=self.setCalibFileChoice)
        self.calibFilePopup.config(bg="#424242",fg="white",highlightbackground='#424242')
        self.dropVar.set("Calibration file")
        #Label(self._frame, text="Choose a dish").grid(row=1, column=1)
        self.calibFilePopup.grid(row=2, column=1)

    def setCalibFileChoice(self, value):
        logging.info(value)
        # First two letters/numbers of string is the new label for camera.
        callname = value[:2]
        logging.info("New callname: " + callname)
        self._VE.setCameraLabelAndParameters(callname)
    def run(self):
        # Pack everything in container
        self._label.grid(row=0,column=0)
        self._cb.grid(row=0, column=1, sticky='w')
        deadspace3 = Frame(self._frame, width=20,bg='#424242').grid(row=0, column=2)
        self.connectBtn.grid(row=0, column=3)
        self.previewBtn.grid(row=0, column=4)
        self.conStatusLabel.grid(row=0, column=5)
        self.calibFilePopup.grid(row=0,column=6)
        self.calibFilePopup.config(state="disabled")
        # return self._frame
        self._frame.grid(row=self._id, column=0)

    def chkbox_checked(self):
        pass

    def setConnectionStatus(self):
        # self._state
        state = self._state.get()
        msg = state
        logging.debug(msg)

    def doConnect(self):
        ''' Create a VisionEntity for the cam on index. Change button states. '''
        self.setState(1)

    def setState(self, newState):
        '''
        Set status for VE:
        0 = Disconnected, VE not initialised
        1 = Trying to connect, creating VE
        2 = Connected, VE created, preview is available
        3 = Want to preview
        4 = Previewing
        5 = Disconnecting
        6 = VE running in PoseEstimator
        7 = Failed to open cam
        8 = Remove cam from PE. Not implemented
        9 = Failed to use in PE (i.e. cam not opened)
        :param newState:
        :return:
        '''
        msg = "State "
        if newState is 0: # Disconnected, VE not initialised
            self.conStatusLabel.config(text="Disconnected", fg="red")
            self.connectBtn.config(text="Connect", command=self.doConnect)
            self.previewBtn.config(state="disabled")
            self.previewBtn.config(text="Preview", command=self.hidePreview)
            self.calibFilePopup.config(state="disabled")
        elif newState is 1: # Trying to connect, creating VE
            logging.debug("State is 1")
            self.connectBtn.config(text="Connecting...", command=self.doDisconnect)
            self.previewBtn.config(state="normal")
            self.conStatusLabel.config(text="Connecting...", fg="black")
            try:
                self._VE = VisionEntity(self._id)
                self._currState = 1
                if self._VE is not None:
                    #Success
                    self.setState(2)
                    return
                else:
                    logging.debug("Failed to open camera.")
                    self.setState(0)
                    self._currState = 0
                    return
            except CamNotOpenedException as e:
                logging.error("Failed to open camera.")
                self._VE = None
                self.setState(7)
                return
        elif newState is 2: # Connected, VE created, preview is available
            self.connectBtn.config(text="Disconnect", command=self.doDisconnect)
            self.previewBtn.config(state="normal", text="Preview",command=self.doPreview)
            self.conStatusLabel.config(text="Connected", fg="green")
            self._currState = 2
            self.calibFilePopup.config(state="normal")
        elif newState is 3: # Want to preview
            self._currState = 3
        elif newState is 4: # Previewing
            logging.debug("Seting state to 4. ")
            self.previewBtn.config(text="Hide preview", command=self.hidePreview)
            self._currState = 4
        elif newState is 5: # Disconnecting
            self._currState = 5
            self.connectBtn.config(text="Connect", command=self.doConnect)
            self.previewBtn.config(state="disabled")
            self.conStatusLabel.config(text="Disconnecting...", fg="red")
            self.setDoPreviewState(False)
            self.calibFilePopup.config(state="disabled")
            # Disconnect and terminate VE
            if self._VE is not None:
                self._VE.terminate()
                self._VE = None
            self._currState = 0
            self._cb.config(state="normal")
            self.setState(0)
            return
        elif newState is 6: # VE running in PoseEstimator
            self.connectBtn.config(text="Deactivate", command=self.removeVEFromRunningPE)
            self.previewBtn.config(state="disabled")
            self.conStatusLabel.config(text="Used in PE", fg="green")
            self.continueRunInPE = True
            self.calibFilePopup.config(state="disabled")
            self._VE = None # Not the responsibility of GUI anymore

        elif newState is 7: # Failed to open camera
            self.conStatusLabel.config(text="Failed.", fg="black")
            self.connectBtn.config(text="Retry")
            self.previewBtn.config(state="disabled")
            self.calibFilePopup.config(state="disabled")
        elif newState is 8: # Disconnect from PE
            pass
        elif newState is 9: # Failed to use in PE (i.e. cam not opened)
            self.conStatusLabel.config(text="Failed.", fg="black")
            self.setState(0)
            self._cb.config(state="normal")
            self.continueRunInPE = False

    def doDisconnect(self):
        '''
        Set the VESU-state to and do disconnect.
        :return:
        '''
        self.setState(5)

    def doPreview(self):
        '''
        Set the VESU-state to and do preview.
        :return:
        '''
        logging.debug("Doing preview")
        self.setDoPreviewState(True)
        # Tell GUI that you want to do a preview.
        self.GUI_setPreviewImage_fx(self._id)
        self.setState(4)
    def hidePreview(self):
        """
        Hide the preview window
        :return:
        """
        self.setDoPreviewState(False)
        self.GUI_setPreviewImage_fx(-1)
        self.setState(2)
    def getFrame(self):
        """
        Get image container.
        :return: Image container
        """
        return self._frame

    def getIncludeStatus(self):
        "Whether the VE should be taken in to the poseestimation."
        return self._cb_v.get()
    def getVE(self):
        return self._VE
    def getIndex(self):
        return self._id
    def removeVEFromRunningPE(self):
        '''
        Set flag to remove the VE from the current PE running. Not implemented.
        :return:
        '''
        #self.continueRunInPE = False
        self._mainGUI.connector.removeVEFromPEListByIndex(self._id)
        self.setState(0)
    def setIncludeInPEbool(self, bool):
        '''
        Set the the mark whether to include VE in PE when applied. If false, the mark is taken away.
        :param bool: True or False
        :return: None
        '''
        if bool:
            self._cb.select() # Set on
            msg = "Selecting checkbutton index ".format(self._id)
            logging.info(msg)
        else:
            self._cb.deselect() # Set off
            msg = "Deselecting checkbutton index ".format(self._id)
            logging.info(msg)
    def setDoPreviewState(self, state):
        '''
        Boool on or off to show prev image.
        :param state:
        :return:
        '''
        self._doPreviewState = state

    def getDoPreviewState(self):
        return self._doPreviewState