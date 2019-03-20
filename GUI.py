import threading
import tkinter as tk
from tkinter import *
from tkinter import Menu
from tkinter import ttk

from PIL import ImageTk, Image

import GUIDataPlotting
from VisionEntityClasses.Camera import *


class GUIApplication(threading.Thread):
    global length

    def __init__(self, connector):
        threading.Thread.__init__(self)

        msg = 'Thread: ', threading.current_thread().name
        logging.info(msg)
        # Camera variables
        self.counter = 0
        self.c = connector
        self.camlist = self.c.initConnectedCams()
        self.camIDInUse = 1
        self.image_tk = None
        # GUI Handling flags
        self.doStopApp = False
        self.show_video = False
        self.showPoseStream = False

    def run(self):
        '''
        Run the main application.
        '''
        self.camIDInUse = 0

        # Set up main window.
        self.root = Tk()
        self.root.title('Boat Pose Estimator')
        self.root.geometry('850x750')
        self.root.configure(background='black')
        # Create menu
        self.menu = Menu(self.root)
        self.file_menu = Menu(self.menu, tearoff=0)

        # Create notebook
        self.notebook = ttk.Notebook(self.root)

        # Defines and places the notebook widget. Expand to cover complete window.
        self.notebook.pack(fill=BOTH, expand=True)

        # gives weight to the cells in the grid so thy don't collapse
        self.rows = 0
        while self.rows < 1:
            self.root.rowconfigure(self.rows, weight=1)
            self.root.columnconfigure(self.rows, weight=1)
            self.rows += 1

        # Adds tabs of the notebook
        self.page_1 = ttk.Frame(self.notebook)
        self.page_2 = ttk.Frame(self.notebook)
        self.page_3 = ttk.Frame(self.notebook)
        self.page_4 = ttk.Frame(self.notebook)
        self.page_5 = ttk.Frame(self.notebook)
        self.notebook.add(self.page_1, text='Camera')
        self.notebook.add(self.page_2, text='Calibration')
        self.notebook.add(self.page_3, text='PDF')
        self.notebook.add(self.page_4, text='Graph')
        self.notebook.add(self.page_5, text='Configuration')

        #  File menu setup
        self.file_menu.add_command(label='New', command=None)
        self.file_menu.add_command(label='Save', command=None)
        self.file_menu.add_command(label='Open', command=None)
        self.file_menu.add_command(label='Settings', command=None)
        self.file_menu.add_command(label='Export', command=None)
        self.file_menu.add_command(label='Exit', command=self.root.quit)
        self.menu.add_cascade(label='File', menu=self.file_menu)

        # Edit menu setup
        self.edit_menu = Menu(self.menu, tearoff=0)
        self.edit_menu.add_command(label='Cut', command=None)
        self.edit_menu.add_command(label='Copy', command=None)
        self.edit_menu.add_command(label='Paste', command=None)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)

        # Configure setup
        self.root.config(menu=self.menu)

        # Camera Page: Configure PanedWindows
        self.camPaneTabMain = PanedWindow(self.page_1, bg='gray40')
        self.camPaneTabMain.pack(fill=BOTH,
                                 expand=True)  # camPaneTabMain.pack(page_1)#(row=0, column=0,columnspan=1,rowspan=1,sticky='NESW')

        self.left_camPaneTabMain = Label(self.camPaneTabMain)  # , text="left pane")
        self.camPaneTabMain.add(self.left_camPaneTabMain)

        self.midSection_camPaneTabMain = PanedWindow(self.camPaneTabMain, orient=VERTICAL, bg='gray80')
        self.camPaneTabMain.add(self.midSection_camPaneTabMain)

        self.top = PanedWindow(self.midSection_camPaneTabMain)
        # self.top.config(height=60)
        self.midSection_camPaneTabMain.add(self.top, height=500)

        self.main_label = Label(self.top, text='Camera Views')
        # self.main_label.config(height=40)
        self.main_label.grid(column=0, row=0)

        self.bottom = PanedWindow(self.midSection_camPaneTabMain)
        self.bottom.config(height=20)
        self.midSection_camPaneTabMain.add(self.bottom, height=50)

        self.poseFontType = "Courier"
        self.poseFontSize = 32
        self.shipPoseLabel_camPaneTabMain = Label(self.bottom, text="Pose:",
                                                  font=(self.poseFontType, self.poseFontSize))
        self.shipPoseLabel_camPaneTabMain.grid(column=0, row=0)

        self.dispPoseBunker_camPaneTabMain = Frame(self.bottom)  # , orient=HORIZONTAL)
        self.dispPoseBunker_camPaneTabMain.grid(column=0, row=1, columnspan=6)

        self.dispX_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='x0',
                                          font=(self.poseFontType, self.poseFontSize), padx=25)
        self.dispX_camPaneTabMain.grid(column=0, row=0)
        self.dispY_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='y0',
                                          font=(self.poseFontType, self.poseFontSize), padx=25)
        self.dispY_camPaneTabMain.grid(column=1, row=0)
        self.dispZ_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='z0',
                                          font=(self.poseFontType, self.poseFontSize), padx=25)
        self.dispZ_camPaneTabMain.grid(column=2, row=0)
        self.dispRoll_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='roll0',
                                             font=(self.poseFontType, self.poseFontSize), padx=25)
        self.dispRoll_camPaneTabMain.grid(column=0, row=1)
        self.dispPitch_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='pitch0',
                                              font=(self.poseFontType, self.poseFontSize), padx=25)
        self.dispPitch_camPaneTabMain.grid(column=1, row=1)
        self.dispYaw_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='yaw0',
                                            font=(self.poseFontType, self.poseFontSize), padx=25)
        self.dispYaw_camPaneTabMain.grid(column=2, row=1)

        self.second_label = Label(self.page_2, text='Camera Calibration')
        self.second_label.place(relx=0.5, rely=0.02, anchor='center')

        # Page 3: PDF setup
        self.page_3_frame = Frame(self.page_3)
        # must keep a global reference to these two
        self.im = Image.open('arucoBoard.png')
        self.im = self.im.resize((300, 300), Image.ANTIALIAS)
        self.ph = ImageTk.PhotoImage(self.im)
        # Need to use ph for tkinter to understand
        self.btn_img = Label(self.page_3_frame, image=self.ph)
        self.btn_img.pack()
        self.page_3_frame.pack()
        self.page_3_label_frame = Frame(self.page_3_frame)
        self.page_3_label_frame.configure(relief='groove')
        self.page_3_label_frame.configure(borderwidth='2')
        self.page_3_label_frame.configure(relief='groove')
        self.page_3_entry_frame = Frame(self.page_3_frame)
        self.page_3_entry_frame.configure(relief='groove')
        self.page_3_entry_frame.configure(borderwidth='2')
        self.page_3_entry_frame.configure(relief='groove')

        self.page_3_label_frame.pack(side=LEFT)
        self.page_3_entry_frame.pack(side=RIGHT)

        self.length = Label(self.page_3_label_frame, text='Length:')  # Add text to label
        self.length_entry = Entry(self.page_3_entry_frame)  # Create entry for that label
        vcmd_length = (self.length_entry.register(self.on_validate), '%P')  # Check if input is valid

        self.width = Label(self.page_3_label_frame, text='Width: ')
        self.width_entry = Entry(self.page_3_entry_frame)
        vcmd_width = (self.width_entry.register(self.on_validate), '%P')

        self.size = Label(self.page_3_label_frame, text='Size: ')
        self.size_entry = Entry(self.page_3_entry_frame)
        vcmd_size = (self.size_entry.register(self.on_validate), '%P')

        self.gap = Label(self.page_3_label_frame, text='Gap: ')
        self.gap_entry = Entry(self.page_3_entry_frame, validate='key')
        vcmd_gap = (self.gap_entry.register(self.on_validate), '%P')

        self.length.pack()
        self.length_entry.insert(0, '3')  # Add generic text
        self.length_entry.bind('<Button-1>', self.on_entry_click)  # If clicked on
        self.length_entry.configure(foreground='gray')
        self.length_entry.pack()
        self.length_entry.config(validate='key', validatecommand=vcmd_length)

        self.width.pack()
        self.width_entry.insert(0, '3')
        self.width_entry.bind('<Button-1>', self.on_entry_click)
        self.width_entry.configure(foreground='gray')
        self.width_entry.pack()
        self.width_entry.config(validate='key', validatecommand=vcmd_width)

        self.size.pack()
        self.size_entry.insert(0, '40')
        self.size_entry.configure(foreground='gray')
        self.size_entry.bind('<Button-1>', self.on_entry_click)
        self.size_entry.pack()
        self.size_entry.config(validate='key', validatecommand=vcmd_size)

        self.gap.pack()
        self.gap_entry.insert(0, '5')
        self.gap_entry.bind('<Button-1>', self.on_entry_click)
        self.gap_entry.configure(foreground='gray')
        self.gap_entry.pack()
        self.gap_entry.config(validate='key', validatecommand=vcmd_gap)

        self.btn_frame = Frame(self.page_3)
        self.btn_frame.pack()
        self.pdf_btn = Button(self.btn_frame, text='Save Aruco Board',
                              command=lambda: self.savePDFParam())
        self.pdf_btn.pack(side=BOTTOM)

        # Page 4: Graph setup
        self.page_4_frame = Frame(self.page_4)
        self.page_4_frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.page_4_frame.configure(relief='groove')
        self.page_4_frame.configure(borderwidth='2')
        self.page_4_frame.configure(relief='groove')
        self.page_4_frame.configure(background='#000000')
        self.page_4_frame.configure(width=565)

        # TODO:Improve so that we dont have to catch error for wrong index.
        try:
            GUIDataPlotting.createDataWindow(self.page_4_frame)
        except IndexError:
            logging.info('Sketchy, but OK.')

        self.camFrameSettingSection = Frame(self.left_camPaneTabMain, bg='gray80')  # , orient=HORIZONTAL)

        # Start and stop button setup
        self.start_btn = Button(self.camFrameSettingSection, text='Start', command=self.startRawCameraClicked)
        # init_cams_btn = Button(page_1, text='Initialise cameras', command=startClicked)
        self.stop_btn = Button(self.camFrameSettingSection, text='Stop', command=self.stopRawCameraClicked)
        self.hidecam_btn = Button(self.camFrameSettingSection, text='Hide', command=self.hideCamBtnClicked)
        self.camFrameSettingSection.pack()
        self.calibrate_btn = Button(self.page_2, text='Calibrate', command=None)

        self.start_btn.grid(column=0, row=0)
        self.stop_btn.grid(column=1, row=0)
        self.hidecam_btn.grid(column=2, row=0)
        self.availCamsLabel = Label(self.left_camPaneTabMain, text='Available cameras: ')
        self.availCamsLabel.pack()

        self.calibrate_btn.grid(column=1, row=1)
        self.calibrate_btn.grid_rowconfigure(1, weight=1)
        self.calibrate_btn.grid_columnconfigure(1, weight=1)

        # Camera temp variables.
        # cam_list = ['Cam 1', 'Cam 2', 'Cam 3']
        self.var = IntVar()

        self.v = tk.IntVar()
        self.v.set(1)  # initializing the choice, i.e. Python

        for vali, cam in enumerate(self.camlist):
            tk.Radiobutton(self.left_camPaneTabMain,text=str(vali),
                           padx=20,
                           variable=self.v,
                           value=vali).pack()  # grid(column=1,row=0+vali)
        deadSpace1 = Frame(self.left_camPaneTabMain, height=100).pack()
        self.startCamApp = Button(self.left_camPaneTabMain, text='Start application', command=self.startFindPoseApp)
        self.stopCamApp = Button(self.left_camPaneTabMain, text='Stop application', command=self.setFindPoseFalse)
        self.startCamApp.pack()
        self.stopCamApp.pack()
        deadSpace2 = Frame(self.left_camPaneTabMain, height=50).pack()

        # Setu the config tab
        self.setupConfigTab()
        # Start it all
        self.root.mainloop()

        # Configuration setup

    def setupConfigTab(self):
        self.configPaneTabMain = PanedWindow(self.page_5, bg='gray40')
        self.configPaneTabMain.pack(fill=BOTH, expand=True)
        # Create paned windows
        self.left_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL)  # , text="left pane")
        self.configPaneTabMain.add(self.left_configPaneTabMain)

        self.midSection_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL, bg='gray80')
        self.configPaneTabMain.add(self.midSection_configPaneTabMain)

        self.rightSection_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL)
        self.configPaneTabMain.add(self.rightSection_configPaneTabMain)

        self.leftSectionLabel_configPaneTabMain = Label(self.left_configPaneTabMain, text="left pane")
        self.left_configPaneTabMain.add(self.leftSectionLabel_configPaneTabMain)

        self.midtopSectionLabel_configPaneTabMain = Label(self.midSection_configPaneTabMain, text="top pane")
        self.midSection_configPaneTabMain.add(self.midtopSectionLabel_configPaneTabMain)

        self.midbottomSectionLabel_configPaneTabMain = Label(self.midSection_configPaneTabMain, text="bottom pane")
        self.midSection_configPaneTabMain.add(self.midbottomSectionLabel_configPaneTabMain)
        self.midSection_configPaneTabMain.add(self.midbottomSectionLabel_configPaneTabMain)

        self.rightSectionLabel_configPaneTabMain = Label(self.rightSection_configPaneTabMain, text="right pane")
        self.rightSection_configPaneTabMain.add(self.rightSectionLabel_configPaneTabMain)
        # Configurations for which cams to connect
        self.selectCamIndexesFrame = Frame(self.midSection_configPaneTabMain)
        self.midSection_configPaneTabMain.add(self.selectCamIndexesFrame)
        opt = []

        def chkbox_checked():
            for ix, item in enumerate(cb):
                opt[ix] = (cb_v[ix].get())
            print(opt)

        mylist = [
            1, 2, 3, 4, 5
        ]
        cb = []
        cb_v = []
        for ix, text in enumerate(mylist):
            cb_v.append(tk.StringVar())
            off_value = -1  # whatever you want it to be when the checkbutton is off
            cb.append(tk.Checkbutton(self.selectCamIndexesFrame, text=text, onvalue=text, offvalue=off_value,
                                     variable=cb_v[ix],
                                     command=chkbox_checked))
            cb[ix].grid(row=ix, column=0, sticky='w')
            opt.append(off_value)
            cb[-1].deselect()  # uncheck the boxes initially.
        label = tk.Label(self.selectCamIndexesFrame, width=20)
        label.grid(row=5 + 1, column=0, sticky='w')

        # e1 = Entry(self.midtopSectionLabel_configPaneTabMain)
        # self.midSection_configPaneTabMain.pack(e1)

        # Add buttons for resetting camera extrinsic matrixes
        self.resettingCamExtrinsicFrame = Frame(self.leftSectionLabel_configPaneTabMain)
        resetCamExtrinsicBtn = Button(self.resettingCamExtrinsicFrame, command=self.resetCamExtrinsic).pack()

    def resetCamExtrinsic(self):
        '''
        Reset the cam extrinsic matrixes to the current frame point.
        :return:
        '''
        if self.poseEstimationIsRunning:
            logging.info()

    def startRawCameraClicked(self):
        '''
        Start Video Stream
        :return: None
        '''
        self.show_video = True
        self.main_label.configure(text='Starting video stream')
        self.rawVideoStream()

    #    if not show_video:
    #       start_btn.grid(column=0, row=2)
    #      stop_btn.grid(column=None, row=None)
    # elif show_video:
    #    stop_btn.grid(column=1, row=2)
    #   start_btn.grid(column=None, row=None)

    def stopRawCameraClicked(self):
        '''
        Stops video stream. Possible to add more functionality later on for saving data etc.
        :return: None at the moment, but may return datastream later on.
        '''
        self.saveFrame()
        self.show_video = False

        self.main_label.configure(text='Stopping video stream')

    #   if not show_video:
    #      start_btn.grid(column=0, row=2)
    #     stop_btn.grid(column=None, row=None)
    # elif show_video:
    #   stop_btn.grid(column=1, row=2)
    #  start_btn.grid(column=None, row=None)

    def hideCamBtnClicked(self):
        # Hide the cam.

        # Don't access new frames.

        self.show_video = False
        self.image_tk = ImageTk.PhotoImage(image=self.img_video)
        self.main_label.image_tk = self.image_tk
        self.main_label.configure(image='', text='Image hidden.')
        # self.main_label.after(1, self.rawVideoStream)
        # self.main_label.grid(column=0, row=0)

    def rawVideoStream(self):
        '''
        Create a simple setup for testing video stream with GUI. Not working if PoseEstimation is running.
        :return: None
        '''
        print('Show video: (show_video) ', self.show_video)
        if self.show_video is True:
            try:
                self.frame = self.c.getImgFromSingleCam(self.v.get())  # currCap.read()
                if self.frame is not None:
                    self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    self.img_video = Image.fromarray(self.cv2image)
                    self.image_tk = ImageTk.PhotoImage(image=self.img_video)
                    # self.main_label.config(height=40)
                    self.main_label.image_tk = self.image_tk
                    self.main_label.configure(image=self.image_tk)
                    self.main_label.after(1, self.rawVideoStream)
                else:
                    logging.info("Frame is None.")
            except AttributeError as e:
                logging.error(str(e))

    def showFindPoseStream(self, frame):
        logging.debug('Inside posestream')
        if self.showPoseStream:
            try:
                if frame is not None:
                    self.cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.img_video = Image.fromarray(self.cv2image)
                    self.image_tk = ImageTk.PhotoImage(image=self.img_video)
                    self.main_label.image_tk = self.image_tk
                    self.main_label.configure(image=self.image_tk)
                    # main_label.after(1, videoStream)
            except AttributeError as e:
                logging.error(str(e))
        else:
            # self.main_label.grid(row=None,column=None)
            pass

    def showImage(self):
        '''
        test to save single frame
        :return: img
        '''
        self.img = ImageTk.PhotoImage(file='images/test_image.png')
        self.img_label = Label(self.root, image=self.img)
        self.img_label.grid(column=0, row=0)

    # function for saving a single frame
    def saveFrame(self):
        '''
        Save a single frame from video feed
        :return: jpg
        '''
        cv2.imwrite('images/frame%d.jpg' % self.counter, self.rawVideoStream())

    def changeCameraID(self, camid):
        print("CHANGING CAMERA ID: Camid to shift to", camid)
        print("Previous camid: ", self.camIDInUse)
        self.camIDInUse = camid

    def placeGraph(self):
        GUIDataPlotting.plotGraph()

    def startFindPoseApp(self):
        '''
        Start the poseestimator in application.
        :return:
        '''
        # Start the main app
        self.poseEstimationIsRunning = True
        self.poseEstmationThread = threading.Thread(target=self.c.startApplication,
                                                    args=[self.dispContiniusResults, self.doAbortApp], daemon=True)
        self.poseEstmationThread.start()
        logging.info('Started application in a own thread.')

    def doAbortApp(self):
        '''
        Stop the poseestimation running, but (for now), don't stop the application. .
        :return:
        '''
        return self.doStopApp  # For now

    def setFindPoseFalse(self):
        '''
        Set flag who stops the poseestimation running to True.
        '''
        logging.info("Setting doStopApp to True")
        self.doStopApp = True
        self.poseEstimationIsRunning = False

    def dispContiniusResults(self, poseFrame):
        '''
        Passed to, and called from Connector, while application runs.
        Delivers pose and the "poseframe".
        '''
        self.showFindPoseStream(poseFrame)

    def fileClicked(self):
        '''
        Dummy function for setup for buttons or other functions that needs callback functions
        :return: print
        '''
        print('File clicked')

    def savePDFParam(self):
        '''
        Return values from entry and send it to the arucoPoseEstimator
        TODO: aruco pose estimator should no longer be used. arucoboard should be used in stead
        :return:
        '''
        length_value = self.length_entry.get()
        length_value = int(length_value)
        width_value = self.width_entry.get()
        width_value = int(width_value)
        size_value = self.size_entry.get()
        size_value = int(size_value)
        gap_value = self.gap_entry.get()
        gap_value = int(gap_value)

        self.aruco = Connector.ArucoPoseEstimator(length_value, width_value, size_value, gap_value)
        self.aruco.writeBoardToPDF()

    def validate(self, string):
        '''
        Regex for input on entry
        :param string: The input you want to check.
        :return: only return numbers written.
        '''
        regex = re.compile(r'(\+|\-)?[0-9,]*$')
        result = regex.match(string)
        return (string == ''
                or (string.count('+') <= 1
                    and string.count('-') <= 1
                    and string.count(',') <= 1
                    and result is not None
                    and result.group(0) != ''))

    def on_validate(self, P):
        '''
        Check if the validation is true
        :param P:
        :return:
        '''
        return self.validate(P)

    # This function needs improvement so that it only checks the entry that is clicked instead of all at the same time.
    def on_entry_click(self, event):
        '''function that gets called whenever entry is clicked'''
        if self.length_entry.get() == '3':
            self.length_entry.delete(0, 'end')  # delete all the text in the entry
            self.length_entry.insert(0, '')  # Insert blank for user input
            self.length_entry.configure(foreground='black')
        elif self.width_entry.get() == '3':
            self.width_entry.delete(0, 'end')  # delete all the text in the entry
            self.width_entry.insert(0, '')  # Insert blank for user input
            self.width_entry.configure(foreground='black')
        elif self.size_entry.get() == '40':
            self.size_entry.delete(0, 'end')  # delete all the text in the entry
            self.size_entry.insert(0, '')  # Insert blank for user input
            self.size_entry.configure(foreground='black')
        elif self.gap_entry.get() == '5':
            self.gap_entry.delete(0, 'end')  # delete all the text in the entry
            self.gap_entry.insert(0, '')  # Insert blank for user input
            self.gap_entry.configure(foreground='black')
