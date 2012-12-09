#!/usr/bin/python
import wx
import wx.lib.agw.flatnotebook as fnb

# Utilities UIs
class UserSelectionDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, title = title)
        
        
        textLabel = wx.StaticText(self, -1, "rfc no.:")
        self.textCtrl = wx.TextCtrl(self, -1, "")

        btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        #self.okButton = wx.Button(self, wx.ID_OK)
        #self.cancelButton = wx.Button(self, wx.ID_CANCEL);
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(textLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.textCtrl, 0, wx.ALL | wx.EXPAND, 5)
        #sizer.Add(okButton, 0, 0, 5)
        #sizer.Add(cancelButton, 0, 0, 5)
        sizer.Add(btns, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self.OnOKButtonPressed, id = wx.ID_OK)
        self.SetSizerAndFit(sizer)

    def OnOKButtonPressed(self, event):
        if event.GetId() == wx.ID_OK:
            try:
                number = int(self.textCtrl.GetValue())
                self.EndModal(event.GetId())
            except ValueError:
                dlg = wx.MessageDialog(
                    parent=self,
                    message='Please enter a valid integer',
                    caption='Error',
                    style=wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP,
                    pos=(200,200)
                )
                dlg.ShowModal()
                dlg.Destroy()
        elif event.GetId() == wx.ID_CANCEL:
            self.EndModal(event.GetId())
    def GetSelection(self):
        try:
            number = int(self.textCtrl.GetValue())
        except ValueError:

            number = -1
        return {"no":number}

# Basic UIs
class PanelView:
    def __init__(self):
        self._controller = None
    def AddListener(self, controller):
        self._controller = controller

# concrete UI

class LeftPanelView(PanelView, wx.Panel):
    """ Left Panel View """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        PanelView.__init__(self)

        self._fnb = fnb.FlatNotebook(self, -1, agwStyle= fnb.FNB_NO_TAB_FOCUS
                                                        | fnb.FNB_HIDE_ON_SINGLE_TAB)
        self._custonmPage = wx.NotebookPage(self._fnb, -1)
        bsizer = wx.BoxSizer()
        bsizer.Add(self._fnb, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(bsizer)

    def AddPage(self, pageName):
        page = wx.NotebookPage(self._fnb, -1)
        self._fnb.AddPage(page, pageName, select=True)
        return page

    def ClearUp(self):
        self._fnb.DeleteAllPages()

    def SetPageText(self, page, pageName):
        self._fnb.SetPageText(page, pageName)

    def OnSelectSection(self, evt):
        item = evt.GetItem()
        self._controller.OnSelectSectionPressed(item)

    def UpdateUi(self, page):
        self._fnb.SetCustomPage(None)


class RightPanelView(PanelView, wx.Panel):
    """ Right Panel View """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        PanelView.__init__(self)
        
        self._fnb = fnb.FlatNotebook(self, -1, agwStyle= fnb.FNB_NO_TAB_FOCUS
                                                        | fnb.FNB_NAV_BUTTONS_WHEN_NEEDED
                                                        | fnb.FNB_NO_X_BUTTON
                                                        | fnb.FNB_X_ON_TAB)
        self._custonmPage = wx.NotebookPage(self._fnb, -1)        
        bsizer = wx.BoxSizer()
        bsizer.Add(self._fnb, 1, wx.EXPAND | wx.ALL)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.SetSizer(bsizer)

    def AddPage(self, pageName):
        page = wx.NotebookPage(self._fnb, -1)
        self._fnb.AddPage(page, pageName, select=True)        
        return page

    def RemovePage(self, page):
        pos = self._fnb.GetPageIndex(page)
        self._fnb.DeletePage(pos)

    def ShowPage(self, page):
        self._fnb.SetSelection(page)

    def SetPageText(self, page, pageName):
        self._fnb.SetPageText(page, pageName)
        self._fnb.SetCustomPage(None)

    def UpdateUi(self, page):
        self._fnb.SetCustomPage(None)

    def ClearUp(self):
        self._fnb.DeleteAllPages()

    # UI event handlers

    def OnAddPage(self, event):
        self._controller.OnAddPage(event)

    def OnSaveCurrentPage(self, event):
        page = self._fnb.GetSelection()
        print page
        pageText = self._fnb.GetPageText(page)
        print "On save current page" + pageText
        self._controller.OnSaveCurrentPage(pageText)

    def OnLoadPage(self, event):
        self._controller.OnLoadPage(event)

    def OnPageClosing(self, event):
        print "Page closing", self._fnb.GetPageText(event.GetSelection())
        self._controller.OnPageClosingCallback(self._fnb.GetPageText(event.GetSelection()))

    def OnPageClosed(self, event):
        nextPageText = self._fnb.GetPageText(event.GetSelection())
        print "Page closed", nextPageText
        if self._fnb.GetPageCount() == 0:
            self._fnb.SetCustomPage(self._custonmPage)
            nextPageText = "-1"
        self._controller.OnPageClosedCallback(nextPageText)

    def OnPageChanged(self, event):
        currentPageText = self._fnb.GetPageText(event.GetSelection())  
        print "Page changed", currentPageText
        self._controller.OnPageChangedCallback(currentPageText)


class ApplicationUi(wx.Frame):
    def __init__(self, parent, title, size):
        wx.Frame.__init__(self, parent, -1, title, size=size)
        
        # Init temp variables
        
        splitter = wx.SplitterWindow(self)

        # Init self-defined members
        
        self.rightPanel = RightPanelView(splitter)
        self.leftPanel = LeftPanelView(splitter)

        splitter.SplitVertically(self.leftPanel, self.rightPanel)
        splitter.SetMinimumPaneSize(100)
        
        self.SetBackgroundColour("white")
        self.menuBar = wx.MenuBar()
        self.menu = wx.Menu()
        
        self.addPageMenuButton = self.menu.Append(wx.ID_ADD, "Add Page", "Add a tab page")
        
        self.saveCurrentPageMenuButton = self.menu.Append(wx.ID_ANY, "Save Current Page", "Save current page")
        
        #self.loadPageMenuButton = self.menu.Append(wx.ID_ANY, "Load Page", "Load a page")
        

        self.menuBar.Append(self.menu, "&File")
        self.SetMenuBar(self.menuBar)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def AddListener(self, controller):
        """ Bind listener and events """
        # Bind listeners
        self._controller = controller
        self.rightPanel.AddListener(controller.GetRightViewController())
        self.leftPanel.AddListener(controller.GetLeftViewController())
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.rightPanel.OnAddPage, self.addPageMenuButton)
        self.Bind(wx.EVT_MENU, self.rightPanel.OnSaveCurrentPage, self.saveCurrentPageMenuButton)
        #self.Bind(wx.EVT_MENU, self.rightPanel.OnLoadPage, self.loadPageMenuButton)
