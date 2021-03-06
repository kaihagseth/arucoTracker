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

class ArucoBoardUnit():
    def __init__(self, board, parent):
        self.boardIsActive = True
        self.id = board.ID
        self.container = Frame(parent, bd=5)
        self.container.configure(borderwidth='2', padx='10', relief=GROOVE,bg='#424242')
        self.conStatusLabel = Label(self.container, text="Active", fg="green", bg='#424242',font=("Courier", 30))
        self.conStatusLabel.grid(row=0, column=0, columnspan=3)
        self.btn = Button(self.container, text="Deactivate", command=self.deactivateBoard,fg="white", bg='#424242')
        self.btn.grid(row=1,column=2)
        self.id_label = Label(self.container, text="ID: " + str(self.id),bg='#424242',fg="white")
        self.id_label.grid(row=1, column=0)

        self.pht = board.getBoardImage((175,175))
        self.pht = cv2.cvtColor(self.pht, cv2.COLOR_BGR2RGB)
        self.pht = Image.fromarray(self.pht)
        self.pht = ImageTk.PhotoImage(self.pht)

        img = Label(self.container, image=self.pht,bg='#424242')
        img.grid(row=3, column=0, columnspan=3)
        self.container.grid(row=0, column=self.id)

    def deactivateBoard(self):
        """
        Deactivate the board for use in PoseEstimator.
        :return:
        """
        self.boardIsActive = False
        self.conStatusLabel.config(text="Not active", fg="red")
        self.btn.config(text="Log this board",command=self.activateBoard)

    def activateBoard(self):
        """
        Activate the board for use in PoseEstimator.
        :return:
        """
        self.boardIsActive = False
        self.conStatusLabel.config(text="Active", fg="green")
        self.btn.config(text="Stop logging this board", command=self.deactivateBoard)

    def removeBoard(self):
        """
        Removes this board from the GUI
        :return:None
        """
        self.container.grid_remove()