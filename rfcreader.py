#!/usr/bin/python

import wx
import controller
import ui
import dataconnector

class Application:
    def __init__(self, parent, title, size):
        self.dataConnector = dataconnector.DataConnector()
        self.uiView = ui.ApplicationUi(None, title, size)
        self.controller = controller.RFCViewController(self.uiView, self.dataConnector)

    def Show(self):
        self.uiView.Show()
        

app = wx.App()
title = "RfcReader"
size = (1000, 600)
frame = Application(None, title, size)
frame.Show()
app.MainLoop()
    
        
