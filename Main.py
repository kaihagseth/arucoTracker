from Connector import Connector
from GUI import GUIApplication
from GUILogin import GUILogin

cam_list = [0]
mainGUI = GUIApplication(cam_list)
c = Connector(mainGUI)
guil = GUILogin(mainGUI=mainGUI)
guil.startLogin()
c.startApplication()
