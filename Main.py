from Connector import Connector
from arucoPoseEstimator import ArucoPoseEstimator
from GUILogin import GUILogin
from GUI import GUIApplication

c = Connector()
mainGUI = GUIApplication(connector=c)
guil = GUILogin(mainGUI=mainGUI)
guil.startLogin()
