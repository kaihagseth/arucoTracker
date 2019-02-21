from tkinter import *
import os
from GUI import RunMain


def delete2():
    screen3.destroy()
    screen2.destroy()
    main_window.destroy()
    RunMain()

def delete3():
    screen4.destroy()


def delete4():
    screen5.destroy()


# Popup that gives user a confirmation that login was successful
def loginSuccessful():
    global screen3
    screen3 = Toplevel(main_window)
    screen3.title('Success')
    screen3.geometry('150x100')
    Label(screen3, text='Login Success').pack()
    Button(screen3, text='OK', command=delete2).pack()


def wrongPassword():
    global screen4
    screen4 = Toplevel(main_window)
    screen4.title('Success')
    screen4.geometry('150x100')
    Label(screen4, text='User Not Found or Wrong Password').pack()
    Button(screen4, text='OK', command=delete3).pack()


def userNotFound():
    global screen5
    screen5 = Toplevel(main_window)
    screen5.title('Success')
    screen5.geometry('150x100')
    Label(screen5, text='User Not Found or Wrong Password').pack()
    Button(screen5, text='OK', command=delete4).pack()


def registerUser():
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
