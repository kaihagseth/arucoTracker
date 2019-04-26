import logging
import threading
import tkinter as tk
from tkinter import *
from tkinter import Menu
from tkinter import ttk
from tkinter.messagebox import showinfo

import cv2
import ttkthemes
from PIL import ImageTk, Image

from GUI.VEConfigUnit import VEConfigUnit
from GUI.ArucoBoardUnit import ArucoBoardUnit
from VisionEntityClasses.VisionEntity import VisionEntity
from VisionEntityClasses.arucoBoard import arucoBoard
from VisionEntityClasses.helperFunctions import stackChecker
from exceptions import CamNotOpenedException

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import time

class GUIApplication(threading.Thread):
    global length

    def __init__(self, connector):
        threading.Thread.__init__(self)
        self.connector = connector
        self.arucoBoardUnits = []
        msg = 'Thread: ', threading.current_thread().name
        logging.info(msg)
        self.camIndexesDisplayed = [False, False, False, False, False, False] # Set corresponding index for what indexes are displayed
        # Camera variables
        self.counter = 0

        # Observer technique: Tell connector which function to call when updating fields.
        self.connector.setGUIupdaterFunction(self.updateGUIFields)
        self.connector.setGUIStreamerFunction(self.showFindPoseStream)

        # Fields written to by external objects. Should only be read in this object.
        self.frame = None           # Image frame to be shown in camera window.
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
        self.poseEstimationStartAllowed = False # Only True if we have applied some VEs to run with in configtab

        # Button lists
        self.boardButtonList = []
        self.cameraButtonList = []
        self.cameraButtonIndexList = []

    def run(self):
        '''
        Run the main application.
        TODO: Please add comments
        '''
        self.camIDInUse = 0

        # Set up main window.

        self.root = Tk()
        #self.root.style = ttkthemes.ThemedStyle()
        self.root.title('Boat Pose Estimator')
        self.root.geometry('850x750')
        #self.root.style.theme_use('black')
        # Create menu
        self.menu = Menu(self.root)
        self.file_menu = Menu(self.menu, tearoff=0)


        #Testing some Style stuff
        s = ttk.Style()
        s.theme_create("MyStyle", parent="alt",
                       settings={
                                "TNotebook":
                                    {"configure":
                                         {"tabmargins": [2, 5, 2, 0],
                                          "background": "#424242",
                                          "foreground": "red"
                                         }
                                    },
                                "TNotebook.Tab":
                                    {"configure":
                                         {"padding": [50, 10],
                                          "font": ('URW Gothic L', '11'),
                                          "background": "#424242",
                                          "foreground": "white"
                                         },
                                    "map": {"background": [("selected", "#424242")],

                                             "expand": [("selected", [1, 1, 1, 0])]}
                                   }
                                }
                       )
        s.theme_use("MyStyle")

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
        self.file_menu.add_command(label='Exit', command=lambda: [self.root.quit])
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
        self.root_cam_tab = PanedWindow(self.page_1)
        self.root_cam_tab.configure(bg='#424242')
        self.root_cam_tab.pack(fill=BOTH,
                               expand=True)

        self.left_camPaneTabMain = tk.PanedWindow(self.root_cam_tab, orient=VERTICAL, bg='#424242')  # Left side of GUI
        self.root_cam_tab.add(self.left_camPaneTabMain)

        self.top_left = PanedWindow(self.left_camPaneTabMain)
        self.top_left.configure(bg='#424242', relief='groove', borderwidth='2')

        self.bottom_left = PanedWindow(self.left_camPaneTabMain)
        self.bottom_left.configure( bg='#424242', relief='groove', borderwidth='2')


        self.left_camPaneTabMain.add(self.top_left, height=500)
        self.left_camPaneTabMain.add(self.bottom_left, height=250)

        self.midSection_camPaneTabMain = PanedWindow(self.root_cam_tab, orient=VERTICAL, bg='gray80') # Mid GUI
        self.root_cam_tab.add(self.midSection_camPaneTabMain)

        self.top = PanedWindow(self.midSection_camPaneTabMain) # Top Mid GUI
        self.top.configure(bg='#424242')
        self.frame = Frame(self.top)
        self.top.add(self.frame)
        self.midSection_camPaneTabMain.add(self.top, height=500)
        self.main_label = Label(self.top, text='Camera Views')
        self.main_label.config(height=480, bg='#424242')
        self.main_label.grid(column=0, row=0)

        self.bottom = PanedWindow(self.midSection_camPaneTabMain)
        self.bottom.configure(height=20, bg='#424242')
        self.midSection_camPaneTabMain.add(self.bottom, height=50)

        self.poseFontType = "Arial"
        self.poseFontSize = 14
        self.shipPoseLabel_camPaneTabMain = Label(self.bottom, text="Poses:", bg='#424242', fg='white',
                                                  font=(self.poseFontType, self.poseFontSize,"bold"))
        self.shipPoseLabel_camPaneTabMain.grid(column=0, row=0, sticky='w')

        self.dispPoseBunker_camPaneTabMain = Frame(self.bottom)  # , orient=HORIZONTAL)
        self.dispPoseBunker_camPaneTabMain.configure(bg='#424242')
        self.dispPoseBunker_camPaneTabMain.grid(column=0, row=1)

        # Text variables for visualization of movement
        self.x_value = DoubleVar()
        self.y_value = DoubleVar()
        self.z_value = DoubleVar()
        self.roll_value = DoubleVar()
        self.pitch_value = DoubleVar()
        self.yaw_value = DoubleVar()
        self.boardPose_quality = DoubleVar()

        self.DISPPLAYLABEL_WIDTH = 7
        self.DISPPOSE_TEXTCOLOR = "White"
        # Display of variables that represents the movement of the object - XYZ - PITCH YAW ROLL.
        self.x_label = Label(self.dispPoseBunker_camPaneTabMain, text='X-VALUE:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize),padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.x_label.grid(column=0, row=0, sticky='w')
        self.dispX_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.x_value, bg='#424242', fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize), padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.dispX_camPaneTabMain.grid(column=1, row=0)
        self.y_label = Label(self.dispPoseBunker_camPaneTabMain, text='Y-VALUE:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize), padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.y_label.grid(column=2, row=0)
        self.dispY_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.y_value,bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize), padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.dispY_camPaneTabMain.grid(column=3, row=0)
        self.z_label = Label(self.dispPoseBunker_camPaneTabMain, text='Z-VALUE:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize),padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.z_label.grid(column=4, row=0)
        self.dispZ_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.z_value,bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize), padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.dispZ_camPaneTabMain.grid(column=5, row=0)
        self.roll_label = Label(self.dispPoseBunker_camPaneTabMain, text='ROLL:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize),padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.roll_label.grid(column=0, row=1, sticky='w')
        self.dispRoll_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=  self.roll_value,bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                             font=(self.poseFontType, self.poseFontSize), padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.dispRoll_camPaneTabMain.grid(column=1, row=1)
        self.pitch_label = Label(self.dispPoseBunker_camPaneTabMain, text='PITCH:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize),padx=15,pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.pitch_label.grid(column=2, row=1)
        self.dispPitch_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.pitch_value,fg=self.DISPPOSE_TEXTCOLOR,
                                              bg='#424242',font=(self.poseFontType,self.poseFontSize), padx=15,pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispPitch_camPaneTabMain.grid(column=3, row=1)
        self.yaw_label = Label(self.dispPoseBunker_camPaneTabMain, text='YAW:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                          font=(self.poseFontType, self.poseFontSize), padx=15,pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.yaw_label.grid(column=4, row=1)
        self.dispYaw_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.yaw_value,bg='#424242', fg=self.DISPPOSE_TEXTCOLOR,
                                            font=(self.poseFontType, self.poseFontSize), padx=15, pady=10,width=self.DISPPLAYLABEL_WIDTH)
        self.dispYaw_camPaneTabMain.grid(column=5, row=1)
        # Display the quality of board estimation
        self.boardPoseQuality_label = Label(self.dispPoseBunker_camPaneTabMain, textvariable=self.boardPose_quality,fg=self.DISPPOSE_TEXTCOLOR,
                                            bg='#424242',font=(self.poseFontType, self.poseFontSize), padx=15,pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.boardPoseQuality_label.grid(column=7, row=0)
        self.dispBoardPoseQual_camPaneTabMain = Label(self.dispPoseBunker_camPaneTabMain, text='Q Board:', bg='#424242',fg=self.DISPPOSE_TEXTCOLOR,
                                            font=(self.poseFontType, self.poseFontSize), padx=15,pady=10, width=self.DISPPLAYLABEL_WIDTH)
        self.dispBoardPoseQual_camPaneTabMain.grid(column=6, row=0)

        self.second_label = Label(self.page_2, text='Camera Calibration', bg='#424242', fg='white')
        self.second_label.place(relx=0.5, rely=0.02, anchor='center')

        # Page 3: PDF setup
        # FIXME:Numbers in field disappears when clicking mouse.
        self.page_3_frame = Frame(self.page_3, bg="#424242")
        # must keep a global reference to these two
        self.im = Image.open('arucoBoard.png')
        self.im = self.im.resize((300, 300), Image.ANTIALIAS)
        self.ph = ImageTk.PhotoImage(self.im)
        # Need to use ph for tkinter to understand
        self.btn_img = Label(self.page_3_frame, image=self.ph)
        self.btn_img.pack(side=RIGHT)
        self.page_3_frame.pack()
        # Create container for holding board list
        self.boardlist_container = Frame(self.page_3)
        self.boardlist_container.config(padx='10',pady='10',bg='#424242')
        self.boardlist_container.pack(side=BOTTOM)
        self.boardimgs = []
        self.boardimgages = [None,None,None,None,None,None,None,None,None]
        self.page_3_label_frame = Frame(self.page_3_frame)
        self.page_3_label_frame.configure(relief='groove')
        self.page_3_label_frame.configure(borderwidth='2')

        self.page_3_entry_frame = Frame(self.page_3_frame)
        self.page_3_entry_frame.configure(relief='groove', borderwidth='2')



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
        self.length_entry.insert(0, 'Length')  # Add generic text
        self.length_entry.bind('<Button-1>', self.on_entry_click)  # If clicked on
        self.length_entry.configure(foreground='gray')
        self.length_entry.pack()
        self.length_entry.config(validate='key', validatecommand=vcmd_length)

        self.width.pack()
        self.width_entry.insert(0, 'Width')
        self.width_entry.bind('<Button-1>', self.on_entry_click)
        self.width_entry.configure(foreground='gray')
        self.width_entry.pack()
        self.width_entry.config(validate='key', validatecommand=vcmd_width)

        self.size.pack()
        self.size_entry.insert(0, 'Size')
        self.size_entry.configure(foreground='gray')
        self.size_entry.bind('<Button-1>', self.on_entry_click)
        self.size_entry.pack()
        self.size_entry.config(validate='key', validatecommand=vcmd_size)

        self.gap.pack()
        self.gap_entry.insert(0, 'Gap')
        self.gap_entry.bind('<Button-1>', self.on_entry_click)
        self.gap_entry.configure(foreground='gray')
        self.gap_entry.pack()
        self.gap_entry.config(validate='key', validatecommand=vcmd_gap)

        self.btn_frame = Frame(self.page_3)
        self.btn_frame.configure(bg='black')
        self.btn_frame.pack()
        self.pdf_btn = Button(self.btn_frame, text='Generate board',
                              command=lambda: [self.createArucoBoard()])
        self.pdf_btn.configure(bg='#424242', fg='white')
        self.pdf_btn.pack(side=LEFT)
        self.pdf_btn = Button(self.btn_frame, text='Add to tracking list',
                              command=lambda: [self.exportArucoBoard()])
        self.pdf_btn.configure(bg='#424242', fg='white')
        self.pdf_btn.pack(side=LEFT)
        self.pdf_btn = Button(self.btn_frame, text='Save Aruco Board',
                              command=lambda: [self.saveArucoPDF()])
        self.pdf_btn.configure(bg='#424242', fg='white')
        self.pdf_btn.pack(side=LEFT)

        # Page 4: Graph setup
        self.page_4_frame = Frame(self.page_4)
        self.page_4_frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.page_4_frame.configure(relief='groove', borderwidth='2', background='#424242', width=565)

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

        self.btn_plot = tk.Button(self.btn_frame_4)
        self.btn_plot.pack(side=LEFT)
        self.btn_plot.configure(background='#665959')
        self.btn_plot.configure(disabledforeground='#911515')
        self.btn_plot.configure(foreground='#FFFFFF')
        self.btn_plot.configure(text='Start')
        self.btn_plot.configure(command=lambda: (self.hideButton(self.btn_plot),self.setupGraph(self.graph_frame)))

        self.btn_save =  tk.Button(self.btn_frame_4)
        self.btn_save.pack(side=RIGHT)
        self.btn_save.configure(background='#665959')
        self.btn_save.configure(disabledforeground='#911515')
        self.btn_save.configure(foreground='#FFFFFF')
        self.btn_save.configure(text='Stop')
        self.btn_save.configure(command=lambda: self.showButton(self.btn_plot))



        self.camFrameSettingSection = Frame(self.left_camPaneTabMain, bg='#424242', height=500)  # , orient=HORIZONTAL)
        #self.camFrameSettingSection.configure(bg='#424242')

        # Start and stop button setup
        self.start_btn = Button(self.camFrameSettingSection, text='Start', bg='green', fg='white',height=2,width=8,
                                command=lambda: [self.sendStartSignal()])
        # init_cams_btn = Button(page_1, text='Initialise cameras', command=startClicked)
        self.stop_btn = Button(self.camFrameSettingSection, text='Stop', bg='red', fg='white',height=2,width=8,
                               command=lambda: [self.sendStopSignal()])
        self.hidecam_btn = Button(self.camFrameSettingSection, text='Hide', command=self.hideCamBtnClicked,height=2,width=8,
                                  bg='#424242', fg='white',)
        # Label to respond if button pushed before VEs have been inited
        self.poseEstimationStartDenied_label = Label(self.camFrameSettingSection,
                                                     text="Please init VEs in config tab first.", bg="#424242")
        self.camFrameSettingSection.pack()
        self.calibrate_btn = Button(self.page_2, bg='#424242', fg='white', text='Calibrate', command=None)

        self.start_btn.grid(column=0, row=0)
        self.stop_btn.grid(column=1, row=0)
        self.hidecam_btn.grid(column=2, row=0)
        self.availCamsLabel = Label(self.left_camPaneTabMain, text='Available cameras: ',font=("Arial", "12"))
        self.availCamsLabel.configure(bg='#424242',fg='white')
        self.availCamsLabel.pack()

        self.calibrate_btn.grid(column=1, row=1)
        self.calibrate_btn.grid_rowconfigure(1, weight=1)
        self.calibrate_btn.grid_columnconfigure(1, weight=1)
        self.__displayedCameraIndex = tk.IntVar()  # Radio buttons controlling which camera feed to show. negatives means auto.
        self.__displayedCameraIndex.set(-1)

        # Camera selection variable
        tk.Radiobutton(self.left_camPaneTabMain, text="Auto", padx=5, variable=self.__displayedCameraIndex,
                       command=self.setCameraIndex, value=-1, bg='#424242', fg='orange',font=("Arial", "12","bold")).pack()

        self.board_label = Label(self.bottom_left, text='Boards', padx=20,bg='#424242', fg='White',font=("Arial", "12")).pack()

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
        self.setupConfigTab()

        # Set focus to start button
        self.start_btn.focus()

        # Adds board radio button to the GUI
        self.addBoardButton()

        # Start it all
        self.root.mainloop()

        # Configuration setup

    def setupConfigTab(self):
        '''
        # Create paned windows for GUI
        :return:
        '''

        self.configPaneTabMain = PanedWindow(self.page_5, bg='black')
        self.configPaneTabMain.pack(fill=BOTH, expand=True)
        self.configPaneTabMain.configure(bg='#424242')


        # Mid section Pane for configuring
        self.midSection_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL, bg='gray80')
        self.configPaneTabMain.add(self.midSection_configPaneTabMain)
        self.midSection_configPaneTabMain.configure(bg='#424242')
        self.rightSection_configPaneTabMain = PanedWindow(self.configPaneTabMain, orient=VERTICAL)
        self.configPaneTabMain.add(self.rightSection_configPaneTabMain)
        self.configPaneTabMain.configure(bg='#424242')

        self.midtopSectionLabel_configPaneTabMain = Frame(self.midSection_configPaneTabMain,height=100)
        self.midSection_configPaneTabMain.add(self.midtopSectionLabel_configPaneTabMain)
        self.midtopSectionLabel_configPaneTabMain.configure(bg='#424242')

        self.rightSectionLabel_configPaneTabMain = Label(self.rightSection_configPaneTabMain, text="right pane")
        self.rightSection_configPaneTabMain.add(self.rightSectionLabel_configPaneTabMain)
        self.rightSection_configPaneTabMain.configure(bg='#424242')
        self.rightSectionLabel_configPaneTabMain.configure(bg='#424242')

        # Configurations for which cams to connect
        self.selectCamIndexesFrame = Frame(self.midSection_configPaneTabMain)
        self.selectCamIndexesFrame.configure(bg='#424242')
        self.midSection_configPaneTabMain.add(self.selectCamIndexesFrame)
        Label(self.selectCamIndexesFrame, text="Hello").grid(row=0,column=0)
        self.selectCamIndexesFrame.configure(relief='groove')
        self.selectCamIndexesFrame.configure(borderwidth='2', pady='10')

        self.midSection_configPaneTabMain.configure(relief='groove')
        self.midSection_configPaneTabMain.configure(borderwidth='2')
        self.rightSection_configPaneTabMain.configure(relief='groove')
        self.rightSection_configPaneTabMain.configure(borderwidth='2')

        ''' Create VEConfigUnits that controls all  '''
        numbCamsToShow = 5
        for i in range(0,numbCamsToShow+1): # Create VEConfigUnits
            # Create VECU fpr given index
            VECU = VEConfigUnit(i,self, self.selectCamIndexesFrame, self.setPreviewStatus)
            VECU.start()
            self.VEConfigUnits.append(VECU)


        self.sendCamSelectionButton_configTab = Button(self.midSection_configPaneTabMain, padx = 10, pady = 10,
                                                       text="Apply",bg='#424242',command=self.applyCamList, width=20,fg="white")
        #deadspace5 = Frame(self.midSection_configPaneTabMain).pack()
        #deadspace6 = Frame(self.midSection_configPaneTabMain).pack()
        self.midSection_configPaneTabMain.add(self.sendCamSelectionButton_configTab)
        deadspace2 = Frame(self.midSection_configPaneTabMain,height=100, bg='#424242')
        self.midSection_configPaneTabMain.add(deadspace2)
        # List for VEs stored in GUI
        self.prelimVEList = []

        #Container for preview image
        self.imgHolder = Label(self.rightSectionLabel_configPaneTabMain)
        self.imgHolder.image = None
        self.imgHolder.pack()


    def applyCamList(self):
        '''
        Collect all VEs to be sent to PE for PoseEstimation, and send it to connector-.
        :return:
        '''
        self.VEsToSend = [] # List of VEs to send to PoseEstimator
        logging.debug("In applyCamList()")
        #print("VEConfigUnits:", len(self.VEConfigUnits), self.VEConfigUnits)
        for VECU in self.VEConfigUnits:
            #print("Inside")
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
            self.poseEstimationStartAllowed = True
            self.poseEstimationStartDenied_label.grid_forget() # Remove eventual error warning
            self.connector.collectGUIVEs(self.VEsToSend) # Send them to GUI
            self.updateCamlist(self.VEsToSend)
        #self.__collectGUIVEs.append(True) # Set flag: PE now picks up.

    def setCameraIndex(self):
        cameraIndex = self.__displayedCameraIndex.get()
        self.connector.setCameraIndex(cameraIndex)

    def getVEsForPE(self):
        '''
        Send the VEs defined and applied in the Config tab in GUI.
        :return: List of VEs
        '''
        return self.VEsToSend

    def resetCamExtrinsic(self):
        '''
        Reset the cam extrinsic matrixes to the current frame point.
        # TODO: Use stack to indicate job done? Add button to GUI.
        :return:
        '''
        self.connector.setResetExtrinsic(True)
        #self.resetBoardPosition.append(True)

    def stopRawCameraClicked(self):
        '''
        Stops video stream. Possible to add more functionality later on for saving data etc.
        :return: None at the moment, but may return datastream later on.
        '''
        self.saveFrame()
        self.show_video = False

    def hideCamBtnClicked(self):
        self.frame = None

    def showFindPoseStream(self):
        pass
        try:
            print("In GUI, line 562. Frame: \n " + str(self.frame) + "\n")
            image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.main_label.configure(image=image)
            self.main_label.image = image
        except AttributeError as e:
            logging.error(str(e))
        except cv2.error as e:
            logging.error(str(e))

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
        cv2.imwrite('images/frame%d.jpg' % self.counter, self.frame)

    def changeCameraID(self, camid):
        print("CHANGING CAMERA ID: Camid to shift to", camid)
        print("Previous camid: ", self.camIDInUse)
        self.camIDInUse = camid

    def doAbortApp(self):
        '''
        Stop the poseestimation running, but (for now), don't stop the application. .
        :return:
        '''
        return self.doStopApp

    def setFindPoseFalse(self):
        '''
        Set flag who stops the poseestimation running to True.
        '''
        logging.info("Setting doStopApp to True")
        self.doStopApp = True
        self.poseEstimationIsRunning = False

    def dispContinuousResults(self):
        '''
        Passed to, and called from Connector, while application runs.
        Delivers pose and the "poseframe".
        '''
        self.showFindPoseStream()

    def fileClicked(self):
        '''
        Dummy function for setup for buttons or other functions that needs callback functions
        :return: print
        '''
        print('File clicked')

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
            self.userBoard = arucoBoard(board_height=length_value, width_value=width_value, marker_size=size_value,
                                        marker_gap=gap_value)
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
            self.__pushedBoards.append(self.userBoard)
            self.addBoardWidgetToGUI(self.userBoard)
            self.addBoardButton()
    def addBoardWidgetToGUI(self, board):
        try:
            ABU = ArucoBoardUnit(board, self.boardlist_container)
            self.arucoBoardUnits.append(ABU)
        except cv2.error as e:
            logging.error("Can't create that many boards, need to expand dictionary!")
            logging.error(str(e))
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

    def updateGUIFields(self, poses, frame, boardPose_quality):
        """
        Update GUI-objects fields outputframe and six axis pose.
        # Pose should probably be a datatype/class?
        :param poses: The poses of all models tracked.
        :param frame: The frame to display in camera view.
        :return: None
        """
        self.modelPoses = poses
        self.frame = frame
        boardIndex = self.boardIndex.get()
        if boardPose_quality is not None:
            self.boardPose_quality.set(round(boardPose_quality, 2))
        else:
            self.boardPose_quality.set(0.0)

        if poses:
            evec, tvec = poses[boardIndex]
            if evec is not None:
                x, y, z = tvec
                self.x_value.set(x)
                self.y_value.set(y)
                self.z_value.set(z)
            else:
                self.x_value.set(0.0)
                self.y_value.set(0.0)
                self.z_value.set(0.0)
            if tvec is not None:
                roll, pitch, yaw = evec
                self.roll_value.set(roll)
                self.pitch_value.set(pitch)
                self.yaw_value.set(yaw)
            else:
                self.roll_value.set(0.0)
                self.pitch_value.set(0.0)
                self.yaw_value.set(0.0)

    def readUserInputs(self):
        # TODO: Remove, and use direct contact with connector.
        """
        Exports all user commands relevant outside of the GUI
        :return: camID: index of selected camera. negative if auto. newBoard: arucoboard created and pushed from GUI
        resetExtrinsic: Command to reset extrinsic matrices of cameras.
        startCommand: Command to start PoseEstimator
        stopCommand: Command to stop PoseEstimator
        doPreview: Return whether to previuew a frame from a camera in the VECU GUI section.
        """
        cameraIndex = None
        boardIndex = None
        try:
            cameraIndex = self.__displayedCameraIndex.get()
            boardIndex = self.boardIndex.get()
        except AttributeError as e:
            # Don't crash if __displayedCameraIndex not initialised, but set a safe value instead.
            cameraIndex = 5
            boardIndex = 0
        if cameraIndex < 0:
            auto = True
            self.connector.setAuto(True)
        else:
            self.connector.setAuto(False)
        newBoard = stackChecker(self.__pushedBoards)
        resetExtrinsic = stackChecker(self.__resetBoardPosition)
        startCommand = stackChecker(self.__start_application)
        stopCommand = stackChecker(self.__stop_application)
        collectGUIVEs = stackChecker(self.__collectGUIVEs)
        self.__doPreviewIndex = self.checkPreviewStatus() # -1 if none preview was requested
#        msg = "__doPreviewIndex: ", self.__doPreviewIndex
#        logging.debug(msg)
        if self.__doPreviewIndex is not -1 and self.__doPreviewIndex is not None:
            #Activate thread for showing prev image TODO: Use threading
            print("Inside")
            self.showPreviewImage(self.__doPreviewIndex)
        elif self.imgHolder.image is not None:
            self.imgHolder.configure(image='')
            self.imgHolder.image = None
        #return cameraIndex, boardIndex, auto, newBoard, resetExtrinsic, startCommand, stopCommand, collectGUIVEs#, VEsToRun

    def sendStartSignal(self):
        """
        Adds a start signal to the stop signal stack. The signal is consumed when read.
        :return: None
        """
        if self.poseEstimationStartAllowed: # VEs are initialised
            logging.info("Pose Estimation is starting.")
            self.connector.setStartCommand(True)
            self.connector.start()
            #self.__start_application.append(True)
            logging.debug("Start signal sent.")
            self.poseEstimationStartDenied_label.grid_forget()
        else:
            showinfo("Error", "Please choose some cameras in the Config-section first.")
            #self.poseEstimationStartDenied_label.grid(row=1, column=0, columnspan=3)

    def sendStopSignal(self):
        """
        Adds a start signal to the stop signal stack. The signal is consumed when read.
        :return: None
        """
        self.connector.setStopCommand(True)
        self.__stop_application.append(True)
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
        print("Index to preview:", index)
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

    def addBoardButton(self):
        """
        Adds a radio button to the board list in the side panel.
        :return: None
        """
        i = len(self.boardButtonList)
        buttonText = "Board " + str(i)
        button = tk.Radiobutton(self.bottom_left, text=buttonText, padx=5, bg='#424242', fg='Orange',font=("Arial", "12","bold"),
                                command=self.setBoardIndexToDisplay, variable=self.boardIndex, value=i)
        self.boardButtonList.append(button)
        self.boardButtonList[-1].pack()

    def setBoardIndexToDisplay(self):
        #TODO: Can be called directly from radiobutton.
        boardIndex = self.boardIndex.get()
        self.connector.setBoardIndexToDisplay(boardIndex)

    def addCameraButton(self):
        #TODO: Not used. Remove?
        """
        Adds a radio button to the camera list in the side panel.
        :return: None
        """
        i = len(self.boardButtonList)
        if i not in self.cameraButtonIndexList:
            buttonText = "Camera " + str(i)
            button = tk.Radiobutton(self.left_camPaneTabMain, text=buttonText, padx=5, variable=self.__displayedCameraIndex,
                                    value=i, bg='#424242', fg='orange')
            self.cameraButtonList.append(button)
            self.cameraButtonIndexList.append(i)
            self.cameraButtonList[-1].pack()

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
                                        variable=self.__displayedCameraIndex,
                                        value=camID, bg='#424242', fg='orange')
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

    def setupGraph(self, frame):
        '''
        Send position for the board to the graph frame and plot pos
        :param frame: The frame you want to plot the graph in.
        :return:
        '''
        t_data, x_data, y_data, z_data = [], [], [], []

        figure = plt.figure()
        ax = figure.subplots(3, 1, sharex=True, sharey=True)
        line, = ax[0].plot(t_data, x_data, 'r')
        line2, = ax[1].plot(t_data, y_data, 'c')
        line3, = ax[2].plot(t_data, z_data, '-')
        start_time = time.time()

        def update(self, frame):
            elapsed_time = time.time() - start_time
            t_data.append(elapsed_time)
            x_data.append(self.x_value)
            y_data.append(self.y_value)
            z_data.append(self.z_value)
            line.set_data(t_data, x_data)
            line2.set_data(t_data, y_data)
            line3.set_data(t_data, z_data)
            figure.gca().relim()
            figure.gca().autoscale_view()

        figure.suptitle('Movement')
        ax[0].set_ylabel('X')
        ax[1].set_ylabel('Y')
        ax[2].set_ylabel('Z')
        ax[2].set_xlabel('Time (s)')
        animation = FuncAnimation(figure, update, interval=100)

    def hideButton(self, button):
        '''
        Hide the chosen button if you do not want it to be pressed until some other
        button is pressed first.
        :param button: The button you want to hide
        :return: None
        '''
        button.lower()

    def showButton(self, button):
        '''
        Show a hidden button
        :param button: Button you want to show
        :return:
        '''
        button.lift()

