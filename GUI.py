from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox
from PIL import ImageTk, Image
from Camera import *
import matplotlib as mpl
import GUIDataPlotting
import Connector
import threading

import threading

class GUIApplication(threading.Thread):

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

    def run(self):
        '''
        Run the main application.
        '''
        self.camIDInUse = 0

        # Set up main window.
        self.root = Tk()
        self.root.title('Boat Pose Estimator')
        self.root.geometry('800x600')
        self.root.configure(background='black')

        # Create menu
        self.menu = Menu(self.root)
        self.file_menu = Menu(self.menu, tearoff=0)

        # Create notebook
        self.notebook = ttk.Notebook(self.root)

        # Defines and places the notebook widget. Expand to cover complete window.
        self.notebook.pack(fill=BOTH, expand=True)

        # gives weight to the cells in the grid
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

        self.notebook.add(self.page_1, text='Camera')
        self.notebook.add(self.page_2, text='Calibration')
        self.notebook.add(self.page_3, text='PDF')
        self.notebook.add(self.page_4, text='Graph')



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

        # Create the main pane tab for first tab of gui
        self.camPaneTabMain = PanedWindow(self.page_1, bg='gray40')
        self.camPaneTabMain.pack(fill=BOTH, expand=True)#camPaneTabMain.pack(page_1)#(row=0, column=0,columnspan=1,rowspan=1,sticky='NESW')

        self.left_camPaneTabMain = Label(self.camPaneTabMain)#, text="left pane")
        self.camPaneTabMain.add(self.left_camPaneTabMain)

        self.midSection_camPaneTabMain = PanedWindow(self.camPaneTabMain, orient=VERTICAL, bg='gray80')
        self.camPaneTabMain.add(self.midSection_camPaneTabMain)

        self.top = Label(self.midSection_camPaneTabMain, text="top pane")
        self.midSection_camPaneTabMain.add(self.top)

        self.bottom = Label(self.midSection_camPaneTabMain, text="bottom pane")
        self.midSection_camPaneTabMain.add(self.bottom)

        self.main_label = Label(self.midSection_camPaneTabMain, text='Camera Views')
        self.main_label.grid(column=2, row=0)

        self.second_label = Label(self.page_2, text='Camera Calibration')
        self.second_label.place(relx=0.5, rely=0.02, anchor='center')

        self.page_4_frame = Frame(self.page_4)
        self.page_4_frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.page_4_frame.configure(relief='groove')
        self.page_4_frame.configure(borderwidth='2')
        self.page_4_frame.configure(relief='groove')
        self.page_4_frame.configure(background='#000000')
        self.page_4_frame.configure(width=565)

        try:
            GUIDataPlotting.createDataWindow(self.page_4_frame)
        except IndexError:
            pass
            logging.info('Sketchy, but OK.')

        self.camFrameSettingSection = Frame(self.left_camPaneTabMain,bg='gray80')#, orient=HORIZONTAL)

        # Start and stop button setup
        self.start_btn = Button(self.camFrameSettingSection, text='Start', command=self.startClicked)
        #init_cams_btn = Button(page_1, text='Initialise cameras', command=startClicked)
        self.stop_btn = Button(self.camFrameSettingSection, text='Stop', command=self.stopClicked)
        self.hidecam_btn = Button(self.left_camPaneTabMain, text='Hide', command=self.hideCamBtnClicked)
        self.camFrameSettingSection.pack()
        self.calibrate_btn = Button(self.page_2, text='Calibrate', command=None)

        self.start_btn.grid(column=0, row=0)
        self.stop_btn.grid(column=1,row=0)
        self.availCamsLabel = Label(self.left_camPaneTabMain,text='Available cameras: ')
        self.availCamsLabel.pack()


        self.calibrate_btn.grid(column=1, row=1)
        self.calibrate_btn.grid_rowconfigure(1, weight=1)
        self.calibrate_btn.grid_columnconfigure(1, weight=1)

        # Camera temp variables.
        #cam_list = ['Cam 1', 'Cam 2', 'Cam 3']
        self.var = IntVar()


        self.v = tk.IntVar()
        self.v.set(1)  # initializing the choice, i.e. Python

        for vali, cam in enumerate(self.camlist):
            tk.Radiobutton(self.left_camPaneTabMain,
                           text=str(vali),
                           padx=20,
                           variable=self.v,
                           value=vali).pack()#grid(column=1,row=0+vali)
        deadSpace1 = Frame(self.left_camPaneTabMain, height=100).pack()
        self.startCamApp = Button(self.left_camPaneTabMain, text='Start application', command=self.startApplication)
        self.stopCamApp = Button(self.left_camPaneTabMain, text='Stop application', command=self.setDoStopApp)
        self.startCamApp.pack()
        self.stopCamApp.pack()
        self.root.mainloop()

    def startClicked(self):

        '''
        Start Video Stream
        :return: None
        '''

        self.show_video = True
        self.main_label.configure(text='Starting video stream')
        self.videoStream()
    #    if not show_video:
     #       start_btn.grid(column=0, row=2)
      #      stop_btn.grid(column=None, row=None)
       # elif show_video:
        #    stop_btn.grid(column=1, row=2)
         #   start_btn.grid(column=None, row=None)


    def stopClicked(self):
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
        #elif show_video:
         #   stop_btn.grid(column=1, row=2)
          #  start_btn.grid(column=None, row=None)

    def hideCamBtnClicked(self):
        # Hide the cam.

        # Don't access new frames. 
        self.show_video = False


    def videoStream(self):
        '''
        Create a simple setup for testing video stream with GUI
        :return: None
        '''
        print('Show video: (show_video) ',self.show_video)
        if self.show_video is True:
            try:
                #counter += 1
                #currCap = video_streams[int(var.get())]
                print("Var value: ", self.var.get())
                self.frame = self.c.getImgFromSingleCam(self.v.get()) #currCap.read()
                # Check if the webcam is opened correctly
                #if not currCap.isOpened():
                #    raise IOError("Cannot open webcam")
                print("ID: ", self.camIDInUse)
                if self.frame is not None:
                    self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    self.img_video = Image.fromarray(self.cv2image)
                    self.image_tk = ImageTk.PhotoImage(image=self.img_video)
                    self.main_label.image_tk = self.image_tk
                    self.main_label.configure(image=image_tk)
                    self.main_label.after(1, self.videoStream)
                else:
                    logging.info("Frame is None.")
            except AttributeError as e:
                logging.error(str(e))



    def poseStream(self, frame):
        logging.debug('Inside posestream')
        try:
            print("FRRRRAAAAAMMMMMEEE: ", frame)
            print('Image_tk: ', self.image_tk)
            if frame is not None:
                self.cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.img_video = Image.fromarray(self.cv2image)
                self.image_tk = ImageTk.PhotoImage(image=self.img_video)
                self.main_label.image_tk = self.image_tk
                self.main_label.configure(image=self.image_tk)
                #main_label.after(1, videoStream)
        except AttributeError as e:
            logging.error(str(e))

    def showImage(self):
        '''
        test to save single frame
        :return: img
        '''
        self.img = ImageTk.PhotoImage(file='images/test_image.png')
        self.img_label = Label(self.root, image=img)
        self.img_label.grid(column=0, row=0)


    # function for saving a single frame
    def saveFrame(self):
        '''
        Save a single frame from video feed
        :return: jpg
        '''
        cv2.imwrite('images/frame%d.jpg' % self.counter, self.videoStream())


    def changeCameraID(self, camid):
        print("CHANGING CAMERA ID: Camid to shift to", camid)
        print("Previous camid: ", self.camIDInUse)
        self.camIDInUse = camid


    def placeGraph(self):
        GUIDataPlotting.plotGraph()


    def startApplication(self):
        '''
        Start the poseestimator in application.

        :return:
        '''
        #Start the main app
        self.poseEstmationThread = threading.Thread(target=self.c.startApplication, args=[self.dispContiniusResults, self.doAbortApp], daemon=True)
        self.poseEstmationThread.start()
        logging.info('Started application in a own thread.')

    def doAbortApp(self):
        '''
        Stop the poseestimation running, but (for now), don't stop the application. .
        :return:
        '''
        return self.doStopApp # For now

    def setDoStopApp(self):
        '''
        Set flag who stops the poseestimation running to True.
        :return:
        '''
        logging.info("Setting doStopApp to True")
        self.doStopApp = True

    def dispContiniusResults(self, result, poseFrame):
        '''
        Passed to, and called from Connector, while application runs.
        Delivers pose and the "poseframe".
        :param result: A tuple with rvec and tvec.
        :param poseFrame: Image of webcam + detection markers and coordinate system.
        '''
        self.poseStream(poseFrame)

    def fileClicked():
        print('File clicked')
