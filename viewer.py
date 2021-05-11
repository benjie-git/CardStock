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
from runner import Runner
import helpDialogs
from findEngineViewer import FindEngine
from wx.lib.mixins.inspection import InspectionMixin
from consoleWindow import ConsoleWindow

HERE = os.path.dirname(os.path.abspath(__file__))

ID_MENU_FIND = wx.NewIdRef()
ID_MENU_FIND_SEL = wx.NewIdRef()
ID_MENU_FIND_NEXT = wx.NewIdRef()
ID_MENU_FIND_PREV = wx.NewIdRef()
ID_MENU_REPLACE = wx.NewIdRef()
ID_SHOW_CONSOLE = wx.NewIdRef()
ID_CLEAR_CONSOLE = wx.NewIdRef()

# ----------------------------------------------------------------------


class ViewerFrame(wx.Frame):
    """
    A ViewerFrame contains a stackManger's view, and handles menu commands.
    """

    title = "CardStock"

    def __init__(self, parent, stackModel, filename):
        if stackModel and stackModel.GetProperty("canResize"):
            style = wx.DEFAULT_FRAME_STYLE
        else:
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

        wx.Frame.__init__(self, parent, -1, self.title, size=(500,500), style=style)
        # self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/stack.ico')))

        self.stackManager = StackManager(self, False)
        self.stackManager.view.UseDeferredRefresh(True)

        if not stackModel:
            stackModel = StackModel(self.stackManager)
            stackModel.AppendCardModel(CardModel(self.stackManager))

        self.designer = None
        self.stackManager.filename = filename
        self.SetStackModel(stackModel)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.findDlg = None
        self.findEngine = FindEngine(self.stackManager)

        self.consoleWindow = ConsoleWindow(self)

    def Destroy(self):
        if self.consoleWindow:
            self.consoleWindow.Destroy()
            self.consoleWindow = None
        self.findEngine.stackManager = None
        self.findEngine = None
        self.designer = None
        self.stackManager = None
        return super().Destroy()

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
        size = self.stackManager.stackModel.GetProperty("size")
        self.SetClientSize(size)
        self.stackManager.view.SetFocus()
        if self.stackManager.filename:
            self.SetTitle(self.title + ' -- ' + os.path.basename(self.stackManager.filename))

    def MakeMenu(self):
        # create the file menu
        fileMenu = wx.Menu()
        if not self.designer:
            fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl-O", "Open Stack")
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("canSave"):
            fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save Stack")
        if self.designer:
            fileMenu.Append(wx.ID_CLOSE, "&Close\tCtrl-W", "Close Stack")
        else:
            fileMenu.Append(wx.ID_EXIT, "&Quit\tCtrl-Q", "Quit Stack")

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
        helpMenu.Append(wx.ID_ABOUT, "&About\tCtrl-H", "About CardStock")
        helpMenu.Append(ID_SHOW_CONSOLE, "&Show/Hide Output Window\tCtrl-Alt-O", "Toggle Output Window")
        helpMenu.Append(ID_CLEAR_CONSOLE, "&Clear Output Window\tCtrl-Alt-C", "Clear Output Window")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,   self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU,   self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU,   self.OnMenuClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU,   self.OnMenuClose, id=wx.ID_EXIT)

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

        self.Bind(wx.EVT_MENU, self.OnMenuShowConsoleWindow, id=ID_SHOW_CONSOLE)
        self.Bind(wx.EVT_MENU, self.OnMenuClearConsoleWindow, id=ID_CLEAR_CONSOLE)

    wildcard = "CardStock files (*.cds)|*.cds|All files (*.*)|*.*"

    def OpenFile(self, filename):
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("canSave") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Closing?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.SaveFile()
        wx.GetApp().OpenFile(filename)

    def OnMenuOpen(self, event):
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("canSave") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Closing?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.SaveFile()

        dlg = wx.FileDialog(self, "Open CardStock file...", os.getcwd(),
                           style=wx.FD_OPEN, wildcard = self.wildcard)
        self.stackManager.view.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            dlg.Destroy()
            wx.GetApp().OpenFile(filename)
        else:
            dlg.Destroy()
            wx.CallLater(50, self.stackManager.view.Enable, True) # Needed to avoid a MSWindows FileDlg bug

    def OnMenuSave(self, event):
        self.SaveFile()

    def OnMenuClose(self, event):
        self.Close()

    def OnClose(self, event):
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("canSave") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Quitting?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                event.Veto()
                return
            if r == wx.ID_YES:
                self.SaveFile()

        if not self.stackManager.runner.stopRunnerThread:
            self.stackManager.SetDown()
            if self.consoleWindow:
                self.consoleWindow.Destroy()
                self.consoleWindow = None
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

    def OnMenuShowConsoleWindow(self, event):
        if self.consoleWindow.IsShown():
            self.consoleWindow.Hide()
        else:
            self.consoleWindow.Show()

    def OnMenuClearConsoleWindow(self, event):
        self.consoleWindow.Clear()

    def RunViewer(self, cardIndex):
        runner = Runner(self.stackManager)
        if self.designer:
            runner.onRunFinished = self.designer.OnRunnerFinished
        self.stackManager.runner = runner
        self.MakeMenu()
        self.SetClientSize(self.stackManager.stackModel.GetProperty("size"))
        if self.designer:
            runner.AddSyntaxErrors(self.designer.cPanel.codeEditor.analyzer.syntaxErrors)
        self.stackManager.stackModel.RunSetup(runner)
        self.stackManager.LoadCardAtIndex(cardIndex)


# ----------------------------------------------------------------------

class ViewerApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.argFilename = None
        self.doneStarting = False
        self.Init(self)  # for InspectionMixin
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.SetAppDisplayName('CardStock')
        self.frame = None

        return True

    def NewFile(self):
        if self.frame:
            self.frame.Hide()
            self.frame.Destroy()

        self.frame = ViewerFrame(None, None, None)
        self.SetTopWindow(self.frame)
        self.frame.Show(True)
        self.frame.RunViewer(0)

    def OpenFile(self, filename):
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                if data:
                    if self.frame:
                        self.frame.Hide()
                        self.frame.stackManager.SetDown()
                        self.frame.Destroy()

                    stackModel = StackModel(None)
                    stackModel.SetData(data)
                    self.frame = ViewerFrame(None, stackModel, filename)
                    stackModel.SetStackManager(self.frame.stackManager)
                    self.SetTopWindow(self.frame)
                    self.frame.stackManager.filename = filename
                    self.frame.Show(True)
                    self.frame.RunViewer(0)
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

    def MacOpenFile(self, filename):
        self.argFilename = filename
        if self.doneStarting:
            self.frame.OpenFile(self.argFilename)

# ----------------------------------------------------------------------


if __name__ == '__main__':
    app = ViewerApp(redirect=False)

    if len(sys.argv) > 1 and not app.argFilename:
        app.argFilename = sys.argv[1]

    if app.argFilename:
        app.OpenFile(app.argFilename)
    else:
        app.NewFile()

    app.doneStarting = True
    app.argFilename = None

    app.MainLoop()
