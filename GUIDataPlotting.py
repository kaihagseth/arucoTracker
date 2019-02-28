import sys
import tkinter as tk
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import Connector


class dataReading:
    def __init__(self, top=None):
        '''This class configures and populates the data window.
                    top is the toplevel containing window.'''

        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#aaa000'  # X11 color: 'red'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        top.geometry("600x450+650+150")
        top.title("Data from Camera")
        top.configure(background=_fgcolor)
        width = 0.95
        height = 0.2

        pose = []


        self.frame_1 = tk.Frame(top)
        self.frame_1.place(relx=0.017, rely=0.8, relheight=height, relwidth=width)
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(borderwidth='2')
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(background='#000000')
        self.frame_1.configure(width=565)

        self.entry_x = tk.Entry(self.frame_1)
        self.entry_x.place(relx=0.018, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_x.configure(background='red')
        self.entry_x.configure(font='TkTextFont')
        self.entry_x.configure(foreground='black')
        self.entry_x.configure(width=54)
        #self.entry_x.configure(textvariable=pose[0])

        self.entry_y = tk.Entry(self.frame_1)
        self.entry_y.place(relx=0.177, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_y.configure(background='white')
        self.entry_y.configure(font='TkTextFont')
        self.entry_y.configure(foreground='black')
        self.entry_y.configure(width=54)
        #self.entry_y.configure(textvariable=pose[0])

        self.entry_z = tk.Entry(self.frame_1)
        self.entry_z.place(relx=0.336, rely=0.588, relheight=0.282
                           , relwidth=0.096)
        self.entry_z.configure(background='white')
        self.entry_z.configure(font='TkTextFont')
        self.entry_z.configure(foreground='black')
        self.entry_z.configure(highlightbackground='#d9d9d9')
        self.entry_z.configure(highlightcolor='black')
        self.entry_z.configure(insertbackground='black')
        self.entry_z.configure(selectbackground='#c4c4c4')
        self.entry_z.configure(selectforeground='black')
        self.entry_z.configure(width=54)


        self.entry_pitch = tk.Entry(self.frame_1)
        self.entry_pitch.place(relx=0.531, rely=0.588, relheight=0.282
                               , relwidth=0.096)
        self.entry_pitch.configure(background='white')
        self.entry_pitch.configure(font='TkTextFont')
        self.entry_pitch.configure(foreground='black')
        self.entry_pitch.configure(highlightbackground='#d9d9d9')
        self.entry_pitch.configure(highlightcolor='black')
        self.entry_pitch.configure(insertbackground='black')
        self.entry_pitch.configure(selectbackground='#c4c4c4')
        self.entry_pitch.configure(selectforeground='black')
        self.entry_pitch.configure(width=54)


        self.entry_yaw = tk.Entry(self.frame_1)
        self.entry_yaw.place(relx=0.867, rely=0.588, relheight=0.282
                             , relwidth=0.096)
        self.entry_yaw.configure(background='white')
        self.entry_yaw.configure(font='TkTextFont')
        self.entry_yaw.configure(foreground='black')
        self.entry_yaw.configure(highlightbackground='#d9d9d9')
        self.entry_yaw.configure(highlightcolor='black')
        self.entry_yaw.configure(insertbackground='black')
        self.entry_yaw.configure(selectbackground='#c4c4c4')
        self.entry_yaw.configure(selectforeground='black')
        self.entry_yaw.configure(width=54)

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

        self.entry_yaw = tk.Entry(self.frame_1)
        self.entry_yaw.place(relx=0.708, rely=0.588, relheight=0.282
                             , relwidth=0.096)
        self.entry_yaw.configure(background='white')
        self.entry_yaw.configure(font='TkTextFont')
        self.entry_yaw.configure(foreground='black')
        self.entry_yaw.configure(highlightbackground='#d9d9d9')
        self.entry_yaw.configure(highlightcolor='black')
        self.entry_yaw.configure(insertbackground='black')
        self.entry_yaw.configure(selectbackground='#c4c4c4')
        self.entry_yaw.configure(selectforeground='black')
        self.entry_yaw.configure(width=54)

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
        self.graph_frame.place(relx=0.15, rely=0.2, height=200, width=425)
        self.graph_frame.configure(background='red')
        self.graph_frame.configure(borderwidth='2')
        self.graph_frame.configure(relief='ridge')
        self.graph_frame.configure(width=233)
        self.graph_frame.configure(command=plotGraph(self.graph_frame))

        self.label_2 = tk.Label(top)
        self.label_2.place(relx=0.335, rely=0.1, height=30, width=165)
        self.label_2.configure(background='#d9d9d9')
        self.label_2.configure(disabledforeground='#a3a3a3')
        self.label_2.configure(foreground='#000000')
        self.label_2.configure(text='''Live Plotting of Data''')
        self.label_2.configure(width=164)

def vp_start_gui():
    '''Starting point when module is the main routine.'''

    global val, w, root
    root = tk.Tk()
    top = dataReading(root)
    root.mainloop()


w = None


def createDataWindow(root, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = tk.Toplevel(root)
    top = dataReading(w)
    return w, top


def destroy_Toplevel1():
    '''
    Closes the window
    :return:
    '''
    global w
    w.destroy()
    w = None


def plotGraph(frame):
    ''' Draw a matplotlib figure onto a Tk canvas
    loc: location of top-left corner of figure on canvas in pixels.
    Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
    '''
    plot3d = frame
    #plot3d.title('Graph')
    fig = Figure(figsize=(3, 2), dpi=100)
    canvas = FigureCanvasTkAgg(fig, master=plot3d)  # A tk.DrawingArea.
    canvas.draw()

    ax = fig.add_subplot(111, projection="3d")
    for i in range(10):
        y = np.random.random()
        ax.scatter(i, y)

    toolbar = NavigationToolbar2Tk(canvas, plot3d)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

if __name__ == '__main__':
    vp_start_gui()
