from Connector import Connector
from GUI import GUIApplication
from GUILogin import GUILogin

c = Connector()
mainGUI = GUIApplication(connector=c)
guil = GUILogin(mainGUI=mainGUI)
guil.startLogin()
