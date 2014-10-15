__author__ = 'Frederick'
# VPN_gui.py
#
# Construct the whole gui here
# Frame code adapted from
# http://stackoverflow.com/questions/7546050/python-tkinter-changing-the-window-basics
#
# October 10, 2014

import Tkinter
import tkMessageBox
from SecureVpn import *
import threading
from SessionKeyNegotiator import *
import datetime
from SecureVpnCrypter import *

y_bottom_padding = (0, 10)
x_right_padding = (0, 5)
debugBoxWidth = 500
enableDebugString = "Enable debug"
wrapTextLength = 250
minButtonSize = 70

class VPNWindow(Tkinter.Tk):
    # Constructor
    def __init__(self, parent):
        Tkinter.Tk.__init__(self, parent)
        self.parent = parent
        self.initializeFrameContainer()

        self.vpn_client = None
        self.initial_key = None

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
        for F in (startPage, svnConfigPage, svnWaitPage, clientConfigPage,
                  messagingPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="NSEW")

        self.show_frame(startPage)

    def show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()


    def set_key(self, key):
        self.initial_key = key

    def get_key(self):
        return self.initial_key

    def set_vpn(self, vpn):
        self.vpn_client = vpn

    def send_vpn_message(self, message):
        self.vpn_client.send_message(message)

    def log_message(self, message):
        pass

    def log_debug(self, debug):
        pass


class startPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeStartPage(controller)

    def initializeStartPage(self, controller):
        self.svrCheckBoxState = Tkinter.IntVar()
        self.clientCheckBoxState = Tkinter.IntVar()
        self.ipAddress = Tkinter.StringVar()

        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth, weight=1)
        debugFrame.grid_rowconfigure(0, weight=1)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)
        # Debug enable line
        debugLine = Tkinter.Frame(debugFrame)
        debugLine.grid(column=0, row=1, sticky="SW")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString)
        debugCheckBox.grid()
        # Step button
        stepButtonFrame = Tkinter.Frame(debugFrame)
        stepButtonFrame.grid(column=1, row=1, sticky="SE")
        stepButtonFrame.grid_columnconfigure(0, minsize=minButtonSize)
        stepButton = Tkinter.Button(stepButtonFrame, text="Step")
        stepButton.grid(sticky="EW")

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
        self.keyEntry = Tkinter.Entry(enterKeyLine, textvariable=self.ipAddress)
        self.keyEntry.config(show="*")
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
        self.clientModeButton.deselect()
        self.setKeyEntryFocus()

    def onClientClick(self):
        """ Only allow one to be selected """
        self.serverModeButton.deselect()
        self.setKeyEntryFocus()

    def onConnectClick(self, controller):
        if self.keyEntry.get() is "":
            tkMessageBox.showwarning("Missing inputs",
                                     "Shared key is missing")
            return
        controller.set_key(self.keyEntry.get())
        # Delete key
        self.keyEntry.delete(0, Tkinter.END)
        if self.svrCheckBoxState.get():
            controller.title("Assignment 3 VPN - SERVER")
            controller.show_frame(svnConfigPage)
        elif self.clientCheckBoxState.get():
            controller.title("Assignment 3 VPN - CLIENT")
            controller.show_frame(clientConfigPage)
        else:
            tkMessageBox.showwarning("Missing inputs",
                                     "Operation mode not selected")

    def setKeyEntryFocus(self):
        self.keyEntry.focus_set()
        self.keyEntry.selection_range(0, Tkinter.END)

class svnConfigPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeSvrConfigPage(controller)

    def initializeSvrConfigPage(self, controller):
        self.svrPortNumber = Tkinter.StringVar()

        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Debug side panel
        self.debugString = Tkinter.StringVar()
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth, weight=1)
        debugFrame.grid_rowconfigure(0, weight=1)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)
        # Debug enable line
        debugLine = Tkinter.Frame(debugFrame)
        debugLine.grid(column=0, row=1, sticky="SW")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString)
        debugCheckBox.grid()
        # Step button
        stepButtonFrame = Tkinter.Frame(debugFrame)
        stepButtonFrame.grid(column=1, row=1, sticky="SE")
        stepButtonFrame.grid_columnconfigure(0, minsize=minButtonSize)
        stepButton = Tkinter.Button(stepButtonFrame, text="Step")
        stepButton.grid(sticky="EW")

        # Frame to hold Non debug stuff
        appFrame = Tkinter.Frame(self, width=500)
        appFrame.grid(column=0, row=0, padx=x_right_padding, sticky="EW")
        appFrame.grid_columnconfigure(0, weight=1)
        appFrame.grid_rowconfigure(0, weight=1)
        # Enter port line
        portLine = Tkinter.Frame(appFrame)
        portLine.grid(column=0, row=1, sticky="EW")
        portLine.grid_columnconfigure(1, weight=1)
        portPrompt = Tkinter.Label(portLine, text="Port:")
        portPrompt.grid(column=0, row=0, padx=x_right_padding, sticky="W")
        self.portBox = Tkinter.Entry(portLine, textvariable=self.svrPortNumber)
        self.portBox.grid(column=1, row=0, sticky="EW")
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
        if self.svrPortNumber.get() is "":
            tkMessageBox.showwarning("Missing inputs",
                                     "Server port number not found")
        else:
            encrypter = SecureVpnCrypter()
            negotiator = SessionKeyNegotiator("SERVER")
            server = SecureVpnServer('', int(self.portBox.get()), encrypter, negotiator)
            server.set_shared_secret(controller.get_key())
            controller.set_key("")
            controller.set_vpn(server)
            loop_thread = threading.Thread(target= asyncore.loop, name="Asyncore Loop")
            loop_thread.start()
            controller.frames[messagingPage].init_loggers(controller)
            controller.frames[svnWaitPage].checkForClient(controller)
            controller.show_frame(svnWaitPage)

    def onCancelClick(self, controller):
        controller.show_frame(startPage)


class svnWaitPage(Tkinter.Frame):
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
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth, weight=1)
        debugFrame.grid_rowconfigure(0, weight=1)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)
        # Debug enable line
        debugLine = Tkinter.Frame(debugFrame)
        debugLine.grid(column=0, row=1, sticky="SW")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString)
        debugCheckBox.grid()
        # Step button
        stepButtonFrame = Tkinter.Frame(debugFrame)
        stepButtonFrame.grid(column=1, row=1, sticky="SE")
        stepButtonFrame.grid_columnconfigure(0, minsize=minButtonSize)
        stepButton = Tkinter.Button(stepButtonFrame, text="Step")
        stepButton.grid(sticky="EW")

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

    def checkForClient(self, controller):
        if controller.vpn_client.is_client_connected():
            controller.show_frame(messagingPage)
        else:
            self.after(0, lambda: self.checkForClient(controller))

class clientConfigPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeClientConfigPage(controller)

    def initializeClientConfigPage(self, controller):
        self.grid(sticky="NSEW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        ## Debug side panel
        self.debugString = Tkinter.StringVar()
        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth, weight=1)
        debugFrame.grid_rowconfigure(0, weight=1)
        debugMessageBox = Tkinter.Message(debugFrame,
                                          textvariable=self.debugString,
                                          anchor="w",
                                          bg="black",
                                          fg="white")
        debugMessageBox.grid(column=0, row=0, sticky="NW")
        debugMessageBox.grid_propagate(0)
        debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)
        # Debug enable line
        debugLine = Tkinter.Frame(debugFrame)
        debugLine.grid(column=0, row=1, sticky="SW")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString)
        debugCheckBox.grid()
        # Step button
        stepButtonFrame = Tkinter.Frame(debugFrame)
        stepButtonFrame.grid(column=1, row=1, sticky="SE")
        stepButtonFrame.grid_columnconfigure(0, minsize=minButtonSize)
        stepButton = Tkinter.Button(stepButtonFrame, text="Step")
        stepButton.grid(sticky="EW")

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
        self.ipEntryBox = Tkinter.Entry(enterInfoFrame)
        self.ipEntryBox.grid(column=1, row=0, sticky="EW")
        portLabel = Tkinter.Label(enterInfoFrame, text="Port:")
        portLabel.grid(column=0, row=1, padx=x_right_padding, sticky="W")
        self.portEntryBox = Tkinter.Entry(enterInfoFrame)
        self.portEntryBox.grid(column=1, row=1, sticky="EW")
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
        encrypter = SecureVpnCrypter()
        negotiator = SessionKeyNegotiator("CLIENT")
        client = SecureVpnClient(encrypter, negotiator, self.ipEntryBox.get(), int(self.portEntryBox.get()))
        client.set_shared_secret(controller.get_key())
        controller.set_key("")
        controller.set_vpn(client)
        loop_thread = threading.Thread(target= asyncore.loop, name="Asyncore Loop")
        loop_thread.start()
        controller.frames[messagingPage].init_loggers(controller)
        controller.show_frame(messagingPage)

    def onCancelClick(self, controller):
        controller.show_frame(startPage)

class messagingPage(Tkinter.Frame):
    def __init__(self, parent, controller):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initializeMessagingPage(controller)

    def initializeMessagingPage(self, controller):

        debugFrame = Tkinter.Frame(self, bg="black")
        debugFrame.grid(column=1, row=0, sticky="NSEW")
        debugFrame.grid_columnconfigure(0, minsize=debugBoxWidth, weight=1)
        debugFrame.grid_rowconfigure(0, weight=1)

        #scrollbar_debug = Tkinter.Scrollbar(debugFrame)
        #scrollbar_debug.grid(column=0, row=0, sticky="E")
        self.debugMessageBox = Tkinter.Text(debugFrame, wrap=Tkinter.WORD,
                                           bg="black",
                                           fg="white",
                                           #yscrollcommand=scrollbar_debug.set,
                                           state=Tkinter.DISABLED)

        self.debugMessageBox.grid(column=0, row=0, sticky="NW")
        self.debugMessageBox.grid_propagate(0)
        self.debugMessageBox.grid_columnconfigure(0, minsize=debugBoxWidth)

        #scrollbar_debug.config(command=self.debugMessageBox.yview)

        # Debug enable line
        debugLine = Tkinter.Frame(debugFrame)
        debugLine.grid(column=0, row=1, sticky="SW")
        debugCheckBox = Tkinter.Checkbutton(debugLine, text=enableDebugString, command= lambda: self.toggle_debug(controller))
        debugCheckBox.grid()
        # Step button
        stepButtonFrame = Tkinter.Frame(debugLine)
        stepButtonFrame.grid(column=1, row=1, sticky="EW")
        stepButtonFrame.grid_columnconfigure(0, minsize=minButtonSize)
        stepButton = Tkinter.Button(stepButtonFrame, text="Step", command=lambda: self.step_debug(controller))
        stepButton.grid(sticky="E")

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

        #scrollbar_message = Tkinter.Scrollbar(conversationFrame)
        #scrollbar_message.grid(column=0, row=0, sticky="E")
        self.conversationHist = Tkinter.Text(conversationFrame, wrap=Tkinter.WORD,
                                           bg="white",
                                           fg="black",
                                           #yscrollcommand=scrollbar_message.set,
                                           state=Tkinter.DISABLED)
        self.conversationHist.grid(column=0, row=0, padx=x_right_padding,
                              sticky="NEWS")
        #scrollbar_message.config(command=self.conversationHist.yview)

        disconnectButton = \
            Tkinter.Button(conversationFrame,
                           text="Disconnect",
                           command=lambda: self.onDisconnectClick(controller))
        disconnectButton.grid(column=1, row=0, sticky="S")
        # Send button and message box frame
        buttonFrame = Tkinter.Frame(appFrame)
        buttonFrame.grid(column=0, row=1, sticky="EW")
        buttonFrame.grid_columnconfigure(0, weight=1)
        self.enterMessageBox = Tkinter.Entry(buttonFrame)
        self.enterMessageBox.grid(column=0, row=0, padx=x_right_padding,
                             sticky="EW")
        sendButton = Tkinter.Button(buttonFrame, text="Send", command=lambda: self.onSendClick(controller))
        sendButton.grid(column=1, row=0, sticky="EW")
        buttonFrame.grid_columnconfigure(1, minsize=minButtonSize)

    def onDisconnectClick(self, controller):
        controller.show_frame(startPage)

    def onSendClick(self, controller):
        threading.Thread(target= lambda: controller.send_vpn_message(self.enterMessageBox.get()), name="UI Loop").start()
        self.enterMessageBox.delete(0, len(self.enterMessageBox.get()))

    def log(self, message):
        self.conversationHist.config(state=Tkinter.NORMAL)
        self.conversationHist.insert("@0,0", message + "\n\n")
        self.conversationHist.insert("@0,0", "Received: " + str(datetime.datetime.now()) + "\n")
        self.conversationHist.config(state=Tkinter.DISABLED)

    def debug(self, message):
        self.debugMessageBox.config(state=Tkinter.NORMAL)
        self.debugMessageBox.insert("@0,0", message + "\n\n")
        self.debugMessageBox.insert("@0,0", "Received: " + str(datetime.datetime.now()) + "\n")
        self.debugMessageBox.config(state=Tkinter.DISABLED)

    def init_loggers(self, controller):
        controller.vpn_client.set_logger(lambda message: self.log(message))
        controller.vpn_client.set_debugger(lambda message: self.debug(message))

    def toggle_debug(self, controller):
        controller.vpn_client.toggle_step_through_mode()

    def step_debug(self, controller):
        controller.vpn_client.continue_progress()

if __name__ == "__main__":
    app = VPNWindow(None)
    app.title("Assignment 3 VPN")

    loop_thread = threading.Thread(target= app.mainloop, name="UI Loop")
    loop_thread.start()