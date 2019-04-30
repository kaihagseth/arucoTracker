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



class QualityLevelBar():

    def __init__(self, parent, numberOfLevels=9,  width=800, height=200, colorstring='blue'):
        self.mainFrame = Frame(parent, width=width, height=height)
        self.mainFrame.config(bg=colorstring)
        pb = ttk.Progressbar(parent,orient="horizontal",length=300,mode="determinate")
        #pb.config(highlightbackground='black')
        pb.pack()
        maxValue = 100
        currentValue=50
        pb["value"]=currentValue
        self.mainFrame.pack()
        pb["maximum"]= maxValue
        #self.levelbarList = []
        #for i in range(0,numberOfLevels):
        #    frame = Frame(self.mainFrame, height=height,width=(width/numberOfLevels),pady=5,padx=5)
        #    frame.grid(column=i,row=0)
        #    childframe= Frame(frame, height=height,width=(width/numberOfLevels),pady=5,padx=5, bg='#424242')
        #    childframe.pack()
        #    if i < 3:
        #        frame.config(bg="red")
        #    elif i >= 3 and i < 6:
        #        frame.config(bg="yellow")
        #    else:
        #        frame.config(bg="green")
        #    self.levelbarList.append(childframe)
        #
        #
if __name__ == '__main__':
    root = Tk()
    QLB = QualityLevelBar(root)
    root.mainloop()