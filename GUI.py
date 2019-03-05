from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import Menu
from tkinter import messagebox
from PIL import ImageTk, Image
from Camera import *
from CameraGroup import *
import matplotlib as mpl
import GUIDataPlotting
import Connector
import threading

import threading

class GUIApplication(threading.Thread):
    def __init__(self, connector):
        threading.Thread.__init__(self)
        # Camera variables
        self.counter = 0
        self.show_video = False
        self.c = connector

    def run(self):
        # Global camera_index
        global video_streams

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
        notebook.grid(row=0, column=0, columnspan=8, rowspan=6, sticky='NESW')

        # gives weight to the cells in the grid
        rows = 0
        while rows < 6:
            self.root.rowconfigure(rows, weight=1)
            self.root.columnconfigure(rows, weight=1)
            rows += 1

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

        main_label = Label(page_1, text='Camera Views')
        main_label.grid(column=2, row=0)

        second_label = Label(page_2, text='Camera Calibration')
        second_label.place(relx=0.5, rely=0.02, anchor='center')

        style = ttk.Style()
        style.theme_use('default')
        style.configure("black.Horizontal.TProgressbar", background='black')


        def startClicked():

            '''
            Start Video Stream
            :return: None
            '''
            global show_video
            show_video = True
            main_label.configure(text='Starting video stream')
            videoStream()
            if not show_video:
                start_btn.grid(column=0, row=2)
                stop_btn.grid(column=None, row=None)
            elif show_video:
                stop_btn.grid(column=1, row=2)
                start_btn.grid(column=None, row=None)


        def stopClicked():
            '''
            Stops video stream. Possible to add more functionality later on for saving data etc.
            :return: None at the moment, but may return datastream later on.
            '''
            global show_video
            saveFrame()
            show_video = False

            main_label.configure(text='Stopping video stream')
            if not show_video:
                start_btn.grid(column=0, row=2)
                stop_btn.grid(column=None, row=None)
            elif show_video:
                stop_btn.grid(column=1, row=2)
                start_btn.grid(column=None, row=None)


        # function for video streaming
        def videoStream():
            '''
            Create a simple setup for testing video stream with GUI
            :return: None
            '''

            global show_video
            if show_video is True:
                #counter += 1
                var=StringVar()
                currCap = video_streams[int(var.get())]
                _, frame = currCap.read()
                # Check if the webcam is opened correctly
                if not currCap.isOpened():
                    raise IOError("Cannot open webcam")

                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_video = Image.fromarray(cv2image)
                image_tk = ImageTk.PhotoImage(image=img_video)
                main_label.image_tk = image_tk
                main_label.configure(image=image_tk)
                main_label.after(1, videoStream)


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
            cv2.imwrite('images/frame%d.jpg' % counter, videoStream())


        def changeCameraStream(video_stream):
            cap = video_stream


        def placeGraph():
            GUIDataPlotting.plotGraph()



        # Start and stop button setup
        start_btn = Button(page_1, text='Start', command=startClicked)
        #init_cams_btn = Button(page_1, text='Initialise cameras', command=startClicked)
        stop_btn = Button(page_1, text='Stop', command=stopClicked)
        calibrate_btn = Button(page_2, text='Calibrate', command=None)

        start_btn.grid(column=0, row=1)
        calibrate_btn.grid(column=1, row=1)
        calibrate_btn.grid_rowconfigure(1, weight=1)
        calibrate_btn.grid_columnconfigure(1, weight=1)



        def initConnectedCams():
            camlist = self.c.initConnectedCams()

            # Camera temp variables.
            cam_list = ['Cam 1', 'Cam 2', 'Cam 3']
            var = StringVar()
            var.set(cam_list[0])
            n = 0

            # Array for added cameras. Future improvements is getting the list of cameras connected.
            video_streams = [cv2.VideoCapture(0), cv2.VideoCapture(1), cv2.VideoCapture(2)]

            # Creating a radio button for each camera connected.
            for i, video_stream in enumerate(video_streams):
                radio_button = Radiobutton(page_1, text='Cam ' + str(i), variable=var, value=n,
                                           command=changeCameraStream(video_stream))
                radio_button.grid(column=0, row=5 + i)
                n += 1

        self.root.mainloop()
