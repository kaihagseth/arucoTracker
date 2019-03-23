from Connector import Connector
from GUI import GUIApplication
from GUILogin import GUILogin


mainGUI = GUIApplication()
c = Connector(mainGUI)
guil = GUILogin(mainGUI=mainGUI)
guil.startLogin()
