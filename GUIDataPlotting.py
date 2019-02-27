import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import numpy as np
import Connector


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
    t = np.arange(0, 3, .01)
    ax.plot(t, 2 * np.sin(2 * np.pi * t))

    toolbar = NavigationToolbar2Tk(canvas, plot3d)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class dataReading():
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

        pose = Connector.getPose()


        self.frame_1 = tk.Frame(top)
        self.frame_1.place(relx=0.017, rely=0.8, relheight=0.189, relwidth=0.942)
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(borderwidth='2')
        self.frame_1.configure(relief='groove')
        self.frame_1.configure(background='#000000')
        self.frame_1.configure(width=565)

        self.entry_1 = tk.Entry(self.frame_1)
        self.entry_1.place(relx=0.018, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_1.configure(background='red')
        self.entry_1.configure(font='TkTextFont')
        self.entry_1.configure(foreground='black')
        self.entry_1.configure(width=54)
        self.entry_1.configure(textvariable=pose[0])

        self.entry_2 = tk.Entry(self.frame_1)
        self.entry_2.place(relx=0.177, rely=0.588, relheight=0.282, relwidth=0.096)
        self.entry_2.configure(background='white')
        self.entry_2.configure(font='TkTextFont')
        self.entry_2.configure(foreground='black')
        self.entry_2.configure(width=54)
        self.entry_2.configure(textvariable=pose[0])

        self.Text2_1 = tk.Text(self.frame_1)
        self.Text2_1.place(relx=0.336, rely=0.588, relheight=0.282
                           , relwidth=0.096)
        self.Text2_1.configure(background='white')
        self.Text2_1.configure(font='TkTextFont')
        self.Text2_1.configure(foreground='black')
        self.Text2_1.configure(highlightbackground='#d9d9d9')
        self.Text2_1.configure(highlightcolor='black')
        self.Text2_1.configure(insertbackground='black')
        self.Text2_1.configure(selectbackground='#c4c4c4')
        self.Text2_1.configure(selectforeground='black')
        self.Text2_1.configure(width=54)
        self.Text2_1.configure(wrap='word')

        self.Text2_2 = tk.Text(self.frame_1)
        self.Text2_2.place(relx=0.531, rely=0.588, relheight=0.282
                           , relwidth=0.096)
        self.Text2_2.configure(background='white')
        self.Text2_2.configure(font='TkTextFont')
        self.Text2_2.configure(foreground='black')
        self.Text2_2.configure(highlightbackground='#d9d9d9')
        self.Text2_2.configure(highlightcolor='black')
        self.Text2_2.configure(insertbackground='black')
        self.Text2_2.configure(selectbackground='#c4c4c4')
        self.Text2_2.configure(selectforeground='black')
        self.Text2_2.configure(width=54)
        self.Text2_2.configure(wrap='word')

        self.text_3 = tk.Text(self.frame_1)
        self.text_3.place(relx=0.867, rely=0.588, relheight=0.282
                          , relwidth=0.096)
        self.text_3.configure(background='white')
        self.text_3.configure(font='TkTextFont')
        self.text_3.configure(foreground='black')
        self.text_3.configure(highlightbackground='#d9d9d9')
        self.text_3.configure(highlightcolor='black')
        self.text_3.configure(insertbackground='black')
        self.text_3.configure(selectbackground='#c4c4c4')
        self.text_3.configure(selectforeground='black')
        self.text_3.configure(width=54)
        self.text_3.configure(wrap='word')

        self.label_1 = tk.Label(self.frame_1)
        self.label_1.place(relx=0.025, rely=0.235, height=21, width=47)
        self.label_1.configure(background='#d9d9d9')
        self.label_1.configure(disabledforeground='#a3a3a3')
        self.label_1.configure(foreground='#000000')
        self.label_1.configure(text='''X-Value''')

        self.label_5 = tk.Label(self.frame_1)
        self.label_5.place(relx=0.185, rely=0.235, height=21, width=44)
        self.label_5.configure(activebackground='#f9f9f9')
        self.label_5.configure(activeforeground='black')
        self.label_5.configure(background='#d9d9d9')
        self.label_5.configure(disabledforeground='#a3a3a3')
        self.label_5.configure(foreground='#000000')
        self.label_5.configure(highlightbackground='#d9d9d9')
        self.label_5.configure(highlightcolor='black')
        self.label_5.configure(text='''Y-Value''')
        self.label_5.configure(width=44)

        self.label_6 = tk.Label(self.frame_1)
        self.label_6.place(relx=0.342, rely=0.235, height=21, width=44)
        self.label_6.configure(activebackground='#f9f9f9')
        self.label_6.configure(activeforeground='black')
        self.label_6.configure(background='#d9d9d9')
        self.label_6.configure(disabledforeground='#a3a3a3')
        self.label_6.configure(foreground='#000000')
        self.label_6.configure(highlightbackground='#d9d9d9')
        self.label_6.configure(highlightcolor='black')
        self.label_6.configure(text='''Z-Value''')
        self.label_6.configure(width=44)

        self.label_7 = tk.Label(self.frame_1)
        self.label_7.place(relx=0.549, rely=0.235, height=21, width=34)
        self.label_7.configure(activebackground='#f9f9f9')
        self.label_7.configure(activeforeground='black')
        self.label_7.configure(background='#d9d9d9')
        self.label_7.configure(disabledforeground='#a3a3a3')
        self.label_7.configure(foreground='#000000')
        self.label_7.configure(highlightbackground='#d9d9d9')
        self.label_7.configure(highlightcolor='black')
        self.label_7.configure(text='''Pitch''')

        self.label_8 = tk.Label(self.frame_1)
        self.label_8.place(relx=0.885, rely=0.235, height=21, width=34)
        self.label_8.configure(activebackground='#f9f9f9')
        self.label_8.configure(activeforeground='black')
        self.label_8.configure(background='#d9d9d9')
        self.label_8.configure(disabledforeground='#a3a3a3')
        self.label_8.configure(foreground='#000000')
        self.label_8.configure(highlightbackground='#d9d9d9')
        self.label_8.configure(highlightcolor='black')
        self.label_8.configure(text='''Roll''')

        self.text_3 = tk.Text(self.frame_1)
        self.text_3.place(relx=0.708, rely=0.588, relheight=0.282
                          , relwidth=0.096)
        self.text_3.configure(background='white')
        self.text_3.configure(font='TkTextFont')
        self.text_3.configure(foreground='black')
        self.text_3.configure(highlightbackground='#d9d9d9')
        self.text_3.configure(highlightcolor='black')
        self.text_3.configure(insertbackground='black')
        self.text_3.configure(selectbackground='#c4c4c4')
        self.text_3.configure(selectforeground='black')
        self.text_3.configure(width=54)
        self.text_3.configure(wrap='word')

        self.label_4 = tk.Label(self.frame_1)
        self.label_4.place(relx=0.715, rely=0.235, height=21, width=44)
        self.label_4.configure(activebackground='#f9f9f9')
        self.label_4.configure(activeforeground='black')
        self.label_4.configure(background='#d9d9d9')
        self.label_4.configure(disabledforeground='#a3a3a3')
        self.label_4.configure(foreground='#000000')
        self.label_4.configure(highlightbackground='#d9d9d9')
        self.label_4.configure(highlightcolor='black')
        self.label_4.configure(text='''Yaw''')
        self.label_4.configure(width=44)

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


if __name__ == '__main__':
    vp_start_gui()
