__author__ = 'Frederick'
# VPN_gui.py
#
# Construct the whole gui here
# Frame code adapted from
# http://stackoverflow.com/questions/7546050/python-tkinter-changing-the-window-basics
#
# October 10, 2014

import Tkinter

y_bottom_padding = (0, 10)
x_right_padding = (0, 5)
debugBoxWidth = 500
enableDebugString = "Enable debug"
wrapTextLength = 250


class VPNWindow(Tkinter.Tk):
    # Constructor
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initializeFrameContainer()


    def initializeFrameContainer(self):
        self.grid()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create container for frames
        container = Tkinter.Frame(self, padx=5, pady=5)
        container.grid(sticky="NEWS")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (startPage, svrConfigPage, svrWaitPage, clientConfigPage,
                  messagingPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        #self.show_frame(startPage)
        # self.show_frame(svrConfigPage)
        #self.show_frame(svrWaitPage)
        self.show_frame(clientConfigPage)

    def show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()


class startPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeStartPage(controller)

    def initializeStartPage(self, controller):
        self.svrCheckBoxState = Tkinter.IntVar()
        self.clientCheckBoxState = Tkinter.IntVar()

        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        self.debugString.set("test")
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, rowspan=10, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NSEW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)
        # Frame to hold Non debug stuff
        appFrame = Tkinter.Frame(self, width=500)
        appFrame.grid(column=0, row=0, padx=x_right_padding, sticky="EW")
        appFrame.grid_columnconfigure(0, weight=1)
        appFrame.grid_rowconfigure(0, weight=1)
        # Instructions line
        instructionLine = Tkinter.Frame(appFrame)
        instructionLine.grid(column=0, row=0)
        self.headerText = "Enter the key and select the operation mode"
        headerSpace = Tkinter.Label(instructionLine, text=self.headerText,
                                    fg="black")
        headerSpace.grid(column=0, row=0, pady=y_bottom_padding, sticky="SEW")
        # Debug enable line
        debugLine = Tkinter.Frame(appFrame)
        debugLine.grid(column=0, row=1, sticky="W")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString)
        debugCheckBox.grid()
        # Mode check buttons
        buttonLine = Tkinter.Frame(appFrame)
        buttonLine.grid(column=0, row=2, pady=y_bottom_padding, sticky="EW")
        buttonLine.grid_columnconfigure(0, weight=1)
        buttonLine.grid_columnconfigure(1, weight=1)
        self.serverModeButton = Tkinter.Checkbutton(
            buttonLine,
            text=u"Sever Mode",
            onvalue=1,
            offvalue=0,
            variable=self.svrCheckBoxState,
            command=self.onServerClick)
        self.serverModeButton.grid(column=0, row=0, sticky="W")
        self.clientModeButton = Tkinter.Checkbutton(
            buttonLine,
            text=u"Client Mode",
            onvalue=1,
            offvalue=0,
            variable=self.clientCheckBoxState,
            command=self.onClientClick)
        self.clientModeButton.grid(column=1, row=0, sticky="W")
        # Line for entering key
        enterKeyLine = Tkinter.Frame(appFrame)
        enterKeyLine.grid(column=0, row=3, sticky="EW")
        enterKeyLine.grid_columnconfigure(0)
        enterKeyLine.grid_columnconfigure(1, weight=4)
        keyPrompt = Tkinter.Label(enterKeyLine, text=u"Key:")
        keyPrompt.grid(column=0, row=0, pady=y_bottom_padding,
                       padx=x_right_padding, sticky="W")
        self.keyEntry = Tkinter.Entry(enterKeyLine)
        self.keyEntry.grid(column=1, row=0, sticky="EW")
        # Line for connect button
        connectLine = Tkinter.Frame(appFrame)
        connectLine.grid(column=0, row=4, sticky="E")
        connectButton = Tkinter.Button(connectLine, text="Connect",
                                       command=lambda:
                                           self.onConnectClick(
                                               controller))
        connectButton.grid(column=0, row=0, sticky="EW")

    def onServerClick(self):
        """ Only allow one to be selected """
        print self.svrCheckBoxState.get()
        self.clientModeButton.deselect()

    def onClientClick(self):
        """ Only allow one to be selected """
        self.serverModeButton.deselect()

    def onConnectClick(self, controller):
        if self.svrCheckBoxState.get():
            controller.show_frame(svrConfigPage)
        elif self.clientCheckBoxState.get():
            controller.show_frame(clientConfigPage)

class svrConfigPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeSvrConfigPage(controller)

    def initializeSvrConfigPage(self, controller):
        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        self.debugString.set("test")
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, rowspan=10, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NSEW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)

        # Frame to hold Non debug stuff
        appFrame = Tkinter.Frame(self, width=500)
        appFrame.grid(column=0, row=0, padx=x_right_padding, sticky="EW")
        appFrame.grid_columnconfigure(0, weight=1)
        appFrame.grid_rowconfigure(0, weight=1)
        # Debug Button Line
        debugLine = Tkinter.Frame(appFrame)
        debugLine.grid(column=0, row=0, sticky="EW")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString)
        debugCheckBox.grid(sticky="W")
        # Enter port line
        portLine = Tkinter.Frame(appFrame)
        portLine.grid(column=0, row=1, sticky="EW")
        portLine.grid_columnconfigure(1, weight=1)
        portPrompt = Tkinter.Label(portLine, text="Port:")
        portPrompt.grid(column=0, row=0, padx=x_right_padding, sticky="W")
        portBox = Tkinter.Entry(portLine)
        portBox.grid(column=1, row=0, sticky="EW")
        # Connect/Cancel button line
        connectButtonLine = Tkinter.Frame(appFrame)
        connectButtonLine.grid(column=0, row=2, sticky="EW")
        connectButtonLine.grid_columnconfigure(0, weight=1)
        connectButton = \
            Tkinter.Button(connectButtonLine, text="Connect",
                           command=lambda: self.onConnectClick(controller))
        connectButton.grid(column=0, row=0, padx=x_right_padding, sticky="E")
        cancelButton = \
            Tkinter.Button(connectButtonLine, text="Cancel",
                           command=lambda: self.onCancelClick(controller))
        cancelButton.grid(column=1, row=0)

    def onConnectClick(self, controller):
        controller.show_frame(svrWaitPage)

    def onCancelClick(self, controller):
        controller.show_frame(startPage)


class svrWaitPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeSvrWaitPage(controller)

    def initializeSvrWaitPage(self, controller):
        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        self.debugString.set("test")
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, rowspan=10, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NSEW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)

        # Frame to hold Non debug stuff
        appFrame = Tkinter.Frame(self, width=500)
        appFrame.grid(column=0, row=0, padx=x_right_padding, sticky="EW")
        appFrame.grid_columnconfigure(0, weight=1)
        appFrame.grid_rowconfigure(0, weight=1)
        # Wait message line
        waitMessageFrame = Tkinter.Frame(appFrame)
        waitMessageFrame.grid(column=0, row=0, sticky="NSEW")
        waitMessage = Tkinter.Label(waitMessageFrame,
                                    text="Waiting for connection")
        waitMessage.grid(column=0, row=0, sticky="NW")
        # Cancel button line
        cancelButtonFrame = Tkinter.Frame(appFrame)
        cancelButtonFrame.grid(column=0, row=1, sticky="NEW")
        cancelButtonFrame.grid_columnconfigure(0, weight=1)
        cancelButton = \
            Tkinter.Button(cancelButtonFrame,
                           text="Cancel",
                           command=lambda: self.onCancelClick(controller))
        cancelButton.grid(column=0, row=0, sticky="E")

    def onCancelClick(self, controller):
        controller.show_frame(startPage)


class clientConfigPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeClientConfigPage(controller)

    def initializeClientConfigPage(self, controller):
        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        self.debugString.set("test")
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, rowspan=10, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NSEW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)

        # Frame to hold Non debug stuff
        appFrame = Tkinter.Frame(self, width=500)
        appFrame.grid(column=0, row=0, padx=x_right_padding, sticky="EW")
        appFrame.grid_columnconfigure(0, weight=1)
        appFrame.grid_rowconfigure(0, weight=1)
        # Instruction Line
        instructionFrame = Tkinter.Frame(appFrame)
        instructionFrame.grid(column=0, row=0, pady=y_bottom_padding,
                              sticky="EW")
        instructionFrame.grid_columnconfigure(0, weight=1)
        instructionLabel = Tkinter.Label(instructionFrame,
                                         text="Enter the server's IP and port")
        instructionLabel.grid(column=0, row=0, sticky="W")
        # IP/port line
        enterInfoFrame = Tkinter.Frame(appFrame)
        enterInfoFrame.grid(column=0, row=2, pady=y_bottom_padding,
                            sticky="EW")
        enterInfoFrame.grid_columnconfigure(0)
        enterInfoFrame.grid_columnconfigure(1, weight=1)
        ipLabel = Tkinter.Label(enterInfoFrame, text="IP:")
        ipLabel.grid(column=0, row=0,  padx=x_right_padding, sticky="W")
        ipEntryBox = Tkinter.Entry(enterInfoFrame)
        ipEntryBox.grid(column=1, row=0, sticky="EW")
        portLabel = Tkinter.Label(enterInfoFrame, text="Port:")
        portLabel.grid(column=0, row=1, padx=x_right_padding, sticky="W")
        portEntryBox = Tkinter.Entry(enterInfoFrame)
        portEntryBox.grid(column=1, row=1, sticky="EW")
        # Connect button and cancel button line
        buttonsFrame = Tkinter.Frame(appFrame)
        buttonsFrame.grid(column=0, row=3, sticky="EW")
        buttonsFrame.grid_columnconfigure(0, weight=1)
        connectButton = \
            Tkinter.Button(buttonsFrame, text="Connect",
                           command=lambda: self.onConnectClick(controller))
        connectButton.grid(column=0, row=0, padx=x_right_padding, sticky="E")

        cancelButton = \
            Tkinter.Button(buttonsFrame, text="Cancel",
                           command=lambda: self.onCancelClick(controller))
        cancelButton.grid(column=1, row=0)

    def onConnectClick(self, controller):
        controller.show_frame(messagingPage)

    def onCancelClick(self, controller):
        controller.show_frame(startPage)

class messagingPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeMessagingPage(controller)

    def initializeMessagingPage(self, controller):
        self.passedMessages = Tkinter.StringVar()

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        self.debugString.set("test")
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, rowspan=10, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NSEW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)

        # Frame to hold Non debug stuff
        appFrame = Tkinter.Frame(self, width=500)
        appFrame.grid(column=0, row=0, padx=x_right_padding, sticky="EW")
        appFrame.grid_columnconfigure(0, weight=1)
        appFrame.grid_rowconfigure(0, weight=1)
        # Messages and disconnect button  frame
        conversationFrame = Tkinter.Frame(appFrame)
        conversationFrame.grid(column=0, row=0, pady=y_bottom_padding,
                               sticky="NSEW")
        conversationFrame.grid_columnconfigure(0, weight=1,
                                               minsize=debugBoxWidth)
        conversationFrame.grid_rowconfigure(0, weight=1,
                                            minsize=debugBoxWidth)
        conversationHist = Tkinter.Message(conversationFrame,
                                           textvariable=self.passedMessages,
                                           anchor="w",
                                           bg="white",
                                           fg="black")
        conversationHist.grid(column=0, row=0, padx=x_right_padding,
                              sticky="NEWS")
        disconnectButton = \
            Tkinter.Button(conversationFrame,
                           text="Disconnect",
                           command=lambda: self.onDisconnectClick(controller))
        disconnectButton.grid(column=1, row=0, sticky="S")
        # Send and disconnect button frame
        buttonFrame = Tkinter.Frame(appFrame)
        buttonFrame.grid(column=0, row=1, sticky="EW")
        buttonFrame.grid_columnconfigure(0, weight=1)
        enterMessageBox = Tkinter.Entry(buttonFrame)
        enterMessageBox.grid(column=0, row=0, padx=x_right_padding,
                             sticky="EW")
        sendButton = Tkinter.Button(buttonFrame, text="Send")
        sendButton.grid(column=1, row=0)

    def onDisconnectClick(self, controller):
        controller.show_frame(startPage)

    def onSendClick(self):
        pass

if __name__ == "__main__":
    app = VPNWindow(None)
    app.title("Assignment 3 VPN")
    app.mainloop()