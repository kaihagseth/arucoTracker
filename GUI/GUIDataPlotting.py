import sys
import tkinter as tk
import GUI
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import csv

class dataReading():
    def __init__(self, top=None):
        '''This class configures and populates the data window.
                    top is the toplevel containing window.'''

        _bgcolor = '#424242'  # X11 color: 'gray85'
        _fgcolor = '#d9d9d9'  # X11 color: 'red'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        #top.geometry('600x450+650+150')
        #top.title('Data from Camera')
        #top.configure(background=_fgcolor)
        width = 0.95
        height = 0.2


        self.frame_1 = tk.Frame(top)
        self.frame_1.place(relx=0.017, rely=0.8, relheight=height, relwidth=width)
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(borderwidth='2')
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(background='#424242')
        self.frame_1.configure(width=565)

        self.entry_x = tk.Text(self.frame_1)
        self.entry_x.place(relx=0.018, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_x.configure(background='white')
        self.entry_x.configure(font=('TkTextFont', 24))
        self.entry_x.configure(foreground='black')
        self.entry_x.configure(width=54)
        #self.entry_x.configure(textvariable=pose[0])

        self.entry_y = tk.Text(self.frame_1)
        self.entry_y.place(relx=0.177, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_y.configure(background='white')
        self.entry_y.configure(font=('TkTextFont', 24))
        self.entry_y.configure(foreground='black')
        self.entry_y.configure(width=54)

        self.entry_z = tk.Text(self.frame_1)
        self.entry_z.place(relx=0.336, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_z.configure(background='white')
        self.entry_z.configure(font=('TkTextFont', 24))
        self.entry_z.configure(foreground='black')
        self.entry_z.configure(highlightbackground='#d9d9d9')
        self.entry_z.configure(highlightcolor='black')
        self.entry_z.configure(insertbackground='black')
        self.entry_z.configure(selectbackground='#c4c4c4')
        self.entry_z.configure(selectforeground='black')
        self.entry_z.configure(width=54)

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
        self.btn_plot.configure(text='Plot Data')
        self.btn_plot.configure(command=lambda: plotXYZ(self.graph_frame,1,1,1))

        self.btn_save =  tk.Button(top)
        self.btn_save.pack()
        self.btn_save.configure(background='#665959')
        self.btn_save.configure(disabledforeground='#911515')
        self.btn_save.configure(foreground='#FFFFFF')
        self.btn_save.configure(text='Save Data')


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

def plotXYZ(frame, x ,y, z):

    plot3d = frame
    fig=plt.figure()
    canvas = FigureCanvasTkAgg(fig, master=plot3d)
    canvas.draw()
    x_list = []
    y_list = []
    z_list = []
    ax = plt.axes(projection='3d')
    x_list = x_list.append(int(x))
    y_list = y_list.append(int(y))
    z_list = z_list.append(int(z))
    pos = x_list, y_list, z_list

    if pos is not None:
            if len(x_list) > 50:
                x_list.pop(0)
                x_list = x_list.append(x)
            if len(y_list) > 50:
                y_list.pop(0)
                y_list = y_list.append(x)
            if len(z_list) > 50:
                z_list.pop(0)
                z_list = z_list.append(x)
            ax.plot3D(x,y,z, 'green')
    toolbar = NavigationToolbar2Tk(canvas, plot3d)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def plotGraph(frame):
    pass
    ''' Draw a matplotlib figure onto a Tk canvas
    loc: location of top-left corner of figure on canvas in pixels.
    Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
    '''
    global entry_x, entry_y, entry_z
    plot3d = frame
    fig = plt.figure()
    #plot3d.title('Graph')
    #fig = Figure(figsize=(3, 2), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=plot3d)  # A tk.DrawingArea.
    canvas.draw()

    ax = plt.axes(projection='3d')

    x = []
    y = []
    z = []

    with open('logs\position_log.csv', 'r') as csv_file:
        plots = csv.reader(csv_file, delimiter=',', lineterminator='\n', dialect='excel')
        for row in plots:
            try:
                x.append(int(row[0]))
                y.append(int(row[1]))
                z.append(int(row[2]))
            except(TypeError, ValueError):
                print('Error ignored')
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    array = [x,y,z]
    for i in array:

        if x is not x:
            x = np.asarray(x)
        if y is not y:
            y = np.asarray(y)
        if z is not z:
            z = np.asarray(z)
        if i >= 50:
            x.pop(0)
            x.append(i)
            y.pop(0)
            y.append(i)
            z.pop(0)
            z.append(i)

        #ax.plot3D(x[i], y[i], z[i], 'red')
        ax.plot3D(x, y, z, 'red')

    toolbar = NavigationToolbar2Tk(canvas, plot3d)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

if __name__ == '__main__':
    vp_start_gui()
