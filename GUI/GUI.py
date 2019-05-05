import logging
import threading
import tkinter as tk
from tkinter import *
from tkinter import Menu
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
import matplotlib

matplotlib.use('TkAgg')
import cv2
import ttkthemes
import copy
from PIL import ImageTk, Image
from GUI import GUIDataPlotting
import numpy as np
from GUI.VEConfigUnit import VEConfigUnit
from GUI.ArucoBoardUnit import ArucoBoardUnit
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.ArucoBoard import ArucoBoard
from exceptions import CamNotOpenedException
from VisionEntityClasses.IntrinsicCalibrator import videoCalibration
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import time
class GUIApplication(threading.Thread):
    global length

    def __init__(self, connector):
        threading.Thread.__init__(self)
        self.connector = connector
        self.arucoBoardUnits = dict()
        #self.arucoBoardUnits.append(board)
        msg = 'Thread: ', threading.current_thread().name
        logging.info(msg)
        self.camIndexesDisplayed = [False, False, False, False, False, False] # Set corresponding index for what indexes are displayed
        # Camera variables
        self.counter = 0

        # Observer technique: Tell connector which function to call when updating fields.
        self.connector.setPoseDisplayFunction(self.displayPoseInTrackingWindow)
        self.connectorStarted = False
        # Fields written to by external objects. Should only be read in this object.
        self.imageFrame = None           # Image frame to be shown in camera window.
        self.modelPoses = None      # Poses of all currently tracked objects. (Only one at the time for now)
        self.userBoard = None       # Arucoboard created by user in GUI.

        # Private fields written to via GUI.
        self.__displayedCameraIndex = None
        self.__resetBoardPosition = []            # If this list contains an
        self.__pushedBoards = []
        self.__start_application = []
        self.__stop_application = []
        self.__collectGUIVEs = []
        self.__doPreviewIndex = -1

        # GUI Handling flags
        self.doStopApp = False
        self.show_video = False
        self.showPoseStream = False
        self.videoPanel = None
        self.poseEstimationIsRunning = False
        self.anyCameraInitiated = False # Only True if we have applied some VEs to run with in configtab
        self.anyBoardsInitiated = False # Only True if one or more boards are intitated.
        # Button lists
        self.boardButtons = dict()
        self.cameraButtonList = []
        self.cameraButtonIndexList = []

        # Pose data
        self.translation_value_lists = [[],[],[]]

        # Some GUI frames (containers)
        self.calibCam_statusFrame = None
        self.maincalib_window = None

        self.calibConnectionFrame = None

    def run(self):
        '''
        Run the main application.
        TODO: Please add comments
        '''
        self.camIDInUse = 0

        # Set up main window.
        self.root = Tk()
        self.root.style = ttkthemes.ThemedStyle()
        self.root.title('Boat Pose Estimator')
        self.root.geometry('1250x750')
        self.root.style.theme_use('black')
        # Create menu
        self.menu = Menu(self.root)
        self.file_menu = Menu(self.menu, tearoff=0)
        self.setup_menu = Menu(self.menu, tearoff=0)

        # Create notebook
        self.notebook = ttk.Notebook(self.root)

        # Defines and places the notebook widget. Expand to cover complete window.
        self.notebook.pack(fill=BOTH, expand=True)

        # gives weight to the cells in the grid so they don't collapse
        self.rows = 0
        while self.rows < 1:
            self.root.rowconfigure(self.rows, weight=1)
            self.root.columnconfigure(self.rows, weight=1)
            self.rows += 1

        # Adds tabs of the notebook
        self.page_1 = ttk.Frame(self.notebook)
        self.page_3 = ttk.Frame(self.notebook)
        self.page_4 = ttk.Frame(self.notebook)
        self.page_5 = ttk.Frame(self.notebook)
        self.notebook.add(self.page_1, text='Camera')
        self.notebook.add(self.page_3, text='PDF')
        self.notebook.add(self.page_4, text='Graph')
        self.notebook.add(self.page_5, text='Configuration')

        #  File menu setup
        self.file_menu.add_command(label='New', command=None)
        self.file_menu.add_command(label='Save', command=None)
        self.file_menu.add_command(label='Open', command=None)
        self.file_menu.add_command(label='Settings', command=None)
        self.file_menu.add_command(label='Export', command=None)
        self.file_menu.add_command(label='Exit', command=lambda: [self.root.quit])
        self.menu.add_cascade(label='File', menu=self.file_menu)

        # Edit menu setup
        self.edit_menu = Menu(self.menu, tearoff=0)
        self.edit_menu.add_command(label='Cut', command=None)
        self.edit_menu.add_command(label='Copy', command=None)
        self.edit_menu.add_command(label='Paste', command=None)
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)

        self.setup_menu.add_command(label='Calibrate cameras', command=self.launchCalibrationWindow)
        #self.setup_menu.add_command(label='Copy', command=None)
        #self.setup_menu.add_command(label='Paste', command=None)
        self.menu.add_cascade(label='Setup', menu=self.setup_menu)

        # GUI font and colors
        self.DISPPLAYLABEL_WIDTH = 7
        self.WHITE = "White"
        self.GRAY = '#424242'

        # Configure setup
        self.root.config(menu=self.menu)

        # Camera Page: Configure PanedWindows
        self.root_cam_tab = PanedWindow(self.page_1)
        self.root_cam_tab.configure(bg=self.GRAY)
        self.root_cam_tab.pack(fill=BOTH,
                               expand=True)

        self.left_camPaneTabMain = tk.PanedWindow(self.root_cam_tab, orient=VERTICAL, bg=self.GRAY)  # Left side of GUI
        self.root_cam_tab.add(self.left_camPaneTabMain)

        self.top_left = PanedWindow(self.left_camPaneTabMain)
        self.top_left.configure(bg=self.GRAY, relief='groove', borderwidth='2')

        self.bottom_left = PanedWindow(self.left_camPaneTabMain)
        self.bottom_left.configure( bg=self.GRAY, relief='groove', borderwidth='2')


        self.left_camPaneTabMain.add(self.top_left, height=500)
        self.left_camPaneTabMain.add(self.bottom_left, height=250)

        self.midSection_camPaneTabMain = PanedWindow(self.root_cam_tab, orient=VERTICAL, bg='gray40') # Mid GUI
        self.root_cam_tab.add(self.midSection_camPaneTabMain)

        self.top = PanedWindow(self.midSection_camPaneTabMain) # Top Mid GUI
        self.top.configure(bg=self.GRAY)
        self.frame = Frame(self.top, bg=self.GRAY)
        self.top.add(self.frame)
        self.midSection_camPaneTabMain.add(self.top, height=500)
        self.main_label = Label(self.top, text='Camera Views')
        self.main_label.config(height=480, bg=self.GRAY)
        self.main_label.grid(column=0, row=0)

        self.bottom = PanedWindow(self.midSection_camPaneTabMain)
        self.bottom.configure(height=20, bg=self.GRAY)
        self.midSection_camPaneTabMain.add(self.bottom, height=50)

        self.poseFontType = "Arial"
        self.poseFontSize = 14
        self.shipPoseLabel_camPaneTabMain = Label(self.bottom, text="Poses:", bg=self.GRAY, fg=self.WHITE,
                                                  font=(self.poseFontType, self.poseFontSize,"bold"))
        self.shipPoseLabel_camPaneTabMain.grid(column=0, row=0, sticky='w')
        self.dispPoseBunker_camPaneTabMain = Frame(self.bottom)  # , orient=HORIZONTAL)
        self.dispPoseBunker_camPaneTabMain.configure(bg=self.GRAY)
        self.dispPoseBunker_camPaneTabMain.grid(column=0, row=1)

        # Text variables for visualization of movement
        self.translation_values = [DoubleVar(), DoubleVar(), DoubleVar()]
        self.rotation_values = [DoubleVar(), DoubleVar(), DoubleVar()]
        self.boardPose_quality = DoubleVar()

        # Display of variables that represents the movement of the object - XYZ - PITCH YAW ROLL.
        self.x_label = Label(self.dispPoseBunker_camPaneTabMain, text='X-VALUE:', bg=self.GRAY, fg=self.WHITE,
                             font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.x_label.grid(column=0, row=0, sticky='w')
        self.dispX_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.translation_values[0], bg=self.GRAY, fg=self.WHITE,
                                          font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispX_camPaneTabMain.grid(column=1, row=0)
        self.y_label = Label(self.dispPoseBunker_camPaneTabMain, text='Y-VALUE:', bg=self.GRAY, fg=self.WHITE,
                             font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.y_label.grid(column=2, row=0)
        self.dispY_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.translation_values[1], bg=self.GRAY, fg=self.WHITE,
                                          font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispY_camPaneTabMain.grid(column=3, row=0)
        self.z_label = Label(self.dispPoseBunker_camPaneTabMain, text='Z-VALUE:', bg=self.GRAY, fg=self.WHITE,
                             font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.z_label.grid(column=4, row=0)
        self.dispZ_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.translation_values[2], bg=self.GRAY, fg=self.WHITE,
                                          font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispZ_camPaneTabMain.grid(column=5, row=0)
        self.roll_label = Label(self.dispPoseBunker_camPaneTabMain, text='ROLL:', bg=self.GRAY, fg=self.WHITE,
                                font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.roll_label.grid(column=0, row=1, sticky='w')
        self.dispRoll_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=  self.rotation_values[0], bg=self.GRAY, fg=self.WHITE,
                                             font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispRoll_camPaneTabMain.grid(column=1, row=1)
        self.pitch_label = Label(self.dispPoseBunker_camPaneTabMain, text='PITCH:', bg=self.GRAY, fg=self.WHITE,
                                 font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.pitch_label.grid(column=2, row=1)
        self.dispPitch_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.rotation_values[1], fg=self.WHITE,
                                              bg=self.GRAY, font=(self.poseFontType,self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispPitch_camPaneTabMain.grid(column=3, row=1)
        self.yaw_label = Label(self.dispPoseBunker_camPaneTabMain, text='YAW:', bg=self.GRAY, fg=self.WHITE,
                               font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.yaw_label.grid(column=4, row=1)
        self.dispYaw_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.rotation_values[2], bg=self.GRAY, fg=self.WHITE,
                                            font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispYaw_camPaneTabMain.grid(column=5, row=1)
        # Display the quality of board estimation
        self.boardPoseQuality_label = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.boardPose_quality, fg=self.WHITE,
                                            bg=self.GRAY, font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.boardPoseQuality_label.grid(column=7, row=0)
        self.dispBoardPoseQual_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='Q Board:', bg=self.GRAY, fg=self.WHITE,
                                                      font=(self.poseFontType, self.poseFontSize), padx=15, pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispBoardPoseQual_camPaneTabMain.grid(column=6, row=0)

        # Page 3: PDF setup
        # FIXME: If you click on same field twice you can remove text from other fields.
        self.page_3_frame = Frame(self.page_3, bg="#424242")
        # must keep a global reference to these two
        try:
            self.im = Image.open('arucoBoard.png')
            self.im = self.im.resize((300, 300), Image.ANTIALIAS)
            self.ph = ImageTk.PhotoImage(self.im)
            # Need to use ph for tkinter to understand
            self.btn_img = Label(self.page_3_frame,  image=self.ph)
            self.btn_img.pack(side=RIGHT)
        except TclError as e:
            logging.error(str(e))
        self.page_3_frame.pack()
        # Create container for holding board list
        self.boardlist_container = Frame(self.page_3)
        self.boardlist_container.config(padx='10',pady='10',bg=self.GRAY)
        self.boardlist_container.pack(side=BOTTOM)
        self.boardimgs = []
        self.boardimgages = [None,None,None,None,None,None,None,None,None]
        self.page_3_label_frame = Frame(self.page_3_frame, bg=self.GRAY)
        self.page_3_label_frame.configure(relief='groove')
        self.page_3_label_frame.configure(borderwidth='2')

        self.page_3_entry_frame = Frame(self.page_3_frame)
        self.page_3_entry_frame.configure(relief='groove', borderwidth='2')

        self.page_3_label_frame.pack(side=LEFT)
        self.page_3_entry_frame.pack(side=RIGHT)

        self.length = Label(self.page_3_label_frame, text='Length:', bg=self.GRAY, fg=self.WHITE)  # Add text to label
        self.length_entry = Entry(self.page_3_entry_frame)  # Create entry for that label
        vcmd_length = (self.length_entry.register(self.on_validate), '%P')  # Check if input is valid

        self.width = Label(self.page_3_label_frame, text='Width: ',bg=self.GRAY, fg=self.WHITE)
        self.width_entry = Entry(self.page_3_entry_frame)
        vcmd_width = (self.width_entry.register(self.on_validate), '%P')

        self.size = Label(self.page_3_label_frame, text='Size: ',bg=self.GRAY, fg=self.WHITE)
        self.size_entry = Entry(self.page_3_entry_frame)
        vcmd_size = (self.size_entry.register(self.on_validate), '%P')

        self.gap = Label(self.page_3_label_frame, text='Gap: ',bg=self.GRAY, fg=self.WHITE)
        self.gap_entry = Entry(self.page_3_entry_frame, validate='key')
        vcmd_gap = (self.gap_entry.register(self.on_validate), '%P')

        self.length.pack()
        self.length_entry.insert(0, '3')  # Add generic text
        self.length_entry.bind('<Button-1>', self.on_entry_click)  # If clicked on
        self.length_entry.pack()
        self.length_entry.config(validate='key', validatecommand=vcmd_length)

        self.width.pack()
        self.width_entry.insert(0, '3')
        self.width_entry.bind('<Button-1>', self.on_entry_click)
        self.width_entry.pack()
        self.width_entry.config(validate='key', validatecommand=vcmd_width)

        self.size.pack()
        self.size_entry.insert(0, '40')
        self.size_entry.bind('<Button-1>', self.on_entry_click)
        self.size_entry.pack()
        self.size_entry.config(validate='key', validatecommand=vcmd_size)

        self.gap.pack()
        self.gap_entry.insert(0, '1')
        self.gap_entry.bind('<Button-1>', self.on_entry_click)
        self.gap_entry.pack()
        self.gap_entry.config(validate='key', validatecommand=vcmd_gap)

        self.btn_frame = Frame(self.page_3, bg=self.GRAY)
        self.btn_frame.configure(bg='black')
        self.btn_frame.pack()
        self.pdf_btn = Button(self.btn_frame, text='Generate board',
                              command=lambda: [self.createArucoBoard()])
        self.pdf_btn.configure(bg=self.GRAY, fg=self.WHITE)
        self.pdf_btn.pack(side=LEFT)
        self.pdf_btn = Button(self.btn_frame, text='Add to tracking list',
                              command=lambda: [self.exportArucoBoard()])
        self.pdf_btn.configure(bg=self.GRAY, fg=self.WHITE)
        self.pdf_btn.pack(side=LEFT)
        self.pdf_btn = Button(self.btn_frame, text='Save Aruco Board',
                              command=lambda: [self.saveArucoPDF()])
        self.pdf_btn.configure(bg=self.GRAY, fg=self.WHITE)
        self.pdf_btn.pack(side=LEFT)

        Frame(self.btn_frame, width=5,bg=self.GRAY).pack(side=LEFT)
        self.merge_btn = Button(self.btn_frame, text='Merge',
                              command=lambda: [self.doMerging()])
        self.merge_btn.configure(bg=self.GRAY, fg=self.WHITE)
        self.merge_btn.pack(side=LEFT)

        # Page 4: Graph setup
        self.page_4_frame = Frame(self.page_4)
        self.page_4_frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.page_4_frame.configure(relief='groove', borderwidth='2', background=self.GRAY, width=565)

        self.graph_frame = Frame(self.page_4_frame)
        self.graph_frame.configure(background='red')
        self.graph_frame.configure(borderwidth='2')
        self.graph_frame.configure(relief='ridge')
        self.graph_frame.configure(width=750)
        self.graph_frame.configure(height=500)
        self.graph_frame.pack()

        # Buttons in graph page
        self.btn_frame_4 = Frame(self.page_4_frame)
        self.btn_frame_4.pack()
        self.start_pressed = False
        self.btn_plot = tk.Button(self.btn_frame_4)
        self.btn_plot.pack(side=LEFT)
        self.btn_plot.configure(background='#665959',disabledforeground='#911515',foreground='#FFFFFF')
        self.btn_plot.configure(text='Start')
        self.btn_plot.configure(command=lambda: (self.runGraph(),self.hideButton(self.btn_plot)), height=2, width=7)

        self.stop_pressed = False
        self.btn_save =  tk.Button(self.btn_frame_4)
        self.btn_save.pack(side=RIGHT)
        self.btn_save.configure(foreground='#FFFFFF', text='Stop',disabledforeground='#911515',background='#665959')
        self.btn_save.configure(command=lambda: self.showButton(self.btn_plot), height=2, width=7)



        self.camFrameSettingSection = Frame(self.left_camPaneTabMain, bg=self.GRAY, height=500, width=50)
        # Start and stop button setup
        self.start_btn = Button(self.camFrameSettingSection, text='Start', bg='green', fg=self.WHITE
                                ,height=2,width=7,
                                command=lambda: [self.startPoseEstimation()])
        # init_cams_btn = Button(page_1, text='Initialise cameras', command=startClicked)
        self.stop_btn = Button(self.camFrameSettingSection, text='Stop', bg='red', fg=self.WHITE
                               ,height=2,width=7,
                               command=lambda: [self.stopPoseEstimation()])
        self.start_btn.grid(column=0, row=0, pady=10)
        self.stop_btn.grid(column=1, row=0, pady=10)
        # Label to respond if button pushed before VEs have been inited
        self.poseEstimationStartDenied_label = Label(self.camFrameSettingSection,
                                                     text="Please init VEs in config tab first.", bg="#424242")
        self.camFrameSettingSection.configure()
        self.camFrameSettingSection.pack()

        self.availCamsLabel = Label(self.left_camPaneTabMain, text='Available cameras: ',font=("Arial", "12"))
        self.availCamsLabel.configure(bg=self.GRAY,fg=self.WHITE
                                      )
        self.availCamsLabel.pack()

        self.__displayedCameraIndex = tk.IntVar()  # Radio buttons controlling which camera feed to show. negatives means auto.
        self.__displayedCameraIndex.set(-1)

        # Camera selection variable
        tk.Radiobutton(self.left_camPaneTabMain, text="Auto", padx=5, variable=self.__displayedCameraIndex,
                       command=self.setCameraIndexToDisplay, value=-1, bg=self.GRAY, fg='orange',font=("Arial", "12","bold")).pack()

        self.board_label = Label(self.bottom_left, text='Boards', padx=20,bg=self.GRAY, fg=self.WHITE
                                 ,font=("Arial", "12")).pack()

        # Board selection variable setup
        self.boardIndex = tk.IntVar()  # Radio buttons controlling which board to track.
        self.boardIndex.set(0)


        # invoke the button on the return key
        self.root.bind_class('Button', '<Key-Return>', lambda event: event.widget.invoke())

        # remove the default behavior of invoking the button with the space key
        self.root.unbind_class('Button', '<Key-space>')

        # Bool to check if it is full screen or not
        self.state = False



        # Makes full screen possible by pressing F11 and change back by pressing F11 or escape
        self.root.bind('<F11>', self.toggleFullscreen)
        self.root.bind('<Escape>', self.endFullscreen)

        # Setup the config tab

        self.VEConfigUnits = []

        # Set the configPaneTabMain as master of config tab.
        self.configPaneTabMain = PanedWindow(self.page_5, bg='black')
        self.configPaneTabMain.pack(fill=BOTH, expand=True)
        self.configPaneTabMain.configure(bg=self.GRAY)
        # Left section Pane for configuring, Right section for image preview
        self.leftSection_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL, bg='gray80')
        self.configPaneTabMain.add(self.leftSection_configPaneTabMain)
        self.previewSection_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL,bg=self.GRAY)
        self.configPaneTabMain.add(self.previewSection_configPaneTabMain)
        self.configPaneTabMain.configure(bg=self.GRAY)
        #self.page_setup_camconfig
        # Create notebook under setuptab #TODO: Have the notebook in the left section.
        self.configurationtab_notebook = ttk.Notebook(self.leftSection_configPaneTabMain)
        self.page_setup_calib = ttk.Frame(self.configurationtab_notebook)
        self.page_setup_camconfig = ttk.Frame(self.configurationtab_notebook)
        self.configurationtab_notebook.add(self.page_setup_camconfig, text='Camera config')
        self.configurationtab_notebook.add(self.page_setup_calib, text='Calibration')
        self.configurationtab_notebook.pack(fill=BOTH, expand=True)
        self.leftSection_configPaneTabMain.add(self.configurationtab_notebook)

        #self.leftSection_configPaneTabMain.configure(bg=self.GRAY)


        self.setupConfigTab()


        # Setup calibration page:
        self.setupCalibrationPage()

        # Set focus to start button
        self.start_btn.focus()

        # Adds board radio button to the GUI
        # Start it all
        self.root.mainloop()

        # Configuration setup

    def setupConfigTab(self):
        '''
        # Create paned windows for GUI
        :return:
        '''
        #self.midtopSectionLabel_configPaneTabMain = Frame(self.page_setup_camconfig, height=100)
        #self.leftSection_configPaneTabMain.add(self.midtopSectionLabel_configPaneTabMain)
        #self.midtopSectionLabel_configPaneTabMain.configure(bg=self.GRAY)
        #
        #self.rightSectionLabel_configPaneTabMain = Label(self.previewSection_configPaneTabMain, text="right pane")
        #self.previewSection_configPaneTabMain.add(self.rightSectionLabel_configPaneTabMain)
        #self.previewSection_configPaneTabMain.configure(bg=self.GRAY)
        #self.rightSectionLabel_configPaneTabMain.configure(bg=self.GRAY)

        # Configurations for which cams to connect
        self.selectCamIndexesFrame = Frame(self.page_setup_camconfig)
        self.selectCamIndexesFrame.configure(bg=self.GRAY)
        self.selectCamIndexesFrame.pack(fill=BOTH)#.add(self.selectCamIndexesFrame)
        Label(self.selectCamIndexesFrame, text="Hello").grid(row=0,column=0)
        self.selectCamIndexesFrame.configure(relief='groove')
        self.selectCamIndexesFrame.configure(borderwidth='2', pady='10')

        self.leftSection_configPaneTabMain.configure(relief='groove')
        self.leftSection_configPaneTabMain.configure(borderwidth='2')
        self.previewSection_configPaneTabMain.configure(relief='groove')
        self.previewSection_configPaneTabMain.configure(borderwidth='2')

        ''' Create VEConfigUnits that controls all  '''
        self.numbCamsToShow = 5
        for i in range(0,self.numbCamsToShow+1): # Create VEConfigUnits
            # Create VECU fpr given index
            VECU = VEConfigUnit(i,self, self.selectCamIndexesFrame, None, self.setPreviewStatus)
            VECU.start()
            self.VEConfigUnits.append(VECU)

        self.sendCamSelectionButton_configTab = Button(self.page_setup_camconfig, padx = 10, pady = 10,
                                                       text="Apply", bg=self.GRAY, command=self.applyCamList, width=20, fg="white")
        #self.leftSection_configPaneTabMain.add(self.sendCamSelectionButton_configTab)
        self.sendCamSelectionButton_configTab.pack(fill=BOTH)
        deadspace2 = Frame(self.leftSection_configPaneTabMain, height=100, bg=self.GRAY)
        self.leftSection_configPaneTabMain.add(deadspace2)
        # List for VEs stored in GUI
        self.prelimVEList = []

        #Container for preview image
        self.imgHolder = Label(self.previewSection_configPaneTabMain)
        self.imgHolder.image = None
        self.imgHolder.pack()

    def setupCalibrationPage(self):
        self.mainframe_cabtab = Frame(self.page_setup_calib, bg=self.GRAY)#, width=1000, height=1000, bg=self.GRAY)
        self.mainframe_cabtab.grid(row=0,column=0)
        self.launchCalibrationWindow()


    def launchCalibrationWindow(self):
        self.allowToCalibrate = False
        if not self.poseEstimationIsRunning: # Can't calibrate while running.
            self.allowToCalibrate = True
        if self.allowToCalibrate:
            logging.debug('Going to create a TopLevel window now')
            self.prepareCalib_mainFrame = Frame(self.mainframe_cabtab, height=1000, width=1000, bg=self.GRAY)
            warningText = 'Please read this! \n - Doing calibration is not necessary for daily use. \n' \
                          '- It\'s only necessary when using new cameras, or changing the lenses on the old. \n' \
                          '- For guidance on calibration, please refer to the user manual. '
            self.warningLabel_calibtab = Label(self.mainframe_cabtab, bg='#424200', fg=self.WHITE, text=warningText)
            self.warningLabel_calibtab.grid(row=0, column=0)
            self.prepareCalib_mainFrame.grid(row=1,column=0)
            self.selectCamToCalib_label = Label(self.prepareCalib_mainFrame, text='Select camera to calibrate',
                                                font=('Arial', 14), bg=self.GRAY, fg=self.WHITE)
            self.selectCamToCalib_label.grid(row=1,column=0, columnspan=2)
            # OptionMenu for selecting cam to calib.
            self.camToCalib_var = IntVar()
            self.camToCalib_var.set(0)
            calibCamToList = []
            for i,n in enumerate(range(self.numbCamsToShow)):
                calibCamToList.append(i)
            self.possibleCamsToCalibOption = OptionMenu(self.prepareCalib_mainFrame, self.camToCalib_var,
                                                        *calibCamToList, command=self.setCamToCalib)
            self.possibleCamsToCalibOption.config(highlightbackground=self.GRAY,bg=self.GRAY, fg=self.WHITE)
            self.possibleCamsToCalibOption.grid(row=1,column=2, padx=10, pady=10)


    def setCamToCalib(self, cameraIndex):
        '''
        We have choosen a value, and want to display connection options and status for the camera.
        Also displaying configurations for calibration process.
        :param cameraIndex: The choosen camera index.
        :return:
        '''
        logging.info('Selected cam with value: ' + str(self.camToCalib_var.get()))
        self.camIndexToCalibrate = self.camToCalib_var.get()
        self.vecuToCalib = self.getVEConfigUnitById(cameraIndex)
        if self.vecuToCalib is not None:
            logging.debug("Id of given VECU: "+ str(self.vecuToCalib.getIndex()))
            state = self.vecuToCalib.getState()
            if self.calibConnectionFrame is not None:
                try:
                    logging.info('Removing widget with id ' + str(self.calibConnectionFrame.winfo_id()) )
                except TclError:
                    logging.info('Dumb error.')
                self.calibConnectionFrame.grid_remove()
            self.calibConnectionFrame = self.vecuToCalib.getCalibConnectionFrame(self.prepareCalib_mainFrame)
            logging.debug('Correct connection_frame is given.')
            if self.calibConnectionFrame is not None:
                logging.debug('Winfo_:parent: ' + self.calibConnectionFrame.winfo_parent())
                logging.debug('Winfo_id: ' + str(self.calibConnectionFrame.winfo_id()))
                self.calibConnectionFrame.grid(row=3,column=0,columnspan=2)
        # Set whether to use film or images
        calibOptions = ['Images', 'Film']
        self.calibType_var = StringVar()
        self.calibType_var.set('Film')
        self.calibOptions = OptionMenu(self.prepareCalib_mainFrame, self.calibType_var, *calibOptions, command=self.doCalib)
        self.possibleCamsToCalibOption.config(highlightbackground=self.GRAY, bg=self.GRAY, fg=self.WHITE)
        deadSpace11 = Frame(self.prepareCalib_mainFrame, height=20,bg=self.GRAY).grid(row=4,column=1)
        self.doCalibButton = Button(self.prepareCalib_mainFrame, text="Calibrate",bg=self.GRAY,fg=self.WHITE
                                    ,command=self.doCalib, padx=5, pady=5)
        self.selectCamToCalib_label = Label(self.prepareCalib_mainFrame, text='Number of secs/frames',
                                            font=('Arial', 11), bg=self.GRAY, fg=self.WHITE)
        self.lengthOfCalib = Entry(self.prepareCalib_mainFrame,bg=self.GRAY,fg=self.WHITE)
        self.lengthOfCalib.insert(0,'12')
        self.calibName_label = Label(self.prepareCalib_mainFrame, text='Name of calibration file, 2 letters.',
                                            font=('Arial', 11), bg=self.GRAY, fg=self.WHITE)
        self.calibName = Entry(self.prepareCalib_mainFrame, bg=self.GRAY, fg=self.WHITE)
        self.calibName.insert(0, 'XB')
        # Add option for setting number of corners on checkboard
        self.verticalCBCorners_label = Label(self.prepareCalib_mainFrame, text='Inner CB corners y',
                                            font=('Arial', 11), bg=self.GRAY, fg=self.WHITE)
        self.verticalCBCorners_box = Spinbox(self.prepareCalib_mainFrame, from_=1, to=25, bg=self.GRAY, fg=self.WHITE)
        self.verticalCBCorners_box.insert(END, '7')
        self.horizontalCBCorners_label = Label(self.prepareCalib_mainFrame, text='Inner CB corners x',
                                            font=('Arial', 11), bg=self.GRAY, fg=self.WHITE)
        self.horizontalCBCorners_box = Spinbox(self.prepareCalib_mainFrame, from_=1, to=25, bg=self.GRAY, fg=self.WHITE)
        self.horizontalCBCorners_box.insert(END, '9')
        # Place the widgets:
        self.possibleCamsToCalibOption.grid(row=1, column=3, padx=5, pady=5)
        self.selectCamToCalib_label.grid(row=5, column=0, padx=5, pady=5)
        self.lengthOfCalib.grid(row=5,column=1, padx=5, pady=5)
        self.calibName_label.grid(row=6, column=0, padx=5, pady=5)
        self.calibName.grid(row=6, column=1, padx=5, pady=5)
        self.verticalCBCorners_label.grid(row=7, column=0, padx=5, pady=5)
        self.verticalCBCorners_box.grid(row=7, column=1, padx=5, pady=5)
        self.horizontalCBCorners_label.grid(row=8, column=0, padx=5, pady=5)
        self.horizontalCBCorners_box.grid(row=8, column=1, padx=5, pady=5)
        #self.doExitCalibButton.grid(row=10,column=0, padx=10, pady=10)
        self.doCalibButton.grid(row=10,column=3, padx=10, pady=10)

    def doCalib(self):
        '''
        Do the calibration process, if filename is correctly.
        Create a thread to record the film.
        :return:
        '''
        calibFileName = str(self.calibName.get())
        if len(calibFileName) == 2:
            logging.debug('Starting doing calib.')
            calibType = self.calibType_var.get() # Either 'Film' or 'Images'
            VEtoCalib = self.vecuToCalib.getVE()
            if VEtoCalib is None: # Not already created
                # Create VE
                self.vecuToCalib.setState(1)
            calibLength = int(self.lengthOfCalib.get())
            if calibType == 'Film':
                logging.debug('We are calibrating with film.')
                calibThread = threading.Thread(target=self.takeUpCalibrationVideo, args=(calibLength, VEtoCalib))
                calibThread.start()
        else:
            logging.debug('The filename is ' + str(len(calibFileName)) + ' long. The name is ' + calibFileName)
            self.showErrorBox('The name of the calibration-file must be precisely 2 letters/numbers long! ')

    def takeUpCalibrationVideo(self, lengthSec, VE):
        '''
        Running in own thread.
        Record the video, and send it to IntrinsicCalibration-class to do calibration.
        :param lengthSec:
        :param VE:
        :return:
        '''
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        videoName = str(self.calibName.get())
        out = cv2.VideoWriter(('calibVideos/'+videoName + '.avi'), fourcc, 20.0, (640, 480))
        startTime = time.time()
        notAbort = True
        while notAbort:
            VE.getCam().grabFrame()
            ret, frame = VE.getCam().retrieveFrame()
            #frame = VE.getFrame()
            print('Frame: ' + str(frame))
            #ret, frame = cap.read()
            if frame is not None:
                #frame = cv2.flip(frame, 0)
                # write the flipped frame
                out.write(frame)
                cv2.imshow('frame', frame)
                cv2.waitKey(40)
                timeElapsed = time.time() - startTime
                print('Time elapsed: ' + str(timeElapsed))
                print('Wanted length: ' + str(lengthSec))
                if int(timeElapsed) > lengthSec:
                    notAbort = False
        # Calibrate the video
        camParam = videoCalibration(videoName, debug=True)
        #Destroy the calibration window.
        self.vecuToCalib.updateOptionMenu()

    def getVEConfigUnitById(self, ID):
        vecu = None
        for VECU in self.VEConfigUnits:
            currID = VECU.getIndex()
            logging.debug('CurrID: '+ str(currID))
            if currID == ID:
                logging.debug('Returning with ID ' +str(currID))
                return VECU
        logging.error("No VECU found on given index.")
        return vecu

    def doMerging(self):
        '''
        Create a popup window who handles mergingbetween boards.
        '''
        try:
            self.boardIDlist = set(self.arucoBoardUnits.keys())
            assert (len(self.boardIDlist) > 1), "You need at least 2 boards in order to initialize a merge"
            assert self.poseEstimationIsRunning, "Camera feed needs to be running before merging."
        except AssertionError as err:
            self.showErrorBox(err)
            return
        self.merge_window = Toplevel()
        self.merge_window.title("Merge boards")
        self.merge_topframe = Frame(self.merge_window, bg=self.GRAY)
        self.merge_frame = Frame(self.merge_topframe, bg=self.GRAY)
        self.merge_topframe.pack()
        self.merge_frame.pack()

        self.intro_text = Text(self.merge_frame, bg=self.GRAY, fg=self.WHITE
                               )
        text = "This is the merger. Here you can do so several board markers acts as one, thus gives " \
               "you much better accuracy. This because we use find the best correlation between multiple cameras and " \
               "multiple markers to " \
               " provide good accuracy in all directions. \n" \
               "To start with, select the main marker. This marker MUST BE VISIBLE TO ALL OTHER MARKERS that want to " \
               "be merged during the merging process. During the process, the main marker, and the marker(s) that gonna " \
               "be merged, should be visible for the choosen merger camera.   "
        self.intro_text.insert(END,text)
        self.intro_text.grid(column=0, row=0, columnspan=2)
        self.main_cam_label = Label(self.merge_frame, text='Main marker:',bg=self.GRAY,fg="white", height=5)
        self.main_cam_label.grid(column=0,row=1)

        self.main_board_var = IntVar()
        self.main_board_choice_id = 0
        self.main_board_choice = OptionMenu(self.merge_frame, self.main_board_var, *self.boardIDlist, command=self.setMainMergerBoard)
        self.main_board_choice.config(bg="#424242", fg="white", highlightbackground=self.GRAY)
        self.main_board_choice.setvar("Choose")
        self.main_board_choice.grid(row=1, column=1)
        self.packer = Frame(self.merge_frame, bg=self.GRAY,width=150, height=30)
        self.packer.grid(row=3, column=0, columnspan=2)
        self.abort_btn = Button(self.packer, text='Abort', bg=self.GRAY, fg=self.WHITE
                                , command=self.merge_window.destroy)
        self.next_btn = Button(self.packer, text='Next',bg=self.GRAY, fg=self.WHITE
                               , command=self.doMergeProcess)
        self.abort_btn.pack(side=LEFT,pady=10,padx=10)
        self.next_btn.pack(side=RIGHT,pady=10,padx=10)

    def doMergeProcess(self):
        """
        Opens the merge window and starts the merging process
        :return: None
        """
        check_button_states = self.getCheckButtonList(self._sub_board_checkbutton_states)
        try:
            assert True in check_button_states.values(), "Please select at least one board to merge with."
        except AssertionError as err:
            self.showErrorBox(err)
            return
        main_board_index = self.main_board_var.get()
        self.sub_board_indicies = [ key for key in self.available_sub_boards if check_button_states[key]]

        self.merge_frame.pack_forget()
        self.mergeprocess_frame = Frame(self.merge_topframe, bg="#424242")
        self.mergeprocess_frame.pack()
        # Add image showing the merge process, to be updated
        self.image_frame = Frame(self.mergeprocess_frame, bg=self.GRAY)
        self.image_frame.grid(row=0,column=0)
        self.merge_image = None # = ImageTk.PhotoImage(Image.open("True1.gif"))
        self.panel = Label(self.mergeprocess_frame, image=self.merge_image)
        self.panel.grid(row=0,column=0)

        # Show merge quality and some options
        self.info_frame = Frame(self.mergeprocess_frame, bg=self.GRAY)
        self.info_frame.grid(row=0,column=1)
        Label(self.info_frame, text="Quality of merge: ", bg=self.GRAY, fg=self.WHITE
              ).grid(row=0,column=0)
        self.mergeBoardProgressbarsList = dict()
        n = 0
        for n, board_index in enumerate(self.sub_board_indicies):
            Label(self.info_frame, text=("Board " + str(board_index)), bg=self.GRAY, fg=self.WHITE
                  ).grid(row=n + 1, column=0)
            pb = ttk.Progressbar(self.info_frame, value=0, maximum=1, orient="horizontal", length=100,
                                 mode="determinate")
            pb.grid(row=n + 1, column=1)
            self.mergeBoardProgressbarsList[board_index] = pb
        self.cancel_btn = Button(self.info_frame, text='Abort', bg=self.GRAY, fg=self.WHITE
                                 ,
                                command=self.merge_window.destroy)
        self.finish_btn = Button(self.info_frame, text='Finish', bg=self.GRAY, fg=self.WHITE
                                 , command=self.mergeProcessFinished)
        # self.abort_btn = Button(self.packer, bg=self.GRAY, fg=self.WHITE
        # )
        self.cancel_btn.grid(row=n+2,column=0,pady=10, padx=10)
        self.finish_btn.grid(row=n+2,column=1, pady=10, padx=10)
        self.connector.startMerge(main_board_index, self.sub_board_indicies, self.displayMergingQuality,
                                  self.displayImageInMerger)

    def mergeProcessFinished(self):
        """
        Finishes the merging process.
        :return:
        """
        try:
            self.connector.setImageDisplayFunction(self.displayFrameInMainWindow)
            self.connector.finishMerge()
        except AssertionError as err:
            self.showErrorBox(err)
            return
        while self.connector.getMergerBoards() is None:
            time.sleep(0.1)
        mergerBoards = self.connector.getMergerBoards()
        newBoard = mergerBoards["merged_board"]
        oldBoards = [mergerBoards["main_board"]] + mergerBoards["sub_boards"]
        self.boardIndex.set(newBoard.ID)
        self.setBoardIndexToDisplay()
        self.merge_window.destroy()
        for board in oldBoards:
            self.removeBoardWidgetFromGUI(board)
            self.removeBoardButton(board.ID)
        self.addBoardWidgetToGUI(newBoard)
        self.addBoardButton(newBoard)

    def exportArucoBoard(self):
        """
        Adds an aruco board to the pushed boards list, to make it accessible to external objects.
        :return: None
        """
        self.connector.addBoard(self.userBoard)
        self.addBoardWidgetToGUI(self.userBoard)
        self.addBoardButton(self.userBoard)


    def displayMergingQuality(self, qualityList):
        """
        Displays the quality of the merge in the merger window
        :param qualityList: A list of qualities
        :return:
        """
        for sub_board_index, q in zip(self.sub_board_indicies, qualityList):
            pb = self.mergeBoardProgressbarsList[sub_board_index]
            pb.config(value=q)

    def displayImageInMerger(self, frame):
        """
        Displays an image frame in the merger window. Pass this function to where
        :param frame: The cv2 image frame to display
        :return:
        """
        try:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except TypeError:
            image = np.zeros((640, 480, 3), dtype=np.uint8)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.panel.configure(image=image)
        self.panel.image = image

    def setMainMergerBoard(self, value):
        self.available_sub_boards = copy.copy(self.boardIDlist)
        self.available_sub_boards.remove(self.main_board_var.get())
        logging.debug("Value: "+str(value))
        self.child_markers_label = Label(self.merge_frame, text="Markers to merge with:", fg="white",bg=self.GRAY)
        self.child_markers_label.grid(row=2,column=0)
        self.main_mergerboard = value
        self.cb_merger_frame = Frame(self.merge_frame)
        for widg in self.cb_merger_frame.grid_slaves():
            widg.grid_forget()
        self._sub_board_checkbutton_states = dict()
        self.cb_merger_frame.grid(row=2, column=1)
        for boardID in self.available_sub_boards:
            self._sub_board_checkbutton_state = BooleanVar()  # Variable to hold state of
            self._sub_board_checkbutton_state.set(False)
            self._sub_board_checkbutton_states[boardID] = self._sub_board_checkbutton_state
            self._cb = Checkbutton(self.cb_merger_frame, text=str(boardID),  # str(self._id),
                                   fg="black", variable=self._sub_board_checkbutton_states[boardID],
                                   bg=self.GRAY, width=12)  # Checkbutton
            self._cb.grid(row=boardID)

    def applyCamList(self):
        '''
        Collect all VEs to be sent to PE for PoseEstimation, and send it to connector.
        :return:
        '''
        self.VEsToSend = [] # List of VEs to send to PoseEstimator
        for VECU in self.VEConfigUnits:
            # Check if this VE should be included
            include = VECU.getIncludeStatus()
            if include:
                VECU_VE = VECU.getVE()
                VECU.setDoPreviewState(False)
                if VECU_VE is not None:
                    # VE already created
                    # Include the VC
                    self.VEsToSend.append(VECU_VE)
                    VECU.setState(6)
                else: # VE not already made, try to make a new.
                    try:
                        index = VECU.getIndex()
                        VE = VisionEntity(index)
                        self.VEsToSend.append(VE)
                        VECU.setState(6) # Set status as PE running
                    except CamNotOpenedException as e:
                        msg = "Failed to open camera on {0}. Not running in PE".format(VECU.getIndex())
                        logging.error(msg)
                        VECU.setIncludeInPEbool(False) # Deselect checkbutton
                        VECU.setState(9)
        if self.VEsToSend: # is not empty
            self.anyCameraInitiated = True
            self.poseEstimationStartDenied_label.grid_forget() # Remove eventual error warning
            self.connector.collectGUIVEs(self.VEsToSend) # Send them to GUI
            self.updateCamlist(self.VEsToSend)

    def setCameraIndexToDisplay(self):
        self.connector.setCameraIndex(self.__displayedCameraIndex.get())

    def resetCamExtrinsic(self):
        '''
        Reset the cam extrinsic matrixes to the current frame point.
        # TODO: Use stack to indicate job done? Add button to GUI.
        :return:
        '''
        self.connector.resetCameraPositions()

    def displayFrameInMainWindow(self, frame):
        """
        Displays a frame in the main window of the GUI.
        :return:
        """
        try:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.main_label.configure(image=image)
            self.main_label.image = image
        except AttributeError as e:
            logging.error(str(e))
        except cv2.error as e:
            logging.error(str(e))

    def saveFrame(self):
        '''
        Save a single frame from video feed
        :return: jpg
        '''
        cv2.imwrite('images/frame%d.jpg' % self.counter, self.imageFrame)

    def createArucoBoard(self):
        """
        Generates and stores an aruco board internally in the GUI. Displays board preview in pdf-tab.
        :return:
        """
        try: # Try to create board
            length_value = self.length_entry.get()
            length_value = int(length_value)
            width_value = self.width_entry.get()
            width_value = int(width_value)
            size_value = self.size_entry.get()
            size_value = int(size_value)
            gap_value = self.gap_entry.get()
            gap_value = int(gap_value)

            self.userBoard = ArucoBoard(board_height=length_value, board_width=width_value, marker_size=size_value,
                                        marker_gap=gap_value)
            self.connector.setBoardIndex(0)
            #self.connector.PE.addBoard(self.userBoard)
            self.ph = self.userBoard.getBoardImage((300, 300))
            self.ph = cv2.cvtColor(self.ph, cv2.COLOR_BGR2RGB)
            self.ph = Image.fromarray(self.ph)
            self.ph = ImageTk.PhotoImage(self.ph)
            self.btn_img.configure(image=self.ph)
        except ValueError as e: # Invalid values entered, try again
            logging.error(str(e))
            self.userBoard = None
            showinfo("Error", "Please insert insert whole numbers in the boxes to create board.")

    def exportArucoBoard(self):
        """
        Adds an aruco board to the pushed boards list, to make it accessible to external objects.
        :return: None
        """
        if self.userBoard is not None:
            # We have 'generated' the board.
            self.connector.addBoard(self.userBoard)
            self.addBoardWidgetToGUI(self.userBoard)
            self.addBoardButton(self.userBoard)
            self.anyBoardsInitiated = True
        else:
            # Board not generated
            showinfo('Error', "Please 'generate' the board first.")

    def addBoardWidgetToGUI(self, board):
        """
        Adds a board widget
        :param board:
        :return:
        """
        try:
            ABU = ArucoBoardUnit(board, self.boardlist_container)
            self.arucoBoardUnits[board.ID] = ABU
        except cv2.error as e:
            logging.error("Can't create that many boards, need to expand dictionary!")
            logging.error(str(e))

    def removeBoardWidgetFromGUI(self, board):
        """
        Removes board from the GUI and from the arucoboardUnits-list.
        :param board: The board to remove from GUI.
        :return: None
        """
        self.arucoBoardUnits[board.ID].removeBoard()
        del self.arucoBoardUnits[board.ID]

    def saveArucoPDF(self):
        '''
        Return values from entry and send it to the arucoPoseEstimator
        :return:None
        '''
        if self.userBoard is not None:
            self.userBoard.writeBoardToPDF()

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
        if self.length_entry.get() == 'Length':
            self.length_entry.delete(0, 'end')  # delete all the text in the entry
            self.length_entry.insert(0, '')  # Insert blank for user input
            self.length_entry.configure(foreground='black')
        elif self.width_entry.get() == 'Width':
            self.width_entry.delete(0, 'end')  # delete all the text in the entry
            self.width_entry.insert(0, '')  # Insert blank for user input
            self.width_entry.configure(foreground='black')
        elif self.size_entry.get() == 'Size':
            self.size_entry.delete(0, 'end')  # delete all the text in the entry
            self.size_entry.insert(0, '')  # Insert blank for user input
            self.size_entry.configure(foreground='black')
        elif self.gap_entry.get() == 'Gap':
            self.gap_entry.delete(0, 'end')  # delete all the text in the entry
            self.gap_entry.insert(0, '')  # Insert blank for user input
            self.gap_entry.configure(foreground='black')

    def graphPose(self, pose):
        """
        Adds pose to graph and displays it in graph window
        :param pose:  Pose to graph
        :return:
        """
        raise NotImplementedError

    def displayQualityInTrackingWindow(self, quality):
        """
        Displays the board quality in tracking window
        :param quality:
        :return: None
        """
        displayedQuality = round(quality, 2)
        self.boardPose_quality.set(displayedQuality)

    def displayPoseInTrackingWindow(self, pose):
        """
        Displays a pose in tracking window.
        :param pose:
        :return: None
        """
        evec, tvec = pose
        if tvec is not None:
            for pos, translation_value, translation_value_list in zip(tvec, self.translation_values, self.translation_value_lists):
                translation_value_list.append(pos)
                if len(translation_value_list) >= 10:
                    del translation_value_list[0]
                translation_value.set(round(sum(translation_value_list)/len(translation_value_list), 2))
        else:
            for value in self.translation_values:
                value.set(0.0)
        if evec is not None:
            for rot, value in zip(evec, self.rotation_values):
                value.set(round(rot, 2))
        else:
            for value in self.rotation_values:
                value.set(0.0)

    def plotGraph(self, poses, frame):
        '''
        Send position for the board to GUIDataPlotting and plot pos on graph
        :param poses:
        :param frame:
        :return:
        '''
        self.modelPoses = poses
        self.imageFrame = frame
        boardIndex = self.boardIndex.get()
        if poses:
            evec, tvec = poses[boardIndex]
            x, y, z = tvec
            x1 = 0
            y1 = 0
            z1 = 0
            try:
                if tvec is not None and x is not x1 and y is not y1 and z is not z1:
                    GUIDataPlotting.plotXYZ(frame, x, y, z)
                    x=x1
                    y=y1
                    z=z1
                else:
                    pass
            except TypeError:
                print('test')

    def startPoseEstimation(self):
        """
        Starts the pose estimator
        :return: None
        """
        try:
            logging.debug("Attempting to start pose estimation from GUI")
            assert self.anyCameraInitiated and self.anyBoardsInitiated, "No cameras initialized. " \
                                                                        "Please initialize camera in config-section"
            self.connector.startPoseEstimation(self.displayFrameInMainWindow, self.displayPoseInTrackingWindow,
                                               self.displayQualityInTrackingWindow)
            self.poseEstimationIsRunning = True
        except AssertionError as err:
            self.showErrorBox(err)
            return

    def stopPoseEstimation(self):
        """
        Stops the pose estimator
        :return: None
        """
        self.connector.stopPoseEstimation()
        self.poseEstimationIsRunning = False
        logging.debug("Stop signal sent.")

    def checkPreviewStatus(self):
        """
        Check whether one of the VECU has requested to do preview. If so return index
        :return:
        """
        if self.VEConfigUnits: # Only do if not empty.
            for VECU in self.VEConfigUnits:
                doPrev = VECU.getDoPreviewState()
                if doPrev:
                    id = VECU.getIndex()
                    return id

    def setPreviewStatus(self, index):
        '''
        Takew commands from VECU and organise so image preview is happening.
        :param index: Index for camera to preview. Remove the preview if index is -1.
        :return:
        '''
        logging.debug("Inside.")
        if index >= 0:
            # Show preview
            if self.imgHolder.image is not None:
                # Remove earlier preview, just because
                self.imgHolder.configure(image='')
                self.imgHolder.image = None
            self.showPreviewImage(index)
        elif index is -1:
            # Hide preview
            self.imgHolder.configure(image='')
            self.imgHolder.image = None

    def showPreviewImage(self, index):
        '''
        Show preview video-feed from camera on given index.
        :param index: Index of cam to preview
        :return: None
        '''
        logging.debug("Index to preview:"+ str(index))
        if index is not -1 and index is not None:
            try:
                VECU = self.getVECUByIndex(index)
                VE = VECU.getVE()
                VE.grabFrame()
                _, frame = VE.retrieveFrame()
                try:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)
                    self.imgHolder.configure(image=image)
                    self.imgHolder.image = image
                except cv2.error as e:
                    logging.error(str(e))
            except AttributeError as e:
                # VE not found or something.
                # TODO: Change so this is a impossible error to hit. Hard to change cause threading etc.
                msg = str(e) + " \n Probably caused by shutting down preview."
                logging.error(str(e))

    def getVECUByIndex(self, index):
        for VECU in self.VEConfigUnits:
            if index is VECU.getIndex():
                return VECU
        return None

    def addBoardButton(self, userBoard):
        """
        Adds a radio button to the board list in the side panel.
        :return: None
        """
        id = userBoard.ID
        buttonText = "Board " + str(id)
        if id in self.boardButtons:
            logging.error("Attemptet to add board that already existed in list.")
            return
        button = tk.Radiobutton(self.bottom_left, text=buttonText, padx=5, bg=self.GRAY, fg='Orange',font=("Arial", "12","bold"),
                                    command=self.setBoardIndexToDisplay, variable=self.boardIndex, value=id)
        self.boardButtons[id] = button
        self.boardButtons[id].pack()

    def removeBoardButton(self, boardID):
        """
        Removes a radio button from the board list in the side panel and from the board button dictionnary
        :param boardID: Identifier of board and button that should be removed
        :return:None
        """
        self.boardButtons[boardID].pack_forget()
        del self.boardButtons[boardID]

    def setBoardIndexToDisplay(self):
        boardIndex = self.boardIndex.get()
        self.connector.setBoardIndex(boardIndex)

    def updateCamlist(self, VElist):
        """
        Updates the camera list to match the input camlist.
        :param camlist: List of indexes of cameras to add.
        :return: None
        """
        if VElist is None:
            logging.debug("CamIDlist is empty. No buttons were added.")
            return
        for VE in VElist:
            camID = VE.getCam().getSrc()
            if not self.camIndexesDisplayed[camID]: # Not already placed
                buttonText = "Camera " + str(camID)
                button = tk.Radiobutton(self.left_camPaneTabMain, text=buttonText, padx=5,
                                        font=("Arial", "12", "bold"),
                                        command=self.setCameraIndexToDisplay, variable=self.__displayedCameraIndex,
                                        value=camID, bg='#424242', fg='Orange')
                self.cameraButtonList.append(button)
                self.cameraButtonList[-1].pack()

    def toggleFullscreen(self, event=None):
        '''
        Toggle full screen on GUI
        :param event: None
        :return: 'break'
        '''
        self.state = not self.state  # Just toggling the boolean
        self.root.attributes('-fullscreen', self.state)
        return 'break'

    def endFullscreen(self, event=None):
        '''
        End full screen
        :param event: None
        :return: 'break'
        '''
        self.state = False
        self.root.attributes('-fullscreen', False)
        return 'break'

    def runGraph(self):
        '''
        Setup for graph frame and variables needed to show x-y-z.
        :param window: The frame you want to plot the graph in.
        :return: None
        '''
        #if self.x_graph or self.y_graph or self.z_graph is None:
        #    graph_x = 0.0
        #    graph_y = 0.0
        #    graph_z = 0.0
        #else:
        t_data, x_data, y_data, z_data = [], [], [], []

        figure = plt.figure()
        self.ax = figure.subplots(3, 1, sharex=True, sharey=True)
        line, = self.ax[0].plot(t_data, x_data, 'r')
        line2, = self.ax[1].plot(t_data, y_data, 'c')
        line3, = self.ax[2].plot(t_data, z_data, '-')
        start_time = time.time()

        def update(frame):
            elapsed_time = time.time() - start_time
            t_data.append(elapsed_time)
            x_data.append(self.x_graph)
            y_data.append(self.y_graph)
            z_data.append(self.z_graph)
            line.set_data(t_data, x_data)
            line2.set_data(t_data, y_data)
            line3.set_data(t_data, z_data)
            figure.gca().relim()
            figure.gca().autoscale_view()

        figure.suptitle('Movement')
        self.ax[0].set_ylabel('X')
        self.ax[1].set_ylabel('Y')
        self.ax[2].set_ylabel('Z')
        self.ax[2].set_xlabel('Time (s)')
        self.animation = FuncAnimation(figure, update, interval=100)

        def _pause(self,event):
            if self.stop_pressed:
                self.animation.event_source.stop()
                self.stop_pressed = False
            else:
                self.animation.event_source.start()
                self.stop_pressed = True
        plt.show()

    def hideButton(self, button):
        '''
        Hide the chosen button if you do not want it to be pressed until some other
        button is pressed first.
        :param button: The button you want to hide
        :return: None
        '''
        button.lower()
        self.stop_pressed = True

    def showButton(self, button):
        '''
        Show a hidden button
        :param button: Button you want to show
        :return:
        '''
        button.lift()
        self.stop_pressed = False

    def plotGraphPressed(self):
        self.start_pressed = True

    def showErrorBox(self, err):
        """
        Displays an error in a pop up box
        :param args: The traceback to the error to display
        :return: None
        """
        print(err)
        showerror(title='Error', message=err)

    def getCheckButtonList(self, varList):
        """
        Takes a dict of tkinter Var-variables and creates a new dict of the datatype stored
        :param list: the list to get
        :return: A list of output variables
        """
        return {key: value.get() for key, value in varList.items()}
