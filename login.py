from tkinter import *
import os
from GUI import RunMain


def deleteWindows():
    '''
    Delete the windows not used when running GUI
    :return: None
    '''
    screen3.destroy()
    screen2.destroy()
    main_window.destroy()
    RunMain()


def deleteWrongPassWindow():
    '''
    Delete the popup box for wrong user/pass
    :return: None
    '''
    screen4.destroy()


def deleteWrongUserWindow():
    '''
    Delete the popup box for wrong username/password
    :return: None
    '''
    screen5.destroy()


def loginSuccessful():
    '''
    Popup that gives user a confirmation that login was successful
    :return: None
    '''
    global screen3
    screen3 = Toplevel(main_window)
    screen3.title('Success')
    screen3.geometry('150x100')
    Label(screen3, text='Login Success').pack()
    Button(screen3, text='OK', command=deleteWindows).pack()


def wrongPassword():
    '''
    Popup for wrong password/username
    :return: None
    '''
    global screen4
    screen4 = Toplevel(main_window)
    screen4.title('Success')
    screen4.geometry('150x100')
    Label(screen4, text='User Not Found or Wrong Password').pack()
    Button(screen4, text='OK', command=deleteWrongPassWindow).pack()


def userNotFound():
    '''
    Popup for wrong password/username
    :return:
    '''
    global screen5
    screen5 = Toplevel(main_window)
    screen5.title('Success')
    screen5.geometry('150x100')
    Label(screen5, text='User Not Found or Wrong Password').pack()
    Button(screen5, text='OK', command=deleteWrongUserWindow).pack()


def registerUser():
    '''
    Register a user so that you can login
    :return:
    '''
    print('working')

    username_info = username.get()
    password_info = password.get()

    file = open(username_info, 'w')
    file.write(username_info + '\n')
    file.write(password_info)
    file.close()

    username_entry.delete(0, END)
    password_entry.delete(0, END)

    Label(screen1, text='Registration Success', fg='green', font=('calibri', 11)).pack()


def loginVerify():
    '''
    Verify that the user and password match a registered use.
    :return: None
    '''
    username1 = username_verify.get()
    password1 = password_verify.get()
    username_entry1.delete(0, END)
    password_entry1.delete(0, END)

    list_of_files = os.listdir()
    if username1 in list_of_files:
        file1 = open(username1, 'r')
        verify = file1.read().splitlines()
        if password1 in verify:
            loginSuccessful()

        else:
            wrongPassword()

    else:
        userNotFound()


def register():
    '''
    Create a new window where the user can register.
    :return: None
    '''
    global screen1
    screen1 = Toplevel(main_window)
    screen1.title('Register')
    screen1.geometry('300x250')

    global username
    global password
    global username_entry
    global password_entry
    username = StringVar()
    password = StringVar()

    Label(screen1, text='Please enter details below').pack()
    Label(screen1, text='').pack()
    Label(screen1, text='Username * ').pack()

    username_entry = Entry(screen1, textvariable=username)
    username_entry.pack()
    Label(screen1, text='Password * ').pack()
    password_entry = Entry(screen1, show='*', textvariable=password)
    password_entry.pack()
    Label(screen1, text='').pack()
    Button(screen1, text='Register', width=10, height=1, command=registerUser).pack()


def login():
    '''
    Create a new window where the user can login.
    :return: None
    '''
    global screen2
    screen2 = Toplevel(main_window)
    screen2.title('Login')
    screen2.geometry('300x250')
    Label(screen2, text='Please enter details below to login').pack()
    Label(screen2, text='').pack()

    global username_verify
    global password_verify

    username_verify = StringVar()
    password_verify = StringVar()

    global username_entry1
    global password_entry1

    Label(screen2, text='Username: ').pack()
    username_entry1 = Entry(screen2, textvariable=username_verify)
    username_entry1.pack()
    Label(screen2, text='').pack()
    Label(screen2, text='Password: ').pack()
    password_entry1 = Entry(screen2, show='*', textvariable=password_verify)
    password_entry1.pack()
    Label(screen2, text='').pack()
    Button(screen2, text='Login', width=10, height=1, command=loginVerify).pack()


def mainScreen():
    '''
    Main window that shows when starting the app.
    :return: None
    '''
    global main_window
    main_window = Tk()
    main_window.geometry('300x250')
    main_window.title('Boat Pose Estimator 1.0')
    Label(text='Boat Pose Estimator 1.0', bg='magenta', width='300', height='2', font=('Arial', 13)).pack()
    Label(text='').pack()
    Button(text='Login', height='2', width='25', command=login).pack()
    Label(text='').pack()
    Button(text='Register', height='2', width='25', command=register).pack()

    main_window.mainloop()


mainScreen()
