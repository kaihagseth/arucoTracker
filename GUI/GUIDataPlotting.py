import tkinter as tk
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time

class dataReading():
    def __init__(self, top=None):
        '''This class configures and populates the data window.
                    top is the toplevel containing window.'''

        _bgcolor = '#424242'  # X11 color: 'gray85'
        _fgcolor = '#d9d9d9'  # X11 color: 'red'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        width = 0.95
        height = 0.2

        # Frame configuration for the data page
        self.frame_1 = tk.Frame(top)
        self.frame_1.place(relx=0.017, rely=0.8, relheight=height, relwidth=width)
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(borderwidth='2')
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(background='#424242')
        self.frame_1.configure(width=565)

        # Variable for plotting data
        self.plot = False
        self.x_value = DoubleVar()
        self.y_value = DoubleVar()
        self.z_value = DoubleVar()

        self.entry_x = tk.Label(self.frame_1)
        self.entry_x.place(relx=0.018, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_x.configure(background='white')
        self.entry_x.configure(font=('TkTextFont', 24))
        self.entry_x.configure(foreground='black')
        self.entry_x.configure(textvariable=self.x_value)
        self.entry_x.configure(width=54)

        self.entry_y = tk.Label(self.frame_1)
        self.entry_y.place(relx=0.177, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_y.configure(background='white')
        self.entry_y.configure(font=('TkTextFont', 24))
        self.entry_y.configure(foreground='black')
        self.entry_x.configure(textvariable=self.y_value)
        self.entry_y.configure(width=54)

        self.entry_z = tk.Label(self.frame_1)
        self.entry_z.place(relx=0.336, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_y.configure(background='white')
        self.entry_y.configure(font=('TkTextFont', 24))
        self.entry_y.configure(foreground='black')
        self.entry_x.configure(textvariable=self.z_value)
        self.entry_y.configure(width=54)

        self.entry_pitch = tk.Text(self.frame_1)
        self.entry_pitch.place(relx=0.531, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_pitch.configure(background='white')
        self.entry_pitch.configure(font=('TkTextFont', 24))
        self.entry_pitch.configure(foreground='black')
        self.entry_pitch.configure(highlightbackground='#d9d9d9')
        self.entry_pitch.configure(highlightcolor='black')
        self.entry_pitch.configure(insertbackground='black')
        self.entry_pitch.configure(selectbackground='#c4c4c4')
        self.entry_pitch.configure(selectforeground='black')
        self.entry_pitch.configure(width=54)

        self.entry_yaw = tk.Text(self.frame_1)
        self.entry_yaw.place(relx=0.867, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_yaw.configure(background='white')
        self.entry_yaw.configure(font=('TkTextFont', 24))
        self.entry_yaw.configure(foreground='black')
        self.entry_yaw.configure(highlightbackground='#d9d9d9')
        self.entry_yaw.configure(highlightcolor='black')
        self.entry_yaw.configure(insertbackground='black')
        self.entry_yaw.configure(selectbackground='#c4c4c4')
        self.entry_yaw.configure(selectforeground='black')
        self.entry_yaw.configure(width=54)

        self.entry_roll = tk.Text(self.frame_1)
        self.entry_roll.place(relx=0.708, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_roll.configure(background='white')
        self.entry_roll.configure(font=('TkTextFont', 24))
        self.entry_roll.configure(foreground='black')
        self.entry_roll.configure(highlightbackground='#d9d9d9')
        self.entry_roll.configure(highlightcolor='black')
        self.entry_roll.configure(insertbackground='black')
        self.entry_roll.configure(selectbackground='#c4c4c4')
        self.entry_roll.configure(selectforeground='black')
        self.entry_roll.configure(width=54)

        self.label_x = tk.Label(self.frame_1)
        self.label_x.place(relx=0.025, rely=0.235, height=21, width=47)
        self.label_x.configure(background='#d9d9d9')
        self.label_x.configure(disabledforeground='#a3a3a3')
        self.label_x.configure(foreground='#000000')
        self.label_x.configure(text='''X-Value''')

        self.label_y = tk.Label(self.frame_1)
        self.label_y.place(relx=0.185, rely=0.235, height=21, width=44)
        self.label_y.configure(activebackground='#f9f9f9')
        self.label_y.configure(activeforeground='black')
        self.label_y.configure(background='#d9d9d9')
        self.label_y.configure(disabledforeground='#a3a3a3')
        self.label_y.configure(foreground='#000000')
        self.label_y.configure(highlightbackground='#d9d9d9')
        self.label_y.configure(highlightcolor='black')
        self.label_y.configure(text='''Y-Value''')
        self.label_y.configure(width=44)

        self.label_z = tk.Label(self.frame_1)
        self.label_z.place(relx=0.342, rely=0.235, height=21, width=44)
        self.label_z.configure(activebackground='#f9f9f9')
        self.label_z.configure(activeforeground='black')
        self.label_z.configure(background='#d9d9d9')
        self.label_z.configure(disabledforeground='#a3a3a3')
        self.label_z.configure(foreground='#000000')
        self.label_z.configure(highlightbackground='#d9d9d9')
        self.label_z.configure(highlightcolor='black')
        self.label_z.configure(text='''Z-Value''')
        self.label_z.configure(width=44)

        self.label_pitch = tk.Label(self.frame_1)
        self.label_pitch.place(relx=0.549, rely=0.235, height=21, width=34)
        self.label_pitch.configure(activebackground='#f9f9f9')
        self.label_pitch.configure(activeforeground='black')
        self.label_pitch.configure(background='#d9d9d9')
        self.label_pitch.configure(disabledforeground='#a3a3a3')
        self.label_pitch.configure(foreground='#000000')
        self.label_pitch.configure(highlightbackground='#d9d9d9')
        self.label_pitch.configure(highlightcolor='black')
        self.label_pitch.configure(text='''Pitch''')

        self.label_roll = tk.Label(self.frame_1)
        self.label_roll.place(relx=0.885, rely=0.235, height=21, width=34)
        self.label_roll.configure(activebackground='#f9f9f9')
        self.label_roll.configure(activeforeground='black')
        self.label_roll.configure(background='#d9d9d9')
        self.label_roll.configure(disabledforeground='#a3a3a3')
        self.label_roll.configure(foreground='#000000')
        self.label_roll.configure(highlightbackground='#d9d9d9')
        self.label_roll.configure(highlightcolor='black')
        self.label_roll.configure(text='''Roll''')

        self.label_yaw = tk.Label(self.frame_1)
        self.label_yaw.place(relx=0.715, rely=0.235, height=21, width=44)
        self.label_yaw.configure(activebackground='#f9f9f9')
        self.label_yaw.configure(activeforeground='black')
        self.label_yaw.configure(background='#d9d9d9')
        self.label_yaw.configure(disabledforeground='#a3a3a3')
        self.label_yaw.configure(foreground='#000000')
        self.label_yaw.configure(highlightbackground='#d9d9d9')
        self.label_yaw.configure(highlightcolor='black')
        self.label_yaw.configure(text='''Yaw''')
        self.label_yaw.configure(width=44)

        self.graph_frame = tk.Frame(top)
        self.graph_frame.pack()
        self.graph_frame.configure(background='red')
        self.graph_frame.configure(borderwidth='2')
        self.graph_frame.configure(relief='ridge')
        self.graph_frame.configure(width=750)
        self.graph_frame.configure(height=500)

        self.btn_plot = tk.Button(top)
        self.btn_plot.pack()
        self.btn_plot.configure(background='#665959')
        self.btn_plot.configure(disabledforeground='#911515')
        self.btn_plot.configure(foreground='#FFFFFF')
        self.btn_plot.configure(text='Start')
        #self.btn_plot.configure(command=lambda: (self.hideButton(),plotXYZ(self.graph_frame,1,2,3)))

        self.btn_save =  tk.Button(top)
        self.btn_save.pack()
        self.btn_save.configure(background='#665959')
        self.btn_save.configure(disabledforeground='#911515')
        self.btn_save.configure(foreground='#FFFFFF')
        self.btn_save.configure(text='Stop')
        self.btn_save.configure(command=lambda: self.showButton(self))

    def hideButton(self):
        self.btn_plot.lower()
        self.plot = True

    def showButton(self, button):
        self.btn_plot.lift()
        self.plot = False

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = dataReading(root)
    root.mainloop()


w = None


def createDataWindow(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win
    frame = root
    top = dataReading(frame)
    return top


def destroy_Toplevel1():
    '''
    Closes the window
    :return:
    '''
    global w
    w.destroy()
    w = None


def plotXYZ(box, x ,y, z):
    t_data, x_data, y_data, z_data = [], [], [], []
    figure = plt.figure()
    ax = figure.subplots(3, 1, sharex=True, sharey=True)
    line, = ax[0].plot(t_data, x_data, 'r')
    line2, = ax[1].plot(t_data, y_data, 'c')
    line3, = ax[2].plot(t_data, z_data, '-')
    start_time = time.time()

    def update(frame):
        elapsed_time = time.time() - start_time
        t_data.append(elapsed_time)
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)
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
    animation = FuncAnimation(figure, update, interval=200)
    plt.show()

if __name__ == '__main__':
    vp_start_gui()

