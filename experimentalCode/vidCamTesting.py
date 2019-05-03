## Format http://[myCamera]/
#import cv2
#
#print('Starting bef')
#stream = cv2.VideoCapture('http://root:root@169.254.82.79/axis-cgi/mjpg/video.cgi')
#print('Stream is opened: ' + str(stream.isOpened()))
#
##stream = cv2.VideoCapture('protocol://IP:port/80')
#
## Use the next line if your camera has a username and password
## stream = cv2.VideoCapture('protocol://username:password@IP:port/1')
#print('Starting')
#while True:
#
#    r, f = stream.read()
#    print('Stream grabbed')
#    cv2.imshow('IP Camera stream',f)
#
#    if cv2.waitKey(1) & 0xFF == ord('q'):
#        break
#
#cv2.destroyAllWindows()

import requests

#http://myserver/axis-cgi/com/ptz.cgi?rpan=10&camera=3
req = requests.get('http://root:root@169.254.54.160/axis-cgi/com/ptz.cgi?rpan=100&camera=3')
print('Printing.')
print(str(req))