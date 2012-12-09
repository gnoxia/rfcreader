#!/usr/bin/python
import ui
import wx.richtext as rt
import wx
import htmlparser as rrhp
import htmlrichtextdisplayer as rrhrtd
from StringIO import StringIO
#from dataconnector import DataConnector

class ViewController:
    """ Basic view controller. """
    def __init__(self, uiView, dataConnector):
        self._targetUiView = uiView
        self._dataConnector = dataConnector


class LeftViewController(ViewController):
    """ For left view panel controlling, including catalog and notes. """
    def __init__(self, parent, uiView, dataConnector):
        ViewController.__init__(self, uiView=uiView, dataConnector=dataConnector)
        self._currentPageId = -1
        self._parent = parent
        self._treelist = None
        self._currentPage = None

    def _InitTreeList(self, parent, rootTitle, doctree):
        self._doctree = doctree      
        self._currentId = 0
        if self._treelist == None:
            self._treelist = wx.TreeCtrl(parent)
            self._targetUiView.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._targetUiView.OnSelectSection, self._treelist)
            self._root = self._treelist.AddRoot("rfc" + rootTitle)            
            bsizer = wx.BoxSizer()
            bsizer.Add(self._treelist, 1, wx.EXPAND)
            parent.SetSizerAndFit(bsizer)
        else:
            self._treelist.DeleteAllItems()
            self._root = self._treelist.AddRoot("rfc" + rootTitle)
        return self._root

    def _AddNodes(self, parentItem, parentId): 
        if parentItem is self._root:
            currentItem = self._treelist.AppendItem(parentItem, self._doctree[self._currentId].values()[0][1])
            self._treelist.SetItemPyData(currentItem, self._doctree[self._currentId].values()[0])
            self._currentId += 1
            if self._currentId >= len(self._doctree):
                return 0
        else:
            if self._doctree[parentId].keys()[0][1] < self._doctree[self._currentId].keys()[0][1]:
                currentItem = self._treelist.AppendItem(parentItem, self._doctree[self._currentId].values()[0][1])
                self._treelist.SetItemPyData(currentItem, self._doctree[self._currentId].values()[0])
                self._currentId += 1
                if self._currentId >= len(self._doctree):
                    return 0
            elif self._doctree[parentId].keys()[0][1] == self._doctree[self._currentId].keys()[0][1]:
                return 1
            else:
                return 2
        result =  self._AddNodes(currentItem, self._currentId - 1)
        if result == 0:
            return 0
        else:
            return self._AddNodes(parentItem, parentId)

    def _AddPage(self, event):
        if self._currentPage == None:
            self._currentPage = self._targetUiView.AddPage(event)
        else:
            self._targetUiView.SetPageText(self._currentPage, event)  
        return self._currentPage

    def OnUpdate(self, type, event):
        if type == "pageAdded" or type == "pageChanged" :   
            if event == "pageAllClosed":
                self._currentPage = None
                self._treelist = None
                self._currentId = 0
                self._targetUiView.ClearUp()
            else:         
                displayer = event["displayer"]
                pageId = str(event["pageId"])
                page = self._AddPage("rfc" + pageId)
                doctree = displayer.docEntryList
                root = self._InitTreeList(page, pageId, doctree)
                self._AddNodes(root, self._currentId)
                self._treelist.ExpandAll()
                self._targetUiView.UpdateUi(page)

    def OnSelectSectionPressed(self, item):
        listdata = self._treelist.GetPyData(item)
        print(listdata)
        self._parent.NotifyPagePositionChanged(self, listdata[0])
            


class RigthViewController(ViewController):
    """ For controlling rich text displaying. """
    def __init__(self, parent, uiView, dataConnector):
        ViewController.__init__(self, uiView=uiView, dataConnector=dataConnector)
        self._pageStore = {}
        self._parent = parent
        self._currentPageId = None

    # Button Actions
    def OnAddPage(self, event):
        userSelection = {"no":-1}
        selectionDialog = ui.UserSelectionDialog(None, "new page configuration")
        if selectionDialog.ShowModal() == wx.ID_OK:
            userSelection = selectionDialog.GetSelection()
        print userSelection
        selectionDialog.Destroy()

        if userSelection["no"] <= -1:
            return
        elif userSelection["no"] >= 0:
            # read rfc from network currently.
            if str(userSelection["no"]) in self._pageStore :
                value = self._pageStore[str(userSelection["no"])]
                page = value["page"]
                self._targetUiView.ShowPage(page)
                return
            else:
                print "Page<",str(userSelection["no"]),"> Begin to add..."
                
                page = self._targetUiView.AddPage(str(userSelection["no"]))

                try:
                    rich = rt.RichTextCtrl(page, wx.ID_ANY)
                    rich.SetEditable(False)
                    displayer = rrhrtd.HTMLRichTextDisplayer(rich)
                    parser = rrhp.HTMLParser(displayer)
                    print "Read data"
                
                    data = self._dataConnector.Read(str(userSelection["no"]))
                    #print "Parse data"
                    parser.feed(data.decode())

                    bsizer = wx.BoxSizer()
                    bsizer.Add(rich, 1, wx.EXPAND | wx.ALL)
                    page.SetSizerAndFit(bsizer)

                    self._targetUiView.UpdateUi(page)
                except Exception:
                    self._targetUiView.RemovePage(page)
                    return
                print "Add to store"
                self._pageStore[str(userSelection["no"])] = {"page":page, "displayer":displayer, "data":data}
                #print self._pageStore
                self._parent.NotifyPageAdded(self, {"pageId":userSelection["no"], "displayer":displayer})
                self._currentPageId = userSelection["no"]
        else:
            return

    def OnSaveCurrentPage(self, event):
        if event in self._pageStore:
            value = self._pageStore[event]
            data = value["data"]
            self._dataConnector.SaveToFile(event, data)
        else:
            print "Save current page error: " + event + " doesn't exist."

    def LoadPage(self, event):
        pass

    # UI Callback Actions
    def OnPageClosingCallback(self, event):
        del self._pageStore[event]
        print self._pageStore

    def OnPageClosedCallback(self, event):
        if event == "-1":
            self._parent.NotifyPageChanged(self, "pageAllClosed")
            self._targetUiView.ClearUp()

    def OnPageChangedCallback(self, event):
        """ Notify Main controller of Page changed """
        self._currentPageId = int(event)
        try:      
            #print "Page store:"      
            valueDict = self._pageStore[event]
            #print valueDict
            displayer = valueDict["displayer"]
            self._parent.NotifyPageChanged(self, {"pageId":int(event), "displayer":displayer})
        except KeyError:
            return
        else:
            return

    def OnPagePositionChanged(self, event):
        try:
            print(event)
            valueDict = self._pageStore[str(self._currentPageId)]
            print valueDict
            displayer = valueDict["displayer"]
            displayer.SetPosition(event)
        except KeyError:
            print "Key Error"
            return
        else:
            return

class BarController():
	""" Bar controller for controlling bar content. """
	def __init__(self, parent):
		pass


class RFCViewController():
    """ Main controller for all views and data connector. """
    def __init__(self, uiView, dataConnector):
        self._rvController = RigthViewController(self, uiView.rightPanel, dataConnector)
        self._lvController = LeftViewController(self, uiView.leftPanel, dataConnector)
        self._barController = BarController(self)
        self._uiView = uiView
        self._dataConnector = dataConnector
        # Bind listeners to their views
        self._uiView.AddListener(self)

    def NotifyPageChanged(self, source, event):
        if source == self._rvController:
            self._lvController.OnUpdate("pageChanged", event)

    def NotifyPageAdded(self, source, event):
        print "Notify Page Added"
        if source == self._rvController:
            print source, event
            self._lvController.OnUpdate("pageAdded", event)

    def NotifyPagePositionChanged(self, source, event):
        if source == self._lvController:
            self._rvController.OnPagePositionChanged(event)

    def GetRightViewController(self):
        return self._rvController
    def GetLeftViewController(self):
        return self._lvController
    def GetBarController(self):
        return self._barController


