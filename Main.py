from Connector import Connector
from GUI.GUI import GUIApplication
c = Connector()#("GUI")
#c.run() Don't run froim here. Run from GUI.
GUIApp = GUIApplication(connector=c)
GUIApp.run()
