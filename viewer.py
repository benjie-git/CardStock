#!/usr/bin/python3

# viewer.py
"""
This is the root of the CardStock stack viewer application.
It allows running and using a stack, and even saving its updated state,
if the stack has its canSave flag set to True.
"""

import os
import sys
import json
import wx
import wx.html
from stackManager import StackManager
from stackModel import StackModel
from uiCard import CardModel
import version
from runner import Runner
import helpDialogs
from findEngineViewer import FindEngine
from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.abspath(__file__))

ID_MENU_FIND = wx.NewIdRef()
ID_MENU_FIND_SEL = wx.NewIdRef()
ID_MENU_FIND_NEXT = wx.NewIdRef()
ID_MENU_FIND_PREV = wx.NewIdRef()
ID_MENU_REPLACE = wx.NewIdRef()

# ----------------------------------------------------------------------


class ViewerFrame(wx.Frame):
    """
    A stackFrame contains a stackWindow and a ControlPanel and manages
    their layout with a wx.BoxSizer.  A menu and associated event handlers
    provides for saving a stackManager to a file, etc.
    """
    title = "CardStock"

    def __init__(self, parent, stackModel, filename):
        if stackModel.GetProperty("canResize"):
            style = wx.DEFAULT_FRAME_STYLE
        else:
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

        wx.Frame.__init__(self, parent, -1, self.title, size=(500,500), style=style)
        # self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/stack.ico')))

        self.CreateStatusBar()

        self.stackManager = StackManager(self)
        self.stackManager.SetEditing(False)
        self.designer = None
        self.stackManager.filename = filename
        self.SetStackModel(stackModel)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnClose)

        self.findDlg = None
        self.findEngine = FindEngine(self.stackManager)

    def OnResize(self, event):
        self.stackManager.view.SetSize(self.GetClientSize())
        event.Skip()

    def SaveFile(self):
        if self.designer:
            self.designer.OnViewerSave(self.stackManager.stackModel)

        if self.stackManager.filename:
            data = self.stackManager.stackModel.GetData()
            try:
                jsonData = json.dumps(data, indent=2)
                with open(self.stackManager.filename, 'w') as f:
                    f.write(jsonData)
                self.stackManager.stackModel.SetDirty(False)
            except TypeError:
                # e = sys.exc_info()
                # print(e)
                wx.MessageDialog(None, str("Couldn't save file"), "", wx.OK).ShowModal()

    def SetStackModel(self, stackModel):
        self.stackManager.SetStackModel(stackModel)
        self.stackManager.SetEditing(False)
        self.SetClientSize(self.stackManager.stackModel.GetProperty("size"))
        self.stackManager.view.SetFocus()
        if self.stackManager.filename:
            self.SetTitle(self.title + ' -- ' + os.path.basename(self.stackManager.filename))

    def MakeMenu(self):
        # create the file menu
        fileMenu = wx.Menu()
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("canSave"):
            fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save Stack")
        fileMenu.Append(wx.ID_CLOSE, "&Close\tCtrl-W", "Close Stack")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")
        editMenu.AppendSeparator()
        editMenu.Append(ID_MENU_FIND, "&Find...\tCtrl-F", "Find... in stack")
        editMenu.Append(ID_MENU_FIND_SEL, "&Find Selection\tCtrl-E", "Find Selection")
        editMenu.Append(ID_MENU_FIND_NEXT, "&Find Next\tCtrl-G", "Find Next in stack")
        editMenu.Append(ID_MENU_FIND_PREV, "&Find Previous\tCtrl-Shift-G", "Find Previous in stack")
        editMenu.Append(ID_MENU_REPLACE, "&Replace...\tCtrl-Shift-R", "Replace in stack")

        # and the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "&About\tCtrl-H", "Display the gratuitous 'about this app' thingamajig")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,   self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU,   self.OnMenuClose, id=wx.ID_CLOSE)

        self.Bind(wx.EVT_MENU,  self.OnMenuAbout, id=wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU,  self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU,  self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU,  self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU,  self.OnPaste, id=wx.ID_PASTE)

        self.Bind(wx.EVT_MENU, self.OnMenuFind, id=ID_MENU_FIND)
        self.Bind(wx.EVT_MENU, self.OnMenuFindSel, id=ID_MENU_FIND_SEL)
        self.Bind(wx.EVT_MENU, self.OnMenuFindNext, id=ID_MENU_FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.OnMenuFindPrevious, id=ID_MENU_FIND_PREV)
        self.Bind(wx.EVT_MENU, self.OnMenuReplace, id=ID_MENU_REPLACE)

    def OnMenuSave(self, event):
        self.SaveFile()

    def OnMenuClose(self, event):
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("canSave") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Quitting?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.SaveFile()
        self.Close()

    def OnClose(self, event):
        self.stackManager.runner.CleanupFromRun()
        event.Skip()

    def OnCut(self, event):
        f = self.FindFocus()
        if f and hasattr(f, "Cut"):
            f.Cut()

    def OnCopy(self, event):
        f = self.FindFocus()
        if f and hasattr(f, "Copy"):
            f.Copy()

    def OnPaste(self, event):
        f = self.FindFocus()
        if f and hasattr(f, "Paste"):
            f.Paste()

    def OnUndo(self, event):
        f = self.FindFocus()
        if f and hasattr(f, "Undo"):
            if not hasattr(f, "CanUndo") or f.CanUndo():
                f.Undo()
                return
        event.Skip()

    def OnRedo(self, event):
        f = self.FindFocus()
        if f and hasattr(f, "Redo"):
            if not hasattr(f, "CanRedo") or f.CanRedo():
                f.Redo()
                return
        event.Skip()

    def ShowFindDialog(self, isReplace):
        if self.findDlg:
            self.findDlg.Close(True)
        self.findDlg = wx.FindReplaceDialog(self, self.findEngine.findData,
                                            'Replace' if isReplace else 'Find', style=int(isReplace))
        self.findDlg.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)
        self.findDlg.Bind(wx.EVT_FIND, self.OnFindEvent)
        self.findDlg.Bind(wx.EVT_FIND_NEXT, self.OnFindEvent)
        self.findDlg.Bind(wx.EVT_FIND_REPLACE, self.OnReplaceEvent)
        self.findDlg.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAllEvent)
        self.findDlg.Bind(wx.EVT_CLOSE, self.OnFindClose)
        self.findDlg.Show()

    def OnMenuFind(self, event):
        self.ShowFindDialog(False)

    def OnMenuReplace(self, event):
        self.ShowFindDialog(True)

    def OnFindClose(self, event):
        self.findDlg.Destroy()
        self.findDlg = None

    def OnMenuFindSel(self, event):
        self.findEngine.UpdateFindTextFromSelection()

    def OnMenuFindNext(self, event):
        flags = self.findEngine.findData.GetFlags()
        self.findEngine.findData.SetFlags(flags | 1)
        self.findEngine.Find()
        self.findEngine.findData.SetFlags(flags)

    def OnMenuFindPrevious(self, event):
        flags = self.findEngine.findData.GetFlags()
        self.findEngine.findData.SetFlags(flags & ~1)
        self.findEngine.Find()
        self.findEngine.findData.SetFlags(flags)

    def OnFindEvent(self, event):
        self.findEngine.Find()

    def OnReplaceEvent(self, event):
        self.findEngine.Replace()

    def OnReplaceAllEvent(self, event):
        self.findEngine.ReplaceAll()

    def OnMenuAbout(self, event):
        dlg = helpDialogs.CardStockAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def RunViewer(self):
        runner = Runner(self.stackManager, self.GetStatusBar())
        self.stackManager.runner = runner
        self.stackManager.SetEditing(False)
        self.SetClientSize(self.stackManager.stackModel.GetProperty("size"))
        self.MakeMenu()

        self.stackManager.LoadCardAtIndex(None)

        def RunAllSetupHandlers(model):
            if model.type == "card":
                runner.SetupForCard(model)
            if model.GetHandler("OnSetup"):
                runner.RunHandler(model, "OnSetup", None)
            for m in model.childModels:
                RunAllSetupHandlers(m)
        RunAllSetupHandlers(self.stackManager.stackModel)

        self.stackManager.LoadCardAtIndex(0)


# ----------------------------------------------------------------------

class ViewerApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init(self)  # for InspectionMixin

        self.SetAppDisplayName('CardStock')
        self.frame = None

        return True

    def OpenFile(self, filename):
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                if data:
                    stackModel = StackModel(None)
                    stackModel.SetData(data)
                    self.frame = ViewerFrame(None, stackModel, filename)
                    self.SetTopWindow(self.frame)
                    self.frame.stackManager.filename = filename
                    self.frame.Show(True)
            except TypeError:
                # e = sys.exc_info()
                # print(e)
                wx.MessageDialog(None, str("Couldn't read file"), "", wx.OK).ShowModal()

    def MacReopenApp(self):
        """
        Restore the main frame (if it's minimized) when the Dock icon is
        clicked on OSX.
        """
        top = self.GetTopWindow()
        if top and top.IsIconized():
            top.Iconize(False)
        if top:
            top.Raise()


# ----------------------------------------------------------------------


if __name__ == '__main__':
    app = ViewerApp(redirect=False)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        app.OpenFile(filename)
    else:
        print("Usage: python3 viewer.py filename")
        exit(1)
    app.frame.RunViewer()
    app.frame.Show(True)

    app.MainLoop()
