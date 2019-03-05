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
camIDInUse = 1
class GUIApplication(threading.Thread):

    def __init__(self, connector):
        threading.Thread.__init__(self)
        # Camera variables
        self.counter = 0
        self.show_video = False
        self.c = connector
        self.camlist = self.c.initConnectedCams()

    def run(self):
        # Global camera_index
        global video_streams
        self.camIDInUse = 0
        # Empty function to add to dummy buttons
        def fileClicked():
            print('File clicked')


        # Set up main window.
        self.root = Tk()
        self.root.title('Boat Pose Estimator')
        self.root.geometry('800x600')
        self.root.configure(background='black')

        # Create menu
        menu = Menu(self.root)
        file_menu = Menu(menu, tearoff=0)

        # Create notebook
        notebook = ttk.Notebook(self.root)

        # Defines and places the notebook widget
        notebook.pack(fill=BOTH, expand=True)#grid(row=0, column=0, columnspan=1, rowspan=1, sticky='NESW')

        # gives weight to the cells in the grid
        rows = 0
        while rows < 1:
            self.root.rowconfigure(rows, weight=1)
            self.root.columnconfigure(rows, weight=1)
            rows += 1

        #tabs = {} #Implement this in the future for self generating tabs
        #for tab_name in tab_names:
        #    tab = MyTab(self.notebook, tab_name)
        #    self.notebook.add(tab, text=tab_name)
        #    tabs[tab_name] = tab


        # Adds tabs of the notebook
        page_1 = ttk.Frame(notebook)
        page_2 = ttk.Frame(notebook)
        page_3 = ttk.Frame(notebook)
        page_4 = ttk.Frame(notebook)

        notebook.add(page_1, text='Camera')
        notebook.add(page_2, text='Calibration')
        notebook.add(page_3, text='PDF')
        notebook.add(page_4, text='Graph')



        #  File menu setup
        file_menu.add_command(label='New', command=None)
        file_menu.add_command(label='Save', command=None)
        file_menu.add_command(label='Open', command=None)
        file_menu.add_command(label='Settings', command=None)
        file_menu.add_command(label='Export', command=None)
        file_menu.add_command(label='Exit', command=self.root.quit)
        menu.add_cascade(label='File', menu=file_menu)

        # Edit menu setup
        edit_menu = Menu(menu, tearoff=0)
        edit_menu.add_command(label='Cut', command=None)
        edit_menu.add_command(label='Copy', command=None)
        edit_menu.add_command(label='Paste', command=None)
        menu.add_cascade(label='Edit', menu=edit_menu)

        # Configure setup
        self.root.config(menu=menu)

        # Create the main pane tab for first tab of gui
        camPaneTabMain = PanedWindow(page_1, bg='gray40')
        camPaneTabMain.pack(fill=BOTH, expand=True)#camPaneTabMain.pack(page_1)#(row=0, column=0,columnspan=1,rowspan=1,sticky='NESW')

        left_camPaneTabMain = Label(camPaneTabMain)#, text="left pane")
        camPaneTabMain.add(left_camPaneTabMain)

        midSection_camPaneTabMain = PanedWindow(camPaneTabMain, orient=VERTICAL, bg='gray80')
        camPaneTabMain.add(midSection_camPaneTabMain)

        top = Label(midSection_camPaneTabMain, text="top pane")
        midSection_camPaneTabMain.add(top)

        bottom = Label(midSection_camPaneTabMain, text="bottom pane")
        midSection_camPaneTabMain.add(bottom)

        main_label = Label(midSection_camPaneTabMain, text='Camera Views')
        main_label.grid(column=2, row=0)


        second_label = Label(page_2, text='Camera Calibration')
        second_label.place(relx=0.5, rely=0.02, anchor='center')

        page_4_frame = Frame(page_4)
        page_4_frame.place(relx=0, rely=0, relheight=1, relwidth=1)
        page_4_frame.configure(relief='groove')
        page_4_frame.configure(borderwidth='2')
        page_4_frame.configure(relief='groove')
        page_4_frame.configure(background='#000000')
        page_4_frame.configure(width=565)

        GUIDataPlotting.createDataWindow(page_4_frame)



        def startClicked():

            '''
            Start Video Stream
            :return: None
            '''
            global show_video
            show_video = True
            main_label.configure(text='Starting video stream')
            videoStream()
        #    if not show_video:
         #       start_btn.grid(column=0, row=2)
          #      stop_btn.grid(column=None, row=None)
           # elif show_video:
            #    stop_btn.grid(column=1, row=2)
             #   start_btn.grid(column=None, row=None)


        def stopClicked():
            '''
            Stops video stream. Possible to add more functionality later on for saving data etc.
            :return: None at the moment, but may return datastream later on.
            '''
            global show_video
            saveFrame()
            show_video = False

            main_label.configure(text='Stopping video stream')
         #   if not show_video:
          #      start_btn.grid(column=0, row=2)
           #     stop_btn.grid(column=None, row=None)
            #elif show_video:
             #   stop_btn.grid(column=1, row=2)
              #  start_btn.grid(column=None, row=None)

        def hideCamBtnClicked():
            global showVideo
            showVideo = False
        # function for video streaming
        def videoStream():
            '''
            Create a simple setup for testing video stream with GUI
            :return: None
            '''

            global show_video


            if show_video is True:
                try:
                    global camIDInUse
                    #counter += 1
                    #currCap = video_streams[int(var.get())]
                    print("Var value: ", var.get())
                    frame = self.c.getImgFromSingleCam(v.get()) #currCap.read()
                    # Check if the webcam is opened correctly
                    #if not currCap.isOpened():
                    #    raise IOError("Cannot open webcam")
                    print("ID: ", self.camIDInUse)
                    print("Frame: ", frame)
                    if frame is not None:
                        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img_video = Image.fromarray(cv2image)
                        image_tk = ImageTk.PhotoImage(image=img_video)
                        main_label.image_tk = image_tk
                        main_label.configure(image=image_tk)
                        main_label.after(1, videoStream)
                except AttributeError as e:
                    logging.error(str(e))

        def showImage():
            '''
            test to save single frame
            :return: img
            '''
            global show_video
            img = ImageTk.PhotoImage(file='images/test_image.png')
            img_label = Label(self.root, image=img)
            img_label.grid(column=0, row=0)


        # function for saving a single frame
        def saveFrame():
            '''
            Save a single frame from video feed
            :return: jpg
            '''
            cv2.imwrite('images/frame%d.jpg' % self.counter, videoStream())


        def changeCameraID(camid):
            global camIDInUse
            print("CHANGING CAMERA ID: Camid to shift to", camid)
            print("Previous camid: ", camIDInUse)
            camIDInUse = camid#cap = video_stream


        def placeGraph():
            GUIDataPlotting.plotGraph()

        def startApplication():
            #Start the main app
            self.c.startApplication(doAbortFx=doAbortApp,dispContiniusResults=dispContiniusResults)

        def doAbortApp(self):
            return False # For now

        def dispContiniusResults(self, result):
            print(result)
        camFrameSettingSection = Frame(left_camPaneTabMain,bg='gray80')#, orient=HORIZONTAL)

        # Start and stop button setup
        start_btn = Button(camFrameSettingSection, text='Start', command=startClicked)
        #init_cams_btn = Button(page_1, text='Initialise cameras', command=startClicked)
        stop_btn = Button(camFrameSettingSection, text='Stop', command=stopClicked)
        hidecam_btn = Button(left_camPaneTabMain, text='Hide', command=hideCamBtnClicked)
        camFrameSettingSection.pack()
        calibrate_btn = Button(page_2, text='Calibrate', command=None)

        start_btn.grid(column=0, row=0)
        stop_btn.grid(column=1,row=0)
        availCamsLabel = Label(left_camPaneTabMain,text='Available cameras: ')
        availCamsLabel.pack()
        deadSpace1 = Frame(left_camPaneTabMain, height=100).pack()
        startCamApp = Button(left_camPaneTabMain, text='Start application.',command=startApplication)



        calibrate_btn.grid(column=1, row=1)
        calibrate_btn.grid_rowconfigure(1, weight=1)
        calibrate_btn.grid_columnconfigure(1, weight=1)

        # Camera temp variables.
        #cam_list = ['Cam 1', 'Cam 2', 'Cam 3']
        var = IntVar()


        v = tk.IntVar()
        v.set(1)  # initializing the choice, i.e. Python

        for vali, cam in enumerate(self.camlist):
            tk.Radiobutton(left_camPaneTabMain,
                           text=str(vali),
                           padx=20,
                           variable=v,
                           value=vali).pack()#grid(column=1,row=0+vali)

        self.root.mainloop()
    def run2(self):
        n = ttk.Notebook(parent)
        f1 = ttk.Frame(n)  # first page, which would get widgets gridded into it
        f2 = ttk.Frame(n)  # second page
        n.add(f1, text='One')
        n.add(f2, text='Two')
        p = ttk.Panedwindow(parent, orient=VERTICAL)
        # first pane, which would get widgets gridded into it:
        f1 = ttk.Labelframe(p, text='Pane1', width=100, height=100)
        f2 = ttk.Labelframe(p, text='Pane2', width=100, height=100)  # second pane
        p.add(f1)
        p.add(f2)