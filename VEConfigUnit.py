from VisionEntityClasses.VisionEntity import VisionEntity
import logging
from tkinter import *
from exceptions import CamNotOpenedException
from threading import Thread
class VEConfigUnit(Thread):
    '''
    Class for holding choices regarding cam and VE in config tab GUI.
    Also holds created VE, until taken over by PoseEstimator when running PoseEstimation.
    '''

    def __init__(self, camID, parent):
        Thread.__init__(self)
        self._id = camID  # Camera index
        self.parent = parent
        self._VE = None
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
        self._cb = Checkbutton(self._frame, text=str(self._id),
                                  variable=self._cb_v, command=self.chkbox_checked, bg='#424242')  # Checkbutton
        self.cb_string_v = []  # List for telling the status of the cam on given index
        # self.cb_string = []  # Status for each index/camera on index
        self.conStatusLabel = Label(self._frame,
                                    text="Disconnected", fg="red",bg='#424242')
        self.connectBtn = Button(self._frame, text="Connect",bg='#424242',
                                 command=self.doConnect)  # , variable=self._state, onvalue=1, offvalue=0)
        self.previewBtn = Button(self._frame, text="Preview", command=self.doPreview,bg='#424242',
                                 state=DISABLED)  # , variable = self._state, onvalue=3, offvalue=2)
    def run(self):
        # Pack everything in container
        self._cb.grid(row=0, column=0, sticky='w')
        deadspace3 = Frame(self._frame, width=20,bg='#424242').grid(row=0, column=1)
        self.connectBtn.grid(row=0, column=2)
        self.previewBtn.grid(row=0, column=3)
        self.conStatusLabel.grid(row=0, column=4)
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
            self.previewBtn.config(state="normal")
            self.conStatusLabel.config(text="Connected", fg="green")
            self._currState = 2
        elif newState is 3: # Want to preview
            self._currState = 3
        elif newState is 4: # Previewing
            self.previewBtn.config(text="Hide preview", command=self.hidePreview)
            self._currState = 4
        elif newState is 5: # Disconnecting
            self._currState = 5
            self.connectBtn.config(text="Connect", command=self.doConnect)
            self.previewBtn.config(state="disabled")
            self.conStatusLabel.config(text="Disconnecting...", fg="red")
            # Disconnect and terminate VE
            if self._VE is not None:
                self._VE.terminate()
                self._VE = None
            self._currState = 0
            self.setState(0)
            return
        elif newState is 6: # VE running in PoseEstimator
            self.connectBtn.config(text="Deactivate", command=self.removeVEFromRunningPE)
            self.previewBtn.config(state="disabled")
            self.conStatusLabel.config(text="Used in PE", fg="green")
            self.continueRunInPE = True
            self._VE = None # Not the responsibility of GUI anymore

        elif newState is 7: # Failed to open camera
            self.conStatusLabel.config(text="Failed.", fg="black")
            self.connectBtn.config(text="Retry")
            self.previewBtn.config(state="disabled")
        elif newState is 8: # Disconnect from PE
            pass
        elif newState is 9: # Failed to use in PE (i.e. cam not opened)
            self.conStatusLabel.config(text="Failed.", fg="black")
            self.setState(0)
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
        self.setDoPreviewState(True)
        self.setState(4)
    def hidePreview(self):
        """
        Hide the preview window
        :return:
        """
        self.setDoPreviewState(False)
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
        self.continueRunInPE = False

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