#!/usr/bin/python3

# designer.py
"""
This is the root of the main CardStock stack designer application.
It allows building and editing a stack, and running it to test it.
Use the viewer.py app to run and use a stack, without being able to edit it.
"""

import os
import sys
import json
import configparser
import wx
from time import sleep
import version
from tools import *
from stackManager import StackManager
from controlPanel import ControlPanel
from viewer import ViewerFrame
import helpDialogs
from errorListWindow import ErrorListWindow
from allCodeWindow import AllCodeWindow
from stackModel import StackModel
from uiCard import CardModel
from findEngineDesigner import FindEngine
from wx.lib.mixins.inspection import InspectionMixin
from stackExporter import StackExporter

HERE = os.path.dirname(os.path.realpath(__file__))

# ----------------------------------------------------------------------

ID_EXPORT = wx.NewIdRef()
ID_RUN = wx.NewIdRef()
ID_RUN_FROM = wx.NewIdRef()
ID_EDIT = wx.NewIdRef()
ID_MENU_FIND = wx.NewIdRef()
ID_MENU_FIND_SEL = wx.NewIdRef()
ID_MENU_FIND_NEXT = wx.NewIdRef()
ID_MENU_FIND_PREV = wx.NewIdRef()
ID_MENU_REPLACE = wx.NewIdRef()
ID_NEXT_CARD = wx.NewIdRef()
ID_PREV_CARD = wx.NewIdRef()
ID_ADD_CARD = wx.NewIdRef()
ID_DUPLICATE_CARD = wx.NewIdRef()
ID_REMOVE_CARD = wx.NewIdRef()
ID_MOVE_CARD_FWD = wx.NewIdRef()
ID_MOVE_CARD_BACK = wx.NewIdRef()
ID_GROUP = wx.NewIdRef()
ID_UNGROUP = wx.NewIdRef()
ID_FLIP_HORIZ = wx.NewIdRef()
ID_FLIP_VERT = wx.NewIdRef()
ID_MOVE_VIEW_FRONT = wx.NewIdRef()
ID_MOVE_VIEW_FWD = wx.NewIdRef()
ID_MOVE_VIEW_BACK = wx.NewIdRef()
ID_MOVE_VIEW_END = wx.NewIdRef()
ID_SHOW_ERROR_LIST = wx.NewIdRef()
ID_SHOW_ALL_CODE = wx.NewIdRef()


class DesignerFrame(wx.Frame):
    """
    A DesignerFrame contains a stackManger's window and a ControlPanel.  It opens and saves files, and handles or
    delegates all menu commands.
    """

    title = "CardStock"

    def __init__(self, parent):
        # Set up config file
        config_folder = os.path.join(os.path.expanduser("~"), '.config')
        os.makedirs(config_folder, exist_ok=True)
        settings_file = "cardstock.conf"
        self.full_config_file_path = os.path.join(config_folder, settings_file)

        super().__init__(parent, -1, self.title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinClientSize(wx.Size(600,500))
        # self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/stack.png')))
        self.CreateStatusBar()
        self.editMenu = None
        self.MakeMenu()
        self.filename = None
        self.app = None

        toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        toolbar.AddTool(ID_RUN, 'Run', wx.ArtProvider.GetBitmap(wx.ART_FULL_SCREEN), wx.NullBitmap)

        toolbar.AddStretchableSpace()

        self.cardPicker = wx.Choice(parent=toolbar, size=(200,20))
        self.cardPicker.Bind(wx.EVT_CHOICE, self.OnPickCard)
        toolbar.AddControl(self.cardPicker)

        toolbar.AddTool(ID_PREV_CARD, 'Previous Card', wx.ArtProvider.GetBitmap(wx.ART_GO_BACK), wx.NullBitmap)
        toolbar.AddTool(ID_ADD_CARD, 'Add Card', wx.ArtProvider.GetBitmap(wx.ART_PLUS), wx.NullBitmap)
        toolbar.AddTool(ID_NEXT_CARD, 'Next Card', wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD), wx.NullBitmap)

        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnMenuRun, id=ID_RUN)
        self.Bind(wx.EVT_FIND, self.OnFindEvent)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFindEvent)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplaceEvent)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAllEvent)

        self.splitter = wx.SplitterWindow(self, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        self.stackContainer = wx.Window(self.splitter)
        self.stackContainer.SetBackgroundColour("#E0E0E0")
        self.stackContainer.Bind(wx.EVT_SET_FOCUS, self.OnStackContainerFocus)
        self.stackManager = StackManager(self.stackContainer)
        self.stackManager.SetDesigner(self)

        self.stackManager.command_processor.SetEditMenu(self.editMenu)
        self.stackContainer.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        self.stackContainer.Bind(wx.EVT_LEFT_DCLICK, self.FwdOnMouseDown)
        self.stackContainer.Bind(wx.EVT_MOVE, self.FwdOnMouseMove)
        self.stackContainer.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseDown)
        self.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

        self.cPanel = ControlPanel(self.splitter, -1, self.stackManager)
        self.cPanel.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        self.cPanel.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

        self.splitter.SplitVertically(self.stackContainer, self.cPanel)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(self.splitter.GetSize()[0]-600)
        self.splitter.SetSashGravity(0.0)

        self.cPanel.SetSize([600,600])
        self.cPanel.Layout()

        self.cPanel.SetToolByName("hand")

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.findDlg = None
        self.findEngine = FindEngine(self.stackManager)

        self.allCodeWindow = None
        self.errorListWindow = None
        self.lastRunErrors = []

        self.viewer = None
        self.isStartingViewer = False
        self.NewFile()

    def NewFile(self):
        self.filename = None
        stackModel = StackModel(self.stackManager)
        newCard = CardModel(self.stackManager)
        newCard.SetProperty("name", newCard.DeduplicateName("card_1",
                                                            [m.GetProperty("name") for m in stackModel.childModels]),
                                                            notify=False)
        stackModel.AppendCardModel(newCard)
        self.stackManager.filename = None
        self.stackManager.resPathMan.Reset()
        self.stackManager.SetStackModel(stackModel)
        self.stackManager.SetEditing(True)
        self.Layout()
        stackModel.SetProperty("size", self.stackManager.view.GetSize())
        self.stackManager.SelectUiView(self.stackManager.uiCard)
        self.stackManager.view.Refresh()
        self.stackManager.view.SetFocus()
        self.SetFrameSizeFromModel()
        self.stackManager.stackModel.SetDirty(False)
        self.UpdateCardList()
        if self.allCodeWindow:
            self.allCodeWindow.Destroy()
            self.allCodeWindow = None
        if self.errorListWindow:
            self.errorListWindow.Destroy()
            self.errorListWindow = None
        self.lastRunErrors = []

    def SaveFile(self):
        if self.filename:
            # Defocus the inspector, which saves any updated value later, onIdle.  Then yield to idle now.
            self.stackManager.view.SetFocus()
            wx.YieldIfNeeded()
            data = self.stackManager.stackModel.GetData()
            try:
                jsonData = json.dumps(data, indent=2)
                with open(self.filename, 'w') as f:
                    f.write(jsonData)
                self.stackManager.stackModel.SetDirty(False)
            except TypeError:
                # e = sys.exc_info()
                # print(e)
                wx.MessageDialog(None, str("Couldn't save file"), "", wx.OK).ShowModal()

    def ReadFile(self, filename):
        if filename:
            stackModel = None
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                if data:
                    stackModel = StackModel(self.stackManager)
                    stackModel.SetData(data)
            except:
                stackModel = None
                self.NewFile()
                wx.YieldIfNeeded()
                wx.MessageDialog(None, str("Couldn't read file"), "", wx.OK).ShowModal()

            if stackModel:
                self.stackManager.SetDesigner(self)
                self.filename = filename
                self.stackManager.filename = filename
                self.stackManager.resPathMan.Reset()
                self.stackManager.SetStackModel(stackModel)
                self.stackManager.SetEditing(True)
                self.stackManager.SelectUiView(self.stackManager.uiCard)
                self.SetFrameSizeFromModel()
                self.stackManager.stackModel.SetDirty(False)
                self.UpdateCardList()
                self.stackManager.view.Refresh()
                self.stackManager.view.SetFocus()
                self.SetTitle(self.title + ' -- ' + os.path.basename(self.filename))
                self.WriteConfig()
                self.cPanel.SetToolByName("hand")
                if self.allCodeWindow:
                    self.allCodeWindow.Destroy()
                    self.allCodeWindow = None
                if self.errorListWindow:
                    self.errorListWindow.Destroy()
                    self.errorListWindow = None
                self.lastRunErrors = []

    def SetFrameSizeFromModel(self):
        self.stackContainer.SetSize(self.stackManager.view.GetSize())
        clientSize = (self.stackManager.view.GetSize().Width + self.splitter.GetSashSize() + self.cPanel.GetSize().Width,
                      max(self.stackManager.view.GetSize().Height, 500))
        self.splitter.SetSize(clientSize)
        self.SetClientSize(clientSize)
        self.splitter.SetSashPosition(self.stackManager.view.GetSize().Width)

    def SetSelectedUiViews(self, views):
        self.cPanel.UpdateForUiViews(views)

    def UpdateSelectedUiViews(self):
        self.cPanel.UpdateInspectorForUiViews(self.stackManager.GetSelectedUiViews())
        self.cPanel.UpdateHandlerForUiViews(self.stackManager.GetSelectedUiViews(), None)

    def FwdOnMouseDown(self, event):
        self.stackManager.OnMouseDown(self.stackManager.uiCard, event)

    def FwdOnMouseMove(self, event):
        self.stackManager.OnMouseMove(self.stackManager.uiCard, event)

    def FwdOnMouseUp(self, event):
        self.stackManager.OnMouseUp(self.stackManager.uiCard, event)

    def FwdOnKeyDown(self, event):
        self.stackManager.OnKeyDown(None, event)

    def FwdOnKeyUp(self, event):
        self.stackManager.OnKeyUp(None, event)

    def MakeMenu(self):
        # create the file menu
        # Using the "\tKeyName" syntax automatically creates a
        # wx.AcceleratorTable for this frame and binds the keys to
        # the menu items.
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, "&New Stack\tCtrl-N", "Create a new Stack file")
        fileMenu.Append(wx.ID_OPEN, "&Open Stack...\tCtrl-O", "Open a Stack")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_SAVE, "&Save Stack\tCtrl-S", "Save the Stack")
        fileMenu.Append(wx.ID_SAVEAS, "Save Stack &As...\tCtrl-Shift-S", "Save the Stack in a new file")
        fileMenu.Append(ID_EXPORT, "&Export Stack...\tCtrl-Shift-E", "Export the current Stack")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_RUN, "&Run Stack\tCtrl-R", "Run the current Stack")
        fileMenu.Append(ID_RUN_FROM, "&Run From Current Card\tCtrl-Shift-R", "Run from the current Card")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "E&xit", "Terminate the application")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "Re&do\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_SELECTALL,  "Select A&ll\tCtrl-A", "Select All")
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")
        editMenu.AppendSeparator()
        editMenu.Append(ID_MENU_FIND, "&Find...\tCtrl-F", "Find... in stack")
        editMenu.Append(ID_MENU_FIND_SEL, "&Find Selection\tCtrl-E", "Find Selection")
        editMenu.Append(ID_MENU_FIND_NEXT, "&Find Next\tCtrl-G", "Find Next in stack")
        editMenu.Append(ID_MENU_FIND_PREV, "&Find Previous\tCtrl-Shift-G", "Find Previous in stack")
        editMenu.Append(ID_MENU_REPLACE, "&Replace...\tCtrl-Shift-F", "Replace in stack")
        self.editMenu = editMenu

        cardMenu = wx.Menu()
        cardMenu.Append(ID_NEXT_CARD, "&Next Card\tCtrl-]", "Next Card")
        cardMenu.Append(ID_PREV_CARD, "&Previous Card\tCtrl-[", "Previous Card")
        cardMenu.AppendSeparator()
        cardMenu.Append(ID_ADD_CARD, "&Add Card\tCtrl-+", "Add Card")
        cardMenu.Append(ID_DUPLICATE_CARD, "&Duplicate Card\tCtrl-Alt-+", "Duplicate Card")
        cardMenu.Append(ID_REMOVE_CARD, "&Remove Card", "Remove Card")
        cardMenu.AppendSeparator()
        cardMenu.Append(ID_MOVE_CARD_FWD, "Move Card &Forward\tCtrl-Shift-]", "Move Card Forward")
        cardMenu.Append(ID_MOVE_CARD_BACK, "Move Card Bac&k\tCtrl-Shift-[", "Move Card Back")

        viewMenu = wx.Menu()
        viewMenu.Append(ID_GROUP, "&Group Objects\tCtrl-Alt-G", "Group Objects")
        viewMenu.Append(ID_UNGROUP, "&Ungroup Objects\tCtrl-Alt-U", "Ungroup Objects")
        viewMenu.AppendSeparator()
        viewMenu.Append(ID_FLIP_HORIZ, "Flip Horizontal\tCtrl-Alt-H", "Flip Horizontal")
        viewMenu.Append(ID_FLIP_VERT, "Flip Vertical\tCtrl-Alt-V", "Flip Vertical")
        viewMenu.AppendSeparator()
        viewMenu.Append(ID_MOVE_VIEW_FRONT, "Move to Front\tCtrl-Alt-Shift-F", "Move to Front")
        viewMenu.Append(ID_MOVE_VIEW_FWD, "Move &Forward\tCtrl-Alt-F", "Move Forward")
        viewMenu.Append(ID_MOVE_VIEW_BACK, "Move Bac&kward\tCtrl-Alt-B", "Move Back")
        viewMenu.Append(ID_MOVE_VIEW_END, "Move to Back\tCtrl-Alt-Shift-B", "Move to Back")

        # and the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "&About", "About")
        helpMenu.Append(wx.ID_HELP, "&Manual\tCtrl-Alt-M", "Manual")
        helpMenu.Append(wx.ID_REFRESH, "&Reference Guide\tCtrl-Alt-R", "Reference Guide")
        helpMenu.Append(wx.ID_CONTEXT_HELP, "&Show/Hide Context Help\tCtrl-Alt-C", "Toggle Context Help")
        helpMenu.Append(ID_SHOW_ERROR_LIST, "&Show/Hide Error List Window\tCtrl-Alt-E", "Toggle Errors")
        helpMenu.Append(ID_SHOW_ALL_CODE, "&Show/Hide All Code Window\tCtrl-Alt-A", "Toggle AllCode")


        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(cardMenu, "&Card")
        menuBar.Append(viewMenu, "&Object")
        menuBar.Append(helpMenu, "&Help ")  # Add the space to avoid magically adding platform-specific help menu items
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnMenuNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnMenuExport, id=ID_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnMenuRun, id=ID_RUN)
        self.Bind(wx.EVT_MENU, self.OnMenuRunFrom, id=ID_RUN_FROM)
        self.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.OnMenuAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnMenuHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnMenuReference, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.OnMenuContextHelp, id=wx.ID_CONTEXT_HELP)

        self.Bind(wx.EVT_MENU, self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.OnMenuFind, id=ID_MENU_FIND)
        self.Bind(wx.EVT_MENU, self.OnMenuFindSel, id=ID_MENU_FIND_SEL)
        self.Bind(wx.EVT_MENU, self.OnMenuFindNext, id=ID_MENU_FIND_NEXT)
        self.Bind(wx.EVT_MENU, self.OnMenuFindPrevious, id=ID_MENU_FIND_PREV)
        self.Bind(wx.EVT_MENU, self.OnMenuReplace, id=ID_MENU_REPLACE)

        self.Bind(wx.EVT_MENU, self.OnMenuNextCard, id=ID_NEXT_CARD)
        self.Bind(wx.EVT_MENU, self.OnMenuPrevCard, id=ID_PREV_CARD)
        self.Bind(wx.EVT_MENU, self.OnMenuAddCard, id=ID_ADD_CARD)
        self.Bind(wx.EVT_MENU, self.OnMenuDuplicateCard, id=ID_DUPLICATE_CARD)
        self.Bind(wx.EVT_MENU, self.OnMenuRemoveCard, id=ID_REMOVE_CARD)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveCard, id=ID_MOVE_CARD_FWD)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveCard, id=ID_MOVE_CARD_BACK)

        self.Bind(wx.EVT_MENU, self.OnMenuGroup, id=ID_GROUP)
        self.Bind(wx.EVT_MENU, self.OnMenuUngroup, id=ID_UNGROUP)
        self.Bind(wx.EVT_MENU, self.OnMenuFlipHorizontal, id=ID_FLIP_HORIZ)
        self.Bind(wx.EVT_MENU, self.OnMenuFlipVertical, id=ID_FLIP_VERT)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_FRONT)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_FWD)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_BACK)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_END)
        self.Bind(wx.EVT_MENU, self.OnMenuShowErrorList, id=ID_SHOW_ERROR_LIST)
        self.Bind(wx.EVT_MENU, self.OnMenuShowAllCodeWindow, id=ID_SHOW_ALL_CODE)


    wildcard = "CardStock files (*.cds)|*.cds|All files (*.*)|*.*"

    def OnMenuNew(self, event):
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before starting a New file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        self.NewFile()
        self.SetTitle(self.title)

    def OnMenuOpen(self, event):
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Opening a file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        dlg = wx.FileDialog(self, "Open CardStock file...", os.getcwd(),
                           style=wx.FD_OPEN, wildcard = self.wildcard)
        self.stackContainer.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.ReadFile(filename)
        dlg.Destroy()
        wx.CallLater(50, self.stackContainer.Enable, True) # Needed to avoid a MSWindows FileDlg bug

    def OnMenuSave(self, event):
        if not self.filename:
            self.OnMenuSaveAs(event)
        else:
            self.SaveFile()

    def OnMenuSaveAs(self, event):
        dlg = wx.FileDialog(self, "Save CaardStock file as...", os.getcwd(),
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           wildcard = self.wildcard)
        self.stackContainer.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.cds'
            self.filename = filename
            self.stackManager.filename = filename
            self.stackManager.resPathMan.Reset()
            self.SaveFile()
            self.SetTitle(self.title + ' -- ' + os.path.basename(self.filename))
            self.WriteConfig()
        dlg.Destroy()
        wx.CallLater(50, self.stackContainer.Enable, True) # Needed to avoid a MSWindows FileDlg bug

    def OnMenuExport(self, event):
        def doSave():
            self.OnMenuSave(None)
        exporter = StackExporter(self.stackManager)
        exporter.StartExport(doSave)

    def RunFromCard(self, cardIndex):
        if self.isStartingViewer:
            return
        self.isStartingViewer = True

        if self.viewer:
            self.viewer.Destroy()

        if self.errorListWindow and self.errorListWindow.IsShown():
            self.errorListWindow.Hide()

        if self.allCodeWindow and self.allCodeWindow.IsShown():
            self.allCodeWindow.Hide()
            self.allCodeWindow.Clear()

        data = self.stackManager.stackModel.GetData()
        stackModel = StackModel(None)
        stackModel.SetData(data)

        self.Hide()
        if self.stackManager.analyzer.analysisPending:
            self.stackManager.analyzer.RunAnalysis()
            while self.stackManager.analyzer.analysisPending:
                # make sure we have an up-to-date analysis and set of syntax errors
                wx.YieldIfNeeded()
                sleep(0.05)

        self.viewer = ViewerFrame(self, stackModel, self.filename)
        self.viewer.designer = self

        self.viewer.Show(True)
        self.viewer.Refresh()
        self.viewer.RunViewer(cardIndex)
        self.isStartingViewer = False

    def OnMenuRun(self, event):
        self.RunFromCard(0)

    def OnMenuRunFrom(self, event):
        self.RunFromCard(self.stackManager.cardIndex)

    def OnViewerSave(self, stackModel):
        newModel = StackModel(self.stackManager)
        newModel.SetData(stackModel.GetData())
        self.stackManager.SetStackModel(newModel)

    def OnViewerClose(self, event):
        self.lastRunErrors = self.viewer.stackManager.runner.errors
        self.viewer.Destroy()
        self.viewer = None
        self.Refresh()
        self.Show()

        if len(self.lastRunErrors):
            self.OnMenuShowErrorList(None)

    def OnMenuShowErrorList(self, event):
        if self.errorListWindow:
            if self.errorListWindow.IsShown():
                self.errorListWindow.Hide()
            else:
                self.errorListWindow.Show()
        else:
            self.errorListWindow = ErrorListWindow(self)
            self.errorListWindow.SetPosition(self.GetPosition() + (100, 10))
            self.errorListWindow.Show()
            self.errorListWindow.Bind(wx.EVT_CLOSE, self.OnErrorListClose)

        self.errorListWindow.SetErrorList(self.lastRunErrors)

    def OnErrorListClose(self, event):
        self.errorListWindow.Hide()

    def OnMenuShowAllCodeWindow(self, event):
        if self.allCodeWindow:
            if self.allCodeWindow.IsShown():
                self.allCodeWindow.Hide()
                self.allCodeWindow.Clear()
            else:
                self.allCodeWindow.UpdateCode()
                self.allCodeWindow.Show()
        else:
            self.allCodeWindow = AllCodeWindow(self)
            self.allCodeWindow.SetPosition(self.GetPosition() + (50, 100))
            self.allCodeWindow.UpdateCode()
            self.allCodeWindow.Show()
            self.allCodeWindow.Bind(wx.EVT_CLOSE, self.OnAllCodeWindowClose)

    def OnAllCodeWindowClose(self, event):
        self.allCodeWindow.Hide()
        self.allCodeWindow.Clear()

    def OnMenuExit(self, event):
        self.Close()

    def OnClose(self, event):
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Quitting?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                event.Veto()
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)
        if self.viewer:
            self.viewer.Destroy()
        event.Skip()

    def OnMenuGroup(self, event):
        self.stackManager.GroupSelectedViews()

    def OnMenuUngroup(self, event):
        self.stackManager.UngroupSelectedViews()

    def OnMenuFlipHorizontal(self, event):
        self.stackManager.FlipSelection(True)

    def OnMenuFlipVertical(self, event):
        self.stackManager.FlipSelection(False)

    def OnMenuMoveView(self, event):
        if event.GetId() == ID_MOVE_VIEW_FRONT:
            self.stackManager.ReorderSelectedViews("front")
        elif event.GetId() == ID_MOVE_VIEW_FWD:
            self.stackManager.ReorderSelectedViews("fwd")
        elif event.GetId() == ID_MOVE_VIEW_BACK:
            self.stackManager.ReorderSelectedViews("back")
        elif event.GetId() == ID_MOVE_VIEW_END:
            self.stackManager.ReorderSelectedViews("end")

    def OnMenuMoveCard(self, event):
        if event.GetId() == ID_MOVE_CARD_FWD:
            self.stackManager.ReorderCurrentCard("fwd")
        elif event.GetId() == ID_MOVE_CARD_BACK:
            self.stackManager.ReorderCurrentCard("back")

    def OnMenuNextCard(self, event):
        index = self.stackManager.cardIndex+1
        if index < len(self.stackManager.stackModel.childModels):
            self.stackManager.LoadCardAtIndex(index)

    def OnMenuPrevCard(self, event):
        index = self.stackManager.cardIndex-1
        if index >= 0:
            self.stackManager.LoadCardAtIndex(index)

    def OnMenuAddCard(self, event):
        self.stackManager.AddCard()

    def OnMenuDuplicateCard(self, event):
        self.stackManager.DuplicateCard()

    def OnMenuRemoveCard(self, event):
        self.stackManager.RemoveCard()

    def OnPickCard(self, event):
        self.stackManager.LoadCardAtIndex(event.GetSelection())

    def UpdateCardList(self):
        choices = []
        i = 1
        numCards = len(self.stackManager.stackModel.childModels)
        for m in self.stackManager.stackModel.childModels:
            choices.append(f"Card {i} of {numCards}: {m.GetProperty('name')}")
            i += 1
        self.cardPicker.SetItems(choices)
        self.cardPicker.SetSelection(self.stackManager.cardIndex)

    def OnStackContainerFocus(self, event):
        self.stackManager.view.SetFocus()

    def GetDesiredFocus(self, allowEditors):
        f = self.FindFocus()
        views = [self.stackContainer, self.stackManager.view, self.cPanel, self.splitter, self.cPanel.inspector, self.cPanel.codeEditor]
        if allowEditors:
            views = [self.stackContainer, self.stackManager.view, self.splitter, self.cPanel]
        if not f or f in views or isinstance(f, wx.lib.buttons.GenBitmapToggleButton):
            f = self.stackManager
        return f

    def OnSelectAll(self, event):
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "SelectAll"):
            f.SelectAll()

    def OnCut(self, event):
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Cut"):
            f.Cut()

    def OnCopy(self, event):
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Copy"):
            f.Copy()

    def OnPaste(self, event):
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Paste"):
            f.Paste()

    def OnUndo(self, event):
        f = self.GetDesiredFocus(False)
        if f and hasattr(f, "Undo"):
            if not hasattr(f, "CanUndo") or f.CanUndo():
                f.Undo()
                return
        event.Skip()

    def OnRedo(self, event):
        f = self.GetDesiredFocus(False)
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

    def OnMenuHelp(self, event):
        dlg = helpDialogs.CardStockManual(self)
        dlg.Bind(wx.EVT_CLOSE, self.OnHelpClose)
        dlg.Show()

    def OnMenuReference(self, event):
        dlg = helpDialogs.CardStockReference(self)
        dlg.Bind(wx.EVT_CLOSE, self.OnHelpClose)
        dlg.Show()

    def OnMenuContextHelp(self, event):
        self.cPanel.ToggleContextHelp()
        self.WriteConfig()

    def OnHelpClose(self, event):
        event.GetEventObject().Destroy()

    def FinishedStarting(self):
        if not self.filename:
            config = self.ReadConfig()
            self.cPanel.ShowContextHelp(config["show_context_help"])
            if config["last_open_file"] and os.path.exists(config["last_open_file"]):
                self.ReadFile(config["last_open_file"])

    def WriteConfig(self):
        config = configparser.ConfigParser()
        config['User'] = {"last_open_file": self.filename if self.filename else "",
                          "show_context_help": str(self.cPanel.IsContextHelpShown()),
                          "cardstock_app_version": version.VERSION}
        with open(self.full_config_file_path, 'w') as configfile:
            config.write(configfile)

    def ReadConfig(self):
        last_open_file = None
        show_context_help = True
        cardstock_app_version = "0"
        if not os.path.exists(self.full_config_file_path) \
                or os.stat(self.full_config_file_path).st_size == 0:
            self.WriteConfig()
        if os.path.exists(self.full_config_file_path) and os.stat(self.full_config_file_path).st_size > 0:
            config = configparser.ConfigParser()
            config.read(self.full_config_file_path)
            last_open_file = config['User'].get('last_open_file', None)
            show_context_help = config['User'].get('show_context_help', "True") == "True"
            cardstock_app_version = config['User'].get('cardstock_app_version', "0")

        if not last_open_file:
            # On first run, open the welcome stack
            def welcomeExistsHere(path):
                return os.path.exists(os.path.join(path, os.path.join("examples", "welcome.cds")))

            base_dir = os.path.dirname(__file__)
            if not welcomeExistsHere(base_dir):
                base_dir = os.path.dirname(sys.executable)
                if not welcomeExistsHere(base_dir):
                    base_dir = sys._MEIPASS
            last_open_file = os.path.abspath(os.path.join(base_dir, os.path.join("examples", "welcome.cds")))
        return {"last_open_file": last_open_file,
                "show_context_help": show_context_help,
                "cardstock_app_version": cardstock_app_version}

# ----------------------------------------------------------------------


class DesignerApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init() # for InspectionMixin
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.frame = DesignerFrame(None)
        self.frame.app = self
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.SetAppDisplayName('CardStock')
        return True

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
    app = DesignerApp(redirect=False)

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        app.frame.ReadFile(filename)
    app.frame.FinishedStarting()
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()
