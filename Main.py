from Connector import Connector
from GUI.GUI import GUIApplication
c = Connector()#("GUI")
GUIApp = GUIApplication(connector=c)
GUIApp.run()
