from tkinter import *
from ttkthemes import themed_tk as tk
import os
import time
from GUI import GUIApplication
import re
import threading

class GUILogin():
    '''
    Login before accessing GUI.
    '''
    def __init__(self, mainGUI):

        self.mainGUI = mainGUI

    def startMainApplication(self):
        # Start the main GUI.
        self.mainGUI.start()

    def deleteWindows(self):
        '''
        Delete the windows not used when running GUI
        :return: None
        '''
        screen3.destroy()
        screen2.destroy()
        main_window.destroy()
        self.startMainApplication()



    def deleteEntryWindow(self):
        '''
        Delete the popup box for wrong user/pass
        :return: None
        '''
        screen4.destroy()


    def loginSuccessful(self):
        '''
        Popup that gives user a confirmation that login was successful
        :return: None
        '''
        global screen3
        global windows
        screen3 = Toplevel(main_window)
        screen3.title('Success')
        screen3.geometry('150x100')
        Label(screen3, text='Login Success').pack()
        time.sleep(0.25)
        self.deleteWindows()
        #Button(screen3, text='OK', command=self.deleteWindows).pack()


    def wrongEntry(self):
        '''
        Popup for wrong password/email
        :return: None
        '''
        global screen4
        screen4 = Toplevel(main_window)
        screen4.title('Failed')
        screen4.geometry('200x100')
        Label(screen4, text='Wrong Email or Password').pack()
        Button(screen4, text='OK', command=self.deleteEntryWindow).pack()


    def registerUser(self):
        '''
        Register a user so that you can login
        :return:
        '''
        regex = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
        email_info = email.get()
        password_info = password.get()

        if regex.match(email_info):
            # Create file for saving email and password
            file = open(email_info, 'w')
            file.write(email_info + '\n')
            file.write(password_info)
            file.close()
            email_entry.delete(0, END)
            password_entry.delete(0, END)
            Label(register_window, text='Registration Success', fg='green', font=('calibri', 11)).pack()

        elif not regex.match(email_info):
            email_entry.delete(0, END)
            password_entry.delete(0, END)
            Label(register_window, text='Registration Failed', fg='red', font=('calibri', 11)).pack()


    def loginVerify(self):
        '''
        Verify that the user and password match a registered use.
        :return: None
        '''
        email_name = email_verify.get()
        password1 = password_verify.get()
        email_entry.delete(0, END)
        password_entry1.delete(0, END)

        list_of_files = os.listdir()
        if email_name in list_of_files:
            file1 = open(email_name, 'r')
            verify = file1.read().splitlines()
            if password1 in verify:
                self.loginSuccessful()

            else:
                self.wrongEntry()

        elif email_name is "" and password1 is "":
            self.loginSuccessful()
        else:
            self.wrongEntry()


    def register(self):
        '''
        Create a new window where the user can register.
        Check if the email and password is valid \\ to be added later on
        :return: None
        '''
        global register_window
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
        register_window = Toplevel(main_window.set_theme('equilux'))
        register_window.title('Register')
        register_window.geometry('300x250')

        global email
        global password
        global email_entry
        global password_entry
        email = StringVar()
        password = StringVar()

        Label(register_window, text='Please enter details below').pack()
        Label(register_window, text='').pack()
        Label(register_window, text='Username: ').pack()

        email_entry = Entry(register_window, textvariable=email)
        email_entry.pack()
        Label(register_window, text='Password: ').pack()
        password_entry = Entry(register_window, show='*', textvariable=password)
        password_entry.pack()
        Label(register_window, text='').pack()
        Button(register_window, text='Register', width=10, height=1, command=self.registerUser).pack()


    def login(self):
        '''
        Create a new window where the user can login.
        :return: None
        '''
        global screen2
        screen2 = Toplevel(main_window)
        screen2.title('Login')
        screen2.geometry('300x250')
        screen2.configure()
        Label(screen2, text='Please enter details below to login').pack()
        Label(screen2, text='').pack()

        global email_verify
        global password_verify

        email_verify = StringVar()
        password_verify = StringVar()

        global email_entry
        global password_entry1

        Label(screen2, text='Username: ').pack()
        email_entry = Entry(screen2, textvariable=email_verify)
        email_entry.pack()
        Label(screen2, text='').pack()
        Label(screen2, text='Password: ').pack()
        password_entry1 = Entry(screen2, show='*', textvariable=password_verify)
        password_entry1.pack()
        Label(screen2, text='').pack()
        Button(screen2, text='Login', width=10, height=1, command=self.loginVerify).pack()

    def startLogin(self):
        '''
        Main window that shows when starting the app.
        :return: None
        '''
        global main_window
        main_window = tk.ThemedTk()
        main_window.get_themes()
        main_window.set_theme('equilux')
        main_window.geometry('300x250')
        main_window.title('Boat Pose Estimator 1.0')
        Label(main_window, text='Boat Pose Estimator 1.0', bg='magenta', width='300', height='2', font=('Arial', 13)).pack()
        Label(main_window,text='').pack()
        Button(main_window,text='Login', height='2', width='25', command=self.login).pack()
        Label(main_window,text='').pack()
        Button(main_window,text='Register', height='2', width='25', command=self.register).pack()
        #Button(main_window, text='Hack', height='2', width='25', command=self.loginSuccessful).pack()
        self.login()

        main_window.mainloop()


