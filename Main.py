from Connector import Connector
from TextUI import TextUI

c = Connector()
tui = TextUI(connector=c)
tui.start()
