from Connector import Connector
from GUI import GUIApplication
from GUILogin import GUILogin
from VisionEntityClasses.arucoPoseEstimator import ArucoPoseEstimator

c = Connector()
mainGUI = GUIApplication(connector=c)
guil = GUILogin(mainGUI=mainGUI)
guil.startLogin()
