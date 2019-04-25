from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from random import randrange
import time
from GUI import GUIApplication


t_data, x_data, y_data, z_data = [], [], [], []

figure = plt.figure()
ax = figure.subplots(3,1,sharex=True,sharey=True)
line, = ax[0].plot(t_data, x_data, 'r')
line2, = ax[1].plot(t_data,y_data, 'c')
line3, = ax[2].plot(t_data,z_data, '-')
start_time = time.time()

def update(frame):
    elapsed_time = time.time()-start_time
    t_data.append(elapsed_time)
    x_data.append(randrange(-100, 100))
    y_data.append(randrange(-100, 100))
    z_data.append(randrange(-100, 100))
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
animation = FuncAnimation(figure, update, interval=100)
plt.show()