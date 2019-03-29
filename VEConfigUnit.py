from VisionEntityClasses.VisionEntity import VisionEntity
import logging
from tkinter import *

class VEConfigUnit():
    '''
    Class for holding choices regarding cam and VE in config tab GUI.
    Also holds created VE, until taken over by PoseEstimator when running PoseEstimation.
    '''

    def __init__(self, camID, parent):
        self._VE = None
        self._frame = Frame(parent)  # Container for all widgets
        self._id = camID  # Camera index
        self._currState = 0
        self._cb_v = BooleanVar()  # Variable to hold state of
        self._cb_v.set(False)
        self._state = IntVar()
        self._stateText = StringVar()
        self._stateText.set('Disconnected')  # Statustext of connection with cam
        # self._connectionStatusLabel = "Disconnected"
        self._cb = Checkbutton(self._frame, text=str(self._id),
                                  variable=self._cb_v, command=self.chkbox_checked)  # Checkbutton
        self.cb_string_v = []  # List for telling the status of the cam on given index
        # self.cb_string = []  # Status for each index/camera on index
        self.conStatusLabel = Label(self._frame,
                                    text="Disconnected", fg="red")
        self.connectBtn = Button(self._frame, text="Connect",
                                 command=self.doConnect)  # , variable=self._state, onvalue=1, offvalue=0)
        self.previewBtn = Button(self._frame, text="Preview", command=self.doPreview,
                                 state=DISABLED)  # , variable = self._state, onvalue=3, offvalue=2)

        # Pack everything in container
        self._cb.grid(row=0, column=0, sticky='w')
        deadspace3 = Frame(self._frame, width=20).grid(row=0, column=1)
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
        :param newState:
        :return:
        '''
        if newState is 0: # Disconnected, VE not initialised
            self.conStatusLabel.config(text="Disconnected", fg="red")
        elif newState is 1: # Trying to connect, creating VE
            logging.debug("State is 1")
            self.connectBtn.config(text="Disconnect", command=self.doDisconnect)
            self.previewBtn.config(state="normal")
            self.conStatusLabel.config(text="Connecting...", fg="black")
            self._VE = VisionEntity(self._id)
            self._currState = 1
            if self._VE is not None:
                #Success
                self.setState(2)
        elif newState is 2: # Connected, VE created, preview is available
            self.connectBtn.config(text="Disconnect", command=self.doDisconnect)
            self.previewBtn.config(state="normal")
            self.conStatusLabel.config(text="Connected", fg="green")
            self._currState = 2
        elif newState is 3: # Want to preview
            pass
        elif newState is 4: # Previewing
            pass
        elif newState is 5: # Disconnecting
            self.connectBtn.config(text="Connect", command=self.doConnect)
            self.previewBtn.config(state="disabled")
            self.conStatusLabel.config(text="Disconnecting...", fg="red")
            # Disconnect and terminate VE
            self._VE.terminate()
            self._VE = None
            self._currState = 0
            self.setState(0)
        elif newState is 6: # VE running in PoseEstimator
            self.connectBtn.config(text="Deactivate", command=self.removeVEFromRunningPE)
            self.previewBtn.config(state="disabled")
            self.conStatusLabel.config(text="Used in PE", fg="green")
            self._VE = None # Not the responsibility of GUI anymore

    def doDisconnect(self):
        self.setState(5)

    def doPreview(self):
        pass

    def getFrame(self):
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
        pass