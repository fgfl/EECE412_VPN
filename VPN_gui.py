__author__ = 'Frederick'
# VPN_gui.py
#
# Construct the whole gui here
# Frame code adapted from
# http://stackoverflow.com/questions/7546050/python-tkinter-changing-the-window-basics
#
# October 10, 2014

import Tkinter

class VPNWindow(Tkinter.Tk):
    # Constructor
    def __init__(self, parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initializeFrameContainer()


    def initializeFrameContainer(self):
        # Create container for frames
        container = Tkinter.Frame(self)
        container.grid()
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (startPage,svrConfigPage, svrWaitPage, clientConfigPage,
                  messagingPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="NEWS")

        self.show_frame(startPage)

    def show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()







class startPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent

    def initializeStartPage(self):
        self.grid()
        # Some space on top
        self.headerText = "Enter the key and select the operation mode"
        headerSpace = Tkinter.Label(self, textVariable=self.headerText)
        headerSpace.grid(column=0, row=0, columnspan=2, sticky="EW")
        # Mode buttons
        serverModeButton = Tkinter.Button(self, text=u"Sever Mode")
        serverModeButton.grid(column=0, row=1, sticky="EW")
        clientModeButton = Tkinter.Button(self, text=u"Client Mode")
        clientModeButton.grid(column=1, row=1, sticky="EW")
        # Blank line
        blankLine = Tkinter.label(self)
        blankLine.grid(column=0, row=2, columnspan=2)
        # Line for entering key
        keyPrompt = Tkinter.Label(self, textVariable="Key:")
        keyPrompt.grid(column=0, row=3)
        self.keyEntry = Tkinter.Entry(self)
        self.keyEntry.grid(column=1, row=3, sticky="EW")

class svrConfigPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent

class svrWaitPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent

class clientConfigPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent

class messagingPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
if __name__ == "__main__":
    app = VPNWindow(None)
    app.title("Assignment 3 VPN")
    app.mainloop()