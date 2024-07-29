#!/usr/bin/python3
# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
This is the root frame of the CardStock stack viewer application.  It also is used to run stacks from within
the designer, and is used to run the stack from a standalone, exported app as well.
It allows running and using a stack, and even saving its updated state, if the stack has its can_save flag set to True.

Another thing to note is that this class manages the nesting of stacks when calling run_stack() and return_from_stack().
The list stackStack is a stack of cardstock stacks, and keeps the runner, stackModel, filename, and current cardIndex
of each stack(file) in the stack(list).
"""

import os
import sys
import json
import wx
import wx.html
from stackManager import StackManager
from stackModel import StackModel
from runner import Runner
import helpDialogs
from findEngineViewer import FindEngine
from consoleWindow import ConsoleWindow
from variablesWindow import VariablesWindow
from codeRunnerThread import RunOnMainSync, RunOnMainAsync

HERE = os.path.dirname(os.path.abspath(__file__))

ID_SHOW_INFO = wx.NewIdRef()
ID_MENU_FIND = wx.NewIdRef()
ID_MENU_FIND_SEL = wx.NewIdRef()
ID_MENU_FIND_NEXT = wx.NewIdRef()
ID_MENU_FIND_PREV = wx.NewIdRef()
ID_MENU_REPLACE = wx.NewIdRef()
ID_SHOW_VARIABLES = wx.NewIdRef()
ID_SHOW_CONSOLE = wx.NewIdRef()
ID_CLEAR_CONSOLE = wx.NewIdRef()

# ----------------------------------------------------------------------


class ViewerFrame(wx.Frame):
    """
    A ViewerFrame contains a stackManger's view, handles menu commands, manages the stack's runner, and the stack of stacks.
    """

    title = "CardStock"

    def __init__(self, parent, isStandalone, resMap=None):
        if isStandalone:
            self.title = os.path.basename(sys.executable)

        super().__init__(parent, -1, self.title, size=(500,500), style=wx.DEFAULT_FRAME_STYLE)

        self.stackManager = StackManager(self, False)
        self.stackManager.view.UseDeferredRefresh(True)
        if isStandalone and resMap:
            self.stackManager.resPathMan.SetPathMap(resMap)

        self.designer = None  # The designer sets this, if being run from the designer app
        self.isStandalone = isStandalone  # Are we running as a standalone app?
        self.generateThumbnail = False  # If set to true, the stack will run setup, create a thumbnail, and close
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.stackStack = []

        # The original runner for the stack that the user runs.  (As opposed to ones reached by run_stack().)
        self.rootRunner = None

        self.findDlg = None
        self.findEngine = FindEngine(self.stackManager)

        self.consoleWindow = ConsoleWindow(self, not self.isStandalone)
        if self.isStandalone:
            self.variablesWindow = None
        else:
            self.variablesWindow = VariablesWindow(self, self.stackManager)

    def Destroy(self):
        if self.consoleWindow:
            self.consoleWindow.Destroy()
            self.consoleWindow = None
        if self.findEngine:
            self.findEngine.stackManager = None
            self.findEngine = None
        self.designer = None
        self.stackManager = None
        return super().Destroy()

    def OnResize(self, event):
        if self.stackManager and self.stackManager.uiCard.model.GetProperty("can_resize"):
            if not self.stackManager.uiCard.runningInternalResize:
                size = self.stackManager.view.GetTopLevelParent().GetClientSize()
                size = self.stackManager.view.ToDIP(size)
                self.stackManager.uiCard.model.SetProperty("size", size)
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

    def MakeMenuBar(self):
        # create the file menu
        fileMenu = wx.Menu()

        if self.stackManager.stackModel.GetProperty("info").strip():
            fileMenu.Append(ID_SHOW_INFO, "Stack &Info\tCtrl-I", "Stack Info")
            fileMenu.AppendSeparator()

        if not self.isStandalone and not self.designer:
            fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl-O", "Open Stack")
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("can_save"):
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
        if not self.isStandalone:
            helpMenu.Append(ID_SHOW_VARIABLES, "&Show/Hide Variables\tCtrl-Alt-V", "Toggle Variables")
        helpMenu.Append(ID_SHOW_CONSOLE, "&Show/Hide Console\tCtrl-Alt-O", "Toggle Console")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        if self.designer or fileMenu.GetMenuItemCount() > 1:
            menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,  self.OnMenuInfo, id=ID_SHOW_INFO)

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

        if not self.isStandalone:
            self.Bind(wx.EVT_MENU, self.OnMenuShowVariablesWindow, id=ID_SHOW_VARIABLES)
        self.Bind(wx.EVT_MENU, self.OnMenuShowConsoleWindow, id=ID_SHOW_CONSOLE)

    def MakeConsoleMenuBar(self):
        # create the file menu
        fileMenu = wx.Menu()
        fileMenu.Append(ID_SHOW_CONSOLE, "&Close\tCtrl-W", "Close Console")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")

        # and the help menu
        helpMenu = wx.Menu()
        if not self.isStandalone:
            helpMenu.Append(ID_SHOW_VARIABLES, "&Show/Hide Variables\tCtrl-Alt-V", "Toggle Variables")
        helpMenu.Append(ID_SHOW_CONSOLE, "&Hide Console\tCtrl-Alt-O", "Toggle Console")
        helpMenu.Append(ID_CLEAR_CONSOLE, "&Clear Console\tCtrl-Alt-C", "Clear Console")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.consoleWindow.SetMenuBar(menuBar)

        self.consoleWindow.Bind(wx.EVT_MENU,   self.OnMenuClose, id=wx.ID_CLOSE)

        self.consoleWindow.Bind(wx.EVT_MENU,  self.consoleWindow.DoUndo, id=wx.ID_UNDO)
        self.consoleWindow.Bind(wx.EVT_MENU,  self.consoleWindow.DoRedo, id=wx.ID_REDO)

        if not self.isStandalone:
            self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuShowVariablesWindow, id=ID_SHOW_VARIABLES)
        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuShowConsoleWindow, id=ID_SHOW_CONSOLE)
        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuClearConsoleWindow, id=ID_CLEAR_CONSOLE)

    def MakeVariablesMenuBar(self):
        # create the file menu
        fileMenu = wx.Menu()
        fileMenu.Append(ID_SHOW_VARIABLES, "&Close\tCtrl-W", "Close Variables")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")

        # and the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(ID_SHOW_VARIABLES, "&Hide Variables\tCtrl-Alt-V", "Toggle Variables")
        helpMenu.Append(ID_SHOW_CONSOLE, "&Show/Hide Console\tCtrl-Alt-O", "Toggle Console")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.variablesWindow.SetMenuBar(menuBar)

        self.variablesWindow.Bind(wx.EVT_MENU,   self.OnMenuClose, id=wx.ID_CLOSE)

        self.variablesWindow.Bind(wx.EVT_MENU, self.OnMenuShowVariablesWindow, id=ID_SHOW_VARIABLES)
        self.variablesWindow.Bind(wx.EVT_MENU, self.OnMenuShowConsoleWindow, id=ID_SHOW_CONSOLE)

    wildcard = "CardStock files (*.cds)|*.cds"

    def OpenFile(self, filename):
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("can_save") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Closing?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.SaveFile()
        wx.GetApp().OpenFile(filename)

    def OnMenuOpen(self, event):
        if self.stackManager.filename and self.stackManager.stackModel.GetProperty("can_save") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Closing?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.SaveFile()

        initialDir = os.path.expanduser('~')
        if self.stackManager.filename:
            initialDir = os.path.dirname(self.stackManager.filename)
        initialDir = os.path.join(initialDir, '')
        dlg = wx.FileDialog(self, "Open CardStock file...", initialDir,
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
        self.Refresh()

    def OnClose(self, event):
        if not self.generateThumbnail and self.stackManager.filename and \
                self.stackManager.stackModel.GetProperty("can_save") and self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Quitting?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                event.Veto()
                return
            if r == wx.ID_YES:
                self.SaveFile()

        if not self.stackManager.runner.stopRunnerThread:
            self.stackManager.runner.RunHandler(self.stackManager.stackModel, "on_exit_stack", None)

            for _ in range(len(self.stackStack)-1):
                self.PopStack(None, True)

            self.stackManager.SetDown()
            if self.consoleWindow:
                self.consoleWindow.Destroy()
                self.consoleWindow = None
            event.Skip()

    def OnCut(self, event):
        def doCut():
            f = self.FindFocus()
            if f and hasattr(f, "Cut"):
                f.Cut()
        if wx.Platform == "__WXGTK__":
            wx.CallAfter(doCut)
        else:
            doCut()

    def OnCopy(self, event):
        def doCopy():
            f = self.FindFocus()
            if f and hasattr(f, "Copy"):
                f.Copy()
        if wx.Platform == "__WXGTK__":
            wx.CallAfter(doCopy)
        else:
            doCopy()

    def OnPaste(self, event):
        def doPaste():
            f = self.FindFocus()
            if f and hasattr(f, "Paste"):
                f.Paste()
        if wx.Platform == "__WXGTK__":
            wx.CallAfter(doPaste)
        else:
            doPaste()

    def OnUndo(self, event):
        def doUndo():
            f = self.FindFocus()
            if f and hasattr(f, "Undo"):
                if not hasattr(f, "CanUndo") or f.CanUndo():
                    f.Undo()
                    return False
            return True
        if wx.Platform == "__WXGTK__":
            wx.CallAfter(doUndo)
            event.Skip()
        else:
            if doUndo():
                event.Skip()

    def OnRedo(self, event):
        def doRedo():
            f = self.FindFocus()
            if f and hasattr(f, "Redo"):
                if not hasattr(f, "CanRedo") or f.CanRedo():
                    f.Redo()
                    return False
            return True
        if wx.Platform == "__WXGTK__":
            wx.CallAfter(doRedo)
            event.Skip()
        else:
            if doRedo():
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

    def OnMenuInfo(self, event=None):
        info = self.stackManager.stackModel.GetProperty("info")
        wx.MessageDialog(None, info, "Stack Info", wx.OK).ShowModal()

    def OnMenuAbout(self, event):
        dlg = helpDialogs.CardStockAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMenuShowVariablesWindow(self, event):
        if self.variablesWindow.IsShown():
            self.variablesWindow.Hide()
        else:
            self.variablesWindow.Show()
            self.variablesWindow.Raise()

    def UpdateVars(self):
        self.variablesWindow.UpdateVars()

    def OnMenuShowConsoleWindow(self, event):
        if self.consoleWindow.IsShown():
            self.consoleWindow.Hide()
        else:
            self.consoleWindow.Show()
            self.consoleWindow.Raise()

    def OnMenuClearConsoleWindow(self, event):
        self.consoleWindow.Clear()

    def GosubStack(self, filename, cardNumber, ioValue):
        # Enter here on a Runner thread
        # Go into, or back out of, another stack
        # Push a stack if a filename is given, else pop
        # ioValue is the setupValue or the returnValue
        # return True iff successful
        if filename:
            # push
            try:
                if not os.path.isabs(filename):
                    filename = os.path.join(os.path.dirname(self.stackManager.filename), filename)
                with open(filename, 'r') as f:
                    data = json.load(f)
                if data:
                    @RunOnMainAsync
                    def func():
                        # switch over to the main thread
                        stackModel = StackModel(None)
                        stackModel.SetData(data)
                        self.PushStack(stackModel, filename, cardNumber, ioValue)
                    func()
                    return True
            except (TypeError, FileNotFoundError):
                return False
        else:
            # pop
            if len(self.stackStack) > 1:
                @RunOnMainAsync
                def func():
                    # switch over to the main thread
                    self.PopStack(ioValue)
                func()
                return True
            else:
                return False

    def PushStack(self, stackModel, filename, cardIndex, setupValue=None):
        if len(self.stackStack) > 0:
            self.stackStack[-1][3] = self.stackManager.cardIndex
            self.stackManager.runner.StopTimers()

        runner = Runner(self.stackManager, self)
        runner.generatingThumbnail = self.generateThumbnail
        if len(self.stackStack) == 0:
            self.rootRunner = runner

        self.stackStack.append([runner, stackModel, filename, cardIndex])
        self.consoleWindow.runner = runner
        self.RunViewer(runner, stackModel, filename, cardIndex, setupValue, False)

    def PopStack(self, returnValue, isShuttingDown=False):
        if len(self.stackStack) > 1:
            sModel = self.stackManager.stackModel
            def onFinished(runner):
                runner.errors = None  # Not the root stack, so we're not reporting any errors here upon return to the designer
                sModel.SetDown()
                sModel.DismantleChildTree()

            self.stackManager.runner.onRunFinished = onFinished
            self.stackManager.runner.CleanupFromRun()

            self.stackStack.pop()
            parts = self.stackStack[-1]

            if not isShuttingDown:
                parts[1].SetBackUp(self.stackManager)
                self.RunViewer(*parts, returnValue, True)
            else:
                self.stackManager.runner = parts[0]
                self.stackManager.SetStackModel(parts[1], True)

    def SetupViewerSize(self):
        # Size the stack viewer window for the new stack, and allow resizing only if can_resize==True

        if wx.Platform != "__WXGTK__":
            self.SetMaxClientSize(wx.DefaultSize)
            self.SetMinClientSize(wx.DefaultSize)

        cs = self.FromDIP(self.stackManager.uiCard.model.GetProperty("size"))

        self.stackManager.view.SetSize(cs)
        self.stackManager.UpdateBuffer()
        self.SetClientSize(cs)

        if self.stackManager.uiCard.model.GetProperty("can_resize"):
            self.SetMinClientSize(self.FromDIP(wx.Size(200,200)))
        else:
            self.SetMinClientSize(wx.Size(100,100))
            self.SetMaxClientSize(wx.Size(100000,100000))
            self.SetMinClientSize(cs)
            self.SetMaxClientSize(cs)

    def RunViewer(self, runner, stackModel, filename, cardIndex, ioValue, isGoingBack):
        # Load the model, start the runner, and handle ioValues(setup and return values) for pushed/popped stacks
        self.stackManager.SetStackModel(stackModel, True)
        self.stackManager.filename = filename

        if self.designer:
            runner.onRunFinished = self.designer.OnRunnerFinished
        if not isGoingBack:
            runner.stackSetupValue = ioValue
        self.stackManager.runner = runner
        self.MakeMenuBar()
        if self.consoleWindow:
            self.MakeConsoleMenuBar()
        if self.variablesWindow:
            self.MakeVariablesMenuBar()

        if self.designer:
            runner.AddSyntaxErrors(self.designer.stackManager.analyzer.syntaxErrors)
        if not isGoingBack:
            self.stackManager.runner.SetupForCard(self.stackManager.stackModel.childModels[0])
            self.stackManager.stackModel.RunSetup(runner)
        self.stackManager.LoadCardAtIndex(None)
        if not (0 <= cardIndex < len(self.stackManager.stackModel.childModels)):
            cardIndex = 0
        self.stackManager.LoadCardAtIndex(cardIndex)
        self.SetupViewerSize()
        if self.generateThumbnail:
            # Once loading has finished, we'll call MakeThumbnail
            runner.AddCallbackToMain(self.MakeThumbnail)

        if isGoingBack:
            runner.DoReturnFromStack(ioValue)

    def MakeThumbnail(self):
        view = self.stackManager.view
        dc = wx.ClientDC(view)
        size = view.GetSize()
        bmp = wx.Bitmap(*size)
        memDC = wx.MemoryDC()
        memDC.SelectObject(bmp)
        memDC.Blit( 0, #Copy to this X coordinate
                    0, #Copy to this Y coordinate
                    size.width, #Copy this width
                    size.height, #Copy this height
                    dc, #From where do we copy?
                    0, #What's the X offset in the original DC?
                    0  #What's the Y offset in the original DC?
                    )
        img = bmp.ConvertToImage()
        memDC.SelectObject(wx.NullBitmap)

        # Shrink to fit inside a 160x160 square
        targetSize = 160
        scale = min(targetSize/size.width, targetSize/size.height)
        img.Rescale(int(size.width * scale), int(size.height * scale), wx.IMAGE_QUALITY_HIGH)
        self.designer.thumbnail = img.ConvertToBitmap()
        self.Close(True)


# ----------------------------------------------------------------------

class ViewerApp(wx.App):
    def OnInit(self):
        self.argFilename = None
        self.doneStarting = False
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.SetAppDisplayName('CardStock')
        self.frame = None

        return True

    def NewFile(self):
        if self.frame:
            self.frame.Hide()
            self.frame.Destroy()

        self.frame = ViewerFrame(None, False)
        self.frame.PushStack(self.frame.stackManager.stackModel, None, 0)
        self.SetTopWindow(self.frame)
        self.frame.Show(True)

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
                    self.frame = ViewerFrame(None, False)
                    self.frame.PushStack(stackModel, filename, 0)
                    self.SetTopWindow(self.frame)
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

    def MacOpenFile(self, filename):
        self.argFilename = filename
        if self.doneStarting:
            self.frame.OpenFile(self.argFilename)

# ----------------------------------------------------------------------


def RunViewerApp():
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


if __name__ == '__main__':
    if wx.Platform == "__WXMSW__":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        except:
            pass

    RunViewerApp()
