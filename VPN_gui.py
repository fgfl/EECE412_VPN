__author__ = 'Frederick'

import Tkinter

class VPNwindow(Tkinter.Tk):
    # Constructor
    def __init__(self, parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent

        # Create frame







if __name__ == "__main__":
    app = VPNwindow(None)
    app.title("Assignment 3 VPN")
    app.mainloop()