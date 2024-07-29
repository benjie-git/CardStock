#!/usr/bin/python3
# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
import embeddedImages
from time import sleep
import version
from tools import *
from stackManager import StackManager
from controlPanel import ControlPanel
from viewer import ViewerFrame
import helpDialogs
from errorListWindow import ErrorListWindow
from allCodeWindow import AllCodeWindow
from consoleWindow import ConsoleWindow
from stackModel import StackModel
from uiCard import CardModel
from findEngineDesigner import FindEngine
from stackExporter import StackExporter
import mediaSearchDialogs
from runner import Runner
from imageFactory import ImageFactory
from pythonEditor import PythonEditor
from codeRunnerThread import RunOnMainSync
# import gc

HERE = os.path.dirname(os.path.realpath(__file__))

# ----------------------------------------------------------------------

ID_OPEN_EXAMPLE = wx.NewIdRef()
ID_EXPORT = wx.NewIdRef()
ID_EDIT_STACK = wx.NewIdRef()
ID_RUN = wx.NewIdRef()
ID_RUN_FROM = wx.NewIdRef()
ID_SEARCH_IMAGE = wx.NewIdRef()
ID_SEARCH_SOUND = wx.NewIdRef()
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
ID_ALIGN_HL = wx.NewIdRef()
ID_ALIGN_HC = wx.NewIdRef()
ID_ALIGN_HR = wx.NewIdRef()
ID_ALIGN_VT = wx.NewIdRef()
ID_ALIGN_VC = wx.NewIdRef()
ID_ALIGN_VB = wx.NewIdRef()
ID_DISTRIBUTE_HL = wx.NewIdRef()
ID_DISTRIBUTE_HC = wx.NewIdRef()
ID_DISTRIBUTE_HS = wx.NewIdRef()
ID_DISTRIBUTE_HR = wx.NewIdRef()
ID_DISTRIBUTE_VT = wx.NewIdRef()
ID_DISTRIBUTE_VC = wx.NewIdRef()
ID_DISTRIBUTE_VS = wx.NewIdRef()
ID_DISTRIBUTE_VB = wx.NewIdRef()
ID_FLIP_HORIZ = wx.NewIdRef()
ID_FLIP_VERT = wx.NewIdRef()
ID_MOVE_VIEW_FRONT = wx.NewIdRef()
ID_MOVE_VIEW_FWD = wx.NewIdRef()
ID_MOVE_VIEW_BACK = wx.NewIdRef()
ID_MOVE_VIEW_END = wx.NewIdRef()
ID_SHOW_ERROR_LIST = wx.NewIdRef()
ID_SHOW_ALL_CODE = wx.NewIdRef()
ID_BASICS = wx.NewIdRef()
ID_SHOW_CONSOLE = wx.NewIdRef()
ID_CLEAR_CONSOLE = wx.NewIdRef()


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
        self.configInfo = self.ReadConfig()

        super().__init__(parent, -1, self.title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE)
        self.SetMinClientSize(self.FromDIP(wx.Size(500,500)))
        # self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/stack.png')))
        sb = self.CreateStatusBar()
        sb.SetFieldsCount(2, (self.FromDIP(80), self.FromDIP(400)))

        self.editMenu = None
        self.MakeMenuBar()
        self.filename = None
        self.app = None
        # self.lastStats = {}

        self.toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        icn = embeddedImages.run.GetBitmap()
        self.toolbar.AddTool(ID_EDIT_STACK, 'Stack', embeddedImages.stack.GetBitmap(), wx.NullBitmap)
        self.toolbar.AddTool(ID_RUN, 'Run Stack', icn, wx.NullBitmap)

        self.toolbar.AddStretchableSpace()

        self.cardPicker = wx.Choice(parent=self.toolbar)
        self.cardPicker.Bind(wx.EVT_CHOICE, self.OnPickCard)
        self.cardPickerToolId = self.toolbar.AddControl(self.cardPicker).GetId()

        self.toolbar.AddTool(ID_PREV_CARD, 'Previous Card', wx.ArtProvider.GetBitmap(wx.ART_GO_BACK), wx.NullBitmap)
        self.toolbar.AddTool(ID_ADD_CARD, 'Add Card', wx.ArtProvider.GetBitmap(wx.ART_PLUS), wx.NullBitmap)
        self.toolbar.AddTool(ID_NEXT_CARD, 'Next Card', wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD), wx.NullBitmap)

        self.toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnMenuEditStack, id=ID_EDIT_STACK)
        self.Bind(wx.EVT_TOOL, self.OnMenuRun, id=ID_RUN)
        self.Bind(wx.EVT_FIND, self.OnFindEvent)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFindEvent)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnReplaceEvent)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAllEvent)

        self.splitter = wx.SplitterWindow(self, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)
        self.splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDoubleClick)
        self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnSplitterChanging)

        self.stackContainer = wx.Window(self.splitter)
        self.stackContainer.SetBackgroundColour("#E0E0E0")
        self.stackContainer.Bind(wx.EVT_SET_FOCUS, self.OnStackContainerFocus)
        self.stackManager = StackManager(self.stackContainer, True)
        self.stackManager.SetDesigner(self)

        self.stackManager.command_processor.SetEditMenu(self.editMenu)
        self.stackContainer.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        self.stackContainer.Bind(wx.EVT_LEFT_DCLICK, self.FwdOnMouseDown)
        self.stackContainer.Bind(wx.EVT_MOVE, self.FwdOnMouseMove)
        self.stackContainer.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseDown)
        self.stackManager.view.Bind(wx.EVT_SIZE, self.OnStackResize)
        self.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)
        self.Bind(wx.EVT_SIZE, self.OnFrameResize)

        self.cPanel = ControlPanel(self.splitter, -1, self.stackManager)
        self.cPanel.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        self.cPanel.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

        self.splitter.SplitVertically(self.stackContainer, self.cPanel)
        self.splitter.SetMinimumPaneSize(self.FromDIP(120))
        self.splitter.SetSashPosition(self.splitter.GetSize()[0]-self.FromDIP(600))
        self.splitter.SetSashGravity(1.0)

        self.cPanel.SetSize([600,600])
        self.cPanel.Layout()

        self.cPanel.SetToolByName("hand")

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.findDlg = None
        self.findEngine = FindEngine(self.stackManager)

        self.allCodeWindow = None
        self.errorListWindow = None
        self.consoleWindow = None
        self.wasConsoleOpen = False
        self.lastRunErrors = []
        self.runnerFinishedCallback = None

        self.viewer = None
        self.thumbnail = None
        self.isStartingViewer = False
        self.NewFile()
        self.UpdateStatusBar(None, None)

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
        self.stackManager.LoadCardAtIndex(0)
        self.Layout()
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
            except Exception as e:
                stackModel = None
                self.NewFile()
                wx.YieldIfNeeded()
                wx.MessageDialog(None, "Couldn't read file:" + str(e), "", wx.OK).ShowModal()

            if stackModel:
                self.stackManager.SetDesigner(self)
                self.filename = filename
                self.stackManager.filename = filename
                self.stackManager.resPathMan.Reset()
                self.stackManager.SetStackModel(stackModel)
                self.stackManager.LoadCardAtIndex(0)
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
        size = self.stackManager.uiCard.model.GetProperty("size")
        self.stackManager.uiCard.ResizeCardView(size)
        size = self.FromDIP(size)
        self.stackManager.UpdateBuffer()
        cPanelWidth = max(self.FromDIP(self.cPanel.defaultPanelWidth), self.cPanel.GetSize().Width)
        clientSize = (size.Width + self.splitter.GetSashSize() + cPanelWidth,
                      max(size.Height, self.FromDIP(500)))
        def updateSize():
            self.splitter.SetSize(clientSize)
            self.SetClientSize(clientSize)
            self.splitter.SetSashPosition(size.Width)
        updateSize()
        wx.CallAfter(updateSize)  # fix initial sizing on linux

    def OnSplitterDoubleClick(self, event):
        self.splitter.SetSashPosition(self.stackManager.view.GetSize().Width)
        event.Skip()

    def OnSplitterChanging(self, event):
        if event.GetSashPosition() > self.stackManager.view.GetSize().Width:
            event.SetSashPosition(self.stackManager.view.GetSize().Width)
        self.cPanel.Refresh(True)
        event.Skip()

    def OnStackResize(self, event):
        self.splitter.SetSashPosition(self.stackManager.view.GetSize().Width)
        event.Skip()

    def OnFrameResize(self, event):
        if self.splitter.GetSashPosition() < self.stackManager.view.GetSize().Width:
            self.splitter.SetSashGravity(1.0)
        else:
            self.splitter.SetSashGravity(0.0)
            self.splitter.SetSashPosition(self.stackManager.view.GetSize().Width)
        event.Skip()

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

    def MakeMenuBar(self):
        # create the file menu
        # Using the "\tKeyName" syntax automatically creates a
        # wx.AcceleratorTable for this frame and binds the keys to
        # the menu items.
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, "&New Stack\tCtrl-N", "Create a new Stack file")
        fileMenu.Append(wx.ID_OPEN, "&Open Stack...\tCtrl-O", "Open a Stack")
        fileMenu.Append(ID_OPEN_EXAMPLE, "&Open Example...\tCtrl-Shift-O", "Open an Example Stack")
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
        editMenu.AppendSeparator()
        editMenu.Append(ID_SEARCH_IMAGE, "Insert ClipArt...\tCtrl-I", "Search clip-art web site")
        # editMenu.Append(ID_SEARCH_SOUND, "Download Sound...", "Search sound web site")
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
        alignMenu = wx.Menu()
        alignMenu.Append(ID_ALIGN_HL, "Align Left", "Align Objects Left")
        alignMenu.Append(ID_ALIGN_HC, "Align Center (Horizontal)", "Align Objects Horizontal Center")
        alignMenu.Append(ID_ALIGN_HR, "Align Right", "Align Objects Left")
        alignMenu.Append(ID_ALIGN_VT, "Align Top", "Align Objects Top")
        alignMenu.Append(ID_ALIGN_VC, "Align Center (Vertical)", "Align Objects Vertical Center")
        alignMenu.Append(ID_ALIGN_VB, "Align Bottom", "Align Objects Bottom")
        viewMenu.AppendSubMenu(alignMenu, "Align Objects...", "Align Objects")
        distMenu = wx.Menu()
        distMenu.Append(ID_DISTRIBUTE_HL, "Distribute Left", "Distribute Objects Left")
        distMenu.Append(ID_DISTRIBUTE_HC, "Distribute Center (Horizontal)", "Distribute Objects Horizontal Center")
        distMenu.Append(ID_DISTRIBUTE_HS, "Distribute Spacing (Horizontal)", "Distribute Objects Horizontal Even Spacing")
        distMenu.Append(ID_DISTRIBUTE_HR, "Distribute Right", "Distribute Objects Left")
        distMenu.Append(ID_DISTRIBUTE_VT, "Distribute Top", "Distribute Objects Top")
        distMenu.Append(ID_DISTRIBUTE_VC, "Distribute Center (Vertical)", "Distribute Objects Vertical Center")
        distMenu.Append(ID_DISTRIBUTE_VS, "Distribute Spacing (Vertical)", "Distribute Objects Vertical Even Spacing")
        distMenu.Append(ID_DISTRIBUTE_VB, "Distribute Bottom", "Distribute Objects Bottom")
        viewMenu.AppendSubMenu(distMenu, "Distribute Objects...", "Distribute Objects")
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
        # helpMenu.Append(ID_BASICS, "&Python Basics\tCtrl-Alt-P", "Python Basics")
        helpMenu.Append(wx.ID_HELP, "&Manual\tCtrl-Alt-M", "Manual")
        helpMenu.Append(wx.ID_REFRESH, "&Reference Guide\tCtrl-Alt-R", "Reference Guide")
        helpMenu.Append(wx.ID_CONTEXT_HELP, "&Show/Hide Context Help\tCtrl-Alt-C", "Toggle Context Help Window")
        helpMenu.Append(ID_SHOW_ERROR_LIST, "&Show/Hide Error List Window\tCtrl-Alt-E", "Toggle Error Window")
        helpMenu.Append(ID_SHOW_ALL_CODE, "&Show/Hide All Code Window\tCtrl-Alt-A", "Toggle AllCode Window")
        helpMenu.Append(ID_SHOW_CONSOLE, "&Show/Hide Console\tCtrl-Alt-O", "Toggle Console")


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
        self.Bind(wx.EVT_MENU, self.OnMenuOpenExample, id=ID_OPEN_EXAMPLE)
        self.Bind(wx.EVT_MENU, self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnMenuExport, id=ID_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnMenuRun, id=ID_RUN)
        self.Bind(wx.EVT_MENU, self.OnMenuRunFrom, id=ID_RUN_FROM)
        self.Bind(wx.EVT_MENU, self.OnMenuSearchImage, id=ID_SEARCH_IMAGE)
        # self.Bind(wx.EVT_MENU, self.OnMenuSearchSound, id=ID_SEARCH_SOUND)
        self.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.OnMenuAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnMenuHelp, id=wx.ID_HELP)
        # self.Bind(wx.EVT_MENU, self.OnMenuBasics, id=ID_BASICS)
        self.Bind(wx.EVT_MENU, self.OnMenuReference, id=wx.ID_REFRESH)
        self.Bind(wx.EVT_MENU, self.OnMenuContextHelp, id=wx.ID_CONTEXT_HELP)

        self.Bind(wx.EVT_MENU, self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=wx.ID_DELETE)
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
        self.Bind(wx.EVT_MENU, self.OnMenuAlign, id=ID_ALIGN_HL)
        self.Bind(wx.EVT_MENU, self.OnMenuAlign, id=ID_ALIGN_HC)
        self.Bind(wx.EVT_MENU, self.OnMenuAlign, id=ID_ALIGN_HR)
        self.Bind(wx.EVT_MENU, self.OnMenuAlign, id=ID_ALIGN_VT)
        self.Bind(wx.EVT_MENU, self.OnMenuAlign, id=ID_ALIGN_VC)
        self.Bind(wx.EVT_MENU, self.OnMenuAlign, id=ID_ALIGN_VB)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_HL)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_HC)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_HS)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_HR)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_VT)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_VC)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_VS)
        self.Bind(wx.EVT_MENU, self.OnMenuDistribute, id=ID_DISTRIBUTE_VB)
        self.Bind(wx.EVT_MENU, self.OnMenuFlipHorizontal, id=ID_FLIP_HORIZ)
        self.Bind(wx.EVT_MENU, self.OnMenuFlipVertical, id=ID_FLIP_VERT)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_FRONT)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_FWD)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_BACK)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_END)
        self.Bind(wx.EVT_MENU, self.OnMenuShowErrorList, id=ID_SHOW_ERROR_LIST)
        self.Bind(wx.EVT_MENU, self.OnMenuShowAllCodeWindow, id=ID_SHOW_ALL_CODE)
        self.Bind(wx.EVT_MENU, self.OnMenuShowConsoleWindow, id=ID_SHOW_CONSOLE)


    def MakeContextMenu(self, uiViews):
        # create a context menu for the given set of views
        contextMenu = wx.Menu()
        contextMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        contextMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        contextMenu.Append(wx.ID_DELETE,  "Delete\tDelete", "Delete Selection")

        hasGroups = False
        for ui in uiViews:
            if ui.model.type == "group":
                hasGroups = True
                break

        if len(uiViews) == 1 and uiViews[0].model.type == "card":
            contextMenu.AppendSeparator()
            contextMenu.Append(ID_DUPLICATE_CARD, "&Duplicate Card\tCtrl-Alt-+", "Duplicate Card")
            contextMenu.Append(ID_REMOVE_CARD, "&Remove Card", "Remove Card")

        if len(uiViews) > 1:
            contextMenu.AppendSeparator()
            contextMenu.Append(ID_GROUP, "&Group Objects\tCtrl-Alt-G", "Group Objects")
            if hasGroups:
                contextMenu.Append(ID_UNGROUP, "&Ungroup Objects\tCtrl-Alt-U", "Ungroup Objects")
            contextMenu.AppendSeparator()
            alignMenu = wx.Menu()
            alignMenu.Append(ID_ALIGN_HL, "Align Left", "Align Objects Left")
            alignMenu.Append(ID_ALIGN_HC, "Align Center (Horizontal)", "Align Objects Horizontal Center")
            alignMenu.Append(ID_ALIGN_HR, "Align Right", "Align Objects Left")
            alignMenu.Append(ID_ALIGN_VT, "Align Top", "Align Objects Top")
            alignMenu.Append(ID_ALIGN_VC, "Align Center (Vertical)", "Align Objects Vertical Center")
            alignMenu.Append(ID_ALIGN_VB, "Align Bottom", "Align Objects Bottom")
            contextMenu.AppendSubMenu(alignMenu, "Align Objects...", "Align Objects")
            distMenu = wx.Menu()
            distMenu.Append(ID_DISTRIBUTE_HL, "Distribute Left", "Distribute Objects Left")
            distMenu.Append(ID_DISTRIBUTE_HC, "Distribute Center (Horizontal)", "Distribute Objects Horizontal Center")
            distMenu.Append(ID_DISTRIBUTE_HS, "Distribute Spacing (Horizontal)", "Distribute Objects Horizontal Even Spacing")
            distMenu.Append(ID_DISTRIBUTE_HR, "Distribute Right", "Distribute Objects Left")
            distMenu.Append(ID_DISTRIBUTE_VT, "Distribute Top", "Distribute Objects Top")
            distMenu.Append(ID_DISTRIBUTE_VC, "Distribute Center (Vertical)", "Distribute Objects Vertical Center")
            distMenu.Append(ID_DISTRIBUTE_VS, "Distribute Spacing (Vertical)", "Distribute Objects Vertical Even Spacing")
            distMenu.Append(ID_DISTRIBUTE_VB, "Distribute Bottom", "Distribute Objects Bottom")
            contextMenu.AppendSubMenu(distMenu, "Distribute Objects...", "Distribute Objects")
        elif hasGroups:
            contextMenu.AppendSeparator()
            contextMenu.Append(ID_UNGROUP, "&Ungroup Objects\tCtrl-Alt-U", "Ungroup Objects")

        contextMenu.AppendSeparator()
        contextMenu.Append(ID_FLIP_HORIZ, "Flip Horizontal\tCtrl-Alt-H", "Flip Horizontal")
        contextMenu.Append(ID_FLIP_VERT, "Flip Vertical\tCtrl-Alt-V", "Flip Vertical")

        if len(uiViews) == 1 and uiViews[0].model.type == "card":
            contextMenu.AppendSeparator()
            contextMenu.Append(ID_MOVE_CARD_FWD, "Move Card &Forward\tCtrl-Shift-]", "Move Card Forward")
            contextMenu.Append(ID_MOVE_CARD_BACK, "Move Card Bac&k\tCtrl-Shift-[", "Move Card Back")
        else:
            contextMenu.AppendSeparator()
            contextMenu.Append(ID_MOVE_VIEW_FRONT, "Move to Front\tCtrl-Alt-Shift-F", "Move to Front")
            contextMenu.Append(ID_MOVE_VIEW_FWD, "Move &Forward\tCtrl-Alt-F", "Move Forward")
            contextMenu.Append(ID_MOVE_VIEW_BACK, "Move Bac&kward\tCtrl-Alt-B", "Move Back")
            contextMenu.Append(ID_MOVE_VIEW_END, "Move to Back\tCtrl-Alt-Shift-B", "Move to Back")

        return contextMenu

    wildcard = "CardStock files (*.cds)|*.cds"

    def OnMenuNew(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before starting a New file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        self.NewFile()
        self.SetTitle(self.title)

    def OpenFile(self, filename):
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Opening a file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)
        self.ReadFile(filename)

    def DoMenuOpen(self, initialDir):
        if wx.GetMouseState().LeftIsDown():
            return
        if self.stackManager.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Opening a file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        dlg = wx.FileDialog(self, "Open CardStock file...", defaultDir=initialDir, style=wx.FD_OPEN, wildcard=self.wildcard)

        self.stackContainer.Enable(False)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.ReadFile(filename)
        dlg.Destroy()
        wx.CallLater(50, self.stackContainer.Enable, True) # Needed to avoid a MSWindows FileDlg bug

    def OnMenuOpen(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        initialDir = os.path.expanduser('~')
        if self.configInfo and "last_open_dir" in self.configInfo:
            d = self.configInfo["last_open_dir"]
            d = os.path.join(d, '')  # Ensure a trailing slash
            if os.path.exists(d):
                initialDir = d
        self.DoMenuOpen(initialDir)

    def OnMenuOpenExample(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.DoMenuOpen(self.GetExamplesDir())

    def OnMenuSave(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        if not self.filename:
            self.OnMenuSaveAs(event)
        else:
            self.SaveFile()

    def OnMenuSaveAs(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        initialDir = os.path.expanduser('~')
        if self.configInfo and "last_open_dir" in self.configInfo:
            initialDir = self.configInfo["last_open_dir"]
            initialDir = os.path.join(initialDir, '')  # Ensure a trailing slash
        dlg = wx.FileDialog(self, "Save CardStock file as...",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           wildcard = self.wildcard)
        dlg.SetDirectory(initialDir)
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
        if wx.GetMouseState().LeftIsDown():
            return
        def doSave():
            self.OnMenuSave(None)
        exporter = StackExporter(self.stackManager)
        exporter.StartExport(doSave)

    def RunFromCard(self, cardIndex, generateThumbnail=False):
        self.stackManager.view.SetFocus()  # Blur any active property editor, to commit its new value
        wx.YieldIfNeeded()

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

        if self.consoleWindow and self.consoleWindow.IsShown():
            self.wasConsoleOpen = True
            self.consoleWindow.Hide()

        if not generateThumbnail:
            self.Hide()

        if self.stackManager.analyzer.analysisPending:
            self.stackManager.analyzer.RunAnalysis()
            while self.stackManager.analyzer.analysisPending:
                # make sure we have an up-to-date analysis and set of syntax errors
                wx.YieldIfNeeded()
                sleep(0.05)

        data = self.stackManager.stackModel.GetData()
        stackModel = StackModel(None)
        stackModel.SetData(data)

        self.viewer = ViewerFrame(self, False)
        if generateThumbnail:
            self.viewer.generateThumbnail = True
        self.viewer.designer = self

        self.viewer.PushStack(stackModel, self.filename, cardIndex)
        self.viewer.Show(not generateThumbnail)
        self.viewer.Refresh()
        self.isStartingViewer = False

    def OnMenuEditStack(self, event):
        self.stackManager.SelectUiView(self.stackManager.uiStack)

    def OnMenuRun(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.RunFromCard(0)

    def OnMenuRunFrom(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.RunFromCard(self.stackManager.cardIndex)

    def OnMenuSearchImage(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        if not self.stackManager.filename:
            r = wx.MessageDialog(self.stackManager.designer,
                                 "You need to save this stack before inserting Clip Art.",
                                 "Save now?", wx.OK | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            elif r == wx.ID_OK:
                self.OnMenuSave(None)
                if not self.stackManager.filename:
                    return

        def onImageLoaded(path):
            self.stackManager.AddImageFromPath(path)

        dlg = mediaSearchDialogs.ImageSearchDialog(self, self.GetCurDir(), onImageLoaded)
        dlg.RunModal()

    # def OnMenuSearchSound(self, event):
    #     dlg = mediaWebDialogs.AudioSearchDialog(self, self.GetCurDir(), None)
    #     dlg.RunModal()

    def OnViewerSave(self, stackModel):
        newModel = StackModel(self.stackManager)
        newModel.SetData(stackModel.GetData())
        self.stackManager.SetStackModel(newModel)
        self.stackManager.LoadCardAtIndex(0)

    def OnRunnerFinished(self, runner):
        self.lastRunErrors = runner.errors
        self.viewer = None
        ImageFactory.shared().ClearCache()
        self.Show()
        self.Refresh()
        self.Update()
        # wx.CallLater(500, self.UpdateGC_Data)

        if self.wasConsoleOpen:
            self.wasConsoleOpen = False
            self.consoleWindow.Show()

        if len(self.lastRunErrors):
            self.OnMenuShowErrorList(None)

        if self.runnerFinishedCallback:
            self.runnerFinishedCallback()

    # def UpdateGC_Data(self):
    #     gc.collect()
    #     stats = {}
    #     for o in gc.get_objects():
    #         if type(o) in stats:
    #             stats[type(o)] += 1
    #         else:
    #             stats[type(o)] = 1
    #     for k,v in stats.items():
    #         lastV = 0
    #         if k in self.lastStats:
    #             lastV = self.lastStats[k]
    #         if v != lastV:
    #             print(f"{v}: {k} (+{v-lastV})")
    #     print("")
    #     self.lastStats = stats

    def OnMenuShowErrorList(self, event):
        if self.errorListWindow:
            if self.errorListWindow.IsShown():
                self.errorListWindow.Hide()
            else:
                self.errorListWindow.Show()
                self.errorListWindow.Raise()
        else:
            self.errorListWindow = ErrorListWindow(self)
            self.errorListWindow.SetPosition(self.GetPosition() + (100, 10))
            self.errorListWindow.Show()
            self.errorListWindow.Raise()
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
                self.allCodeWindow.Raise()
        else:
            self.allCodeWindow = AllCodeWindow(self)
            self.allCodeWindow.SetPosition(self.GetPosition() + (50, 100))
            self.allCodeWindow.UpdateCode()
            self.allCodeWindow.Show()
            self.allCodeWindow.Raise()
            self.allCodeWindow.Bind(wx.EVT_CLOSE, self.OnAllCodeWindowClose)

    def OnAllCodeWindowClose(self, event):
        self.allCodeWindow.Hide()
        self.allCodeWindow.Clear()

    def OnMenuShowConsoleWindow(self, event):
        if not self.consoleWindow:
            self.consoleWindow = ConsoleWindow(self, allowInput=True)
            self.stackManager.runner = Runner(self.stackManager, None)
            self.consoleWindow.runner = self.stackManager.runner
            self.MakeConsoleMenuBar()
            self.consoleWindow.funcBeforeCode = self.OnPreConsoleRun
            self.consoleWindow.funcAfterCode = self.OnPostConsoleRun

            self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)

        if self.consoleWindow.IsShown():
            self.consoleWindow.Hide()
        else:
            self.consoleWindow.Show()
            self.consoleWindow.Raise()

    def MakeConsoleMenuBar(self):
        # create the file menu
        fileMenu = wx.Menu()
        fileMenu.Append(ID_SHOW_CONSOLE, "&Close\tCtrl-W", "Close Console")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_RUN, "&Run Stack\tCtrl-R", "Run the current Stack")
        fileMenu.Append(ID_RUN_FROM, "&Run From Current Card\tCtrl-Shift-R", "Run from the current Card")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")

        # and the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(ID_SHOW_CONSOLE, "&Hide Console\tCtrl-Alt-O", "Toggle Console")
        helpMenu.Append(ID_CLEAR_CONSOLE, "&Clear Console\tCtrl-Alt-C", "Clear Console")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.consoleWindow.SetMenuBar(menuBar)

        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuConsoleClose, id=wx.ID_CLOSE)
        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuRun, id=ID_RUN)
        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuRunFrom, id=ID_RUN_FROM)

        self.consoleWindow.Bind(wx.EVT_MENU, self.consoleWindow.DoUndo, id=wx.ID_UNDO)
        self.consoleWindow.Bind(wx.EVT_MENU, self.consoleWindow.DoRedo, id=wx.ID_REDO)

        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuShowConsoleWindow, id=ID_SHOW_CONSOLE)
        self.consoleWindow.Bind(wx.EVT_MENU, self.OnMenuClearConsoleWindow, id=ID_CLEAR_CONSOLE)

    @RunOnMainSync
    def OnPreConsoleRun(self):
        index = self.stackManager.cardIndex
        self.console_run_model_pre = self.stackManager.stackModel
        self.console_run_dirty_pre = self.stackManager.stackModel.GetDirty()
        data = self.stackManager.stackModel.GetData()
        newModel = StackModel(self.stackManager)
        newModel.SetData(data)
        self.stackManager.SetStackModel(newModel, skipSetDown=True)
        self.stackManager.stackModel.SetDirty(False)
        self.stackManager.LoadCardAtIndex(index, reload=True)

    @RunOnMainSync
    def OnPostConsoleRun(self):
        if self.stackManager.stackModel.GetDirty():
            command = RunConsoleCommand(True, "Console Command", self.stackManager,
                                         self.console_run_model_pre, self.stackManager.stackModel)
            self.stackManager.command_processor.Submit(command)
        else:
            index = self.stackManager.cardIndex
            oldModel = self.stackManager.stackModel
            self.stackManager.SetStackModel(self.console_run_model_pre, skipSetDown=True)
            self.stackManager.LoadCardAtIndex(index, reload=True)
            self.stackManager.stackModel.SetDirty(self.console_run_dirty_pre)
            oldModel.SetDown()
        del self.console_run_model_pre
        del self.console_run_dirty_pre


    def OnMenuConsoleClose(self, event):
        self.consoleWindow.Hide()

    def OnMenuClearConsoleWindow(self, event):
        self.consoleWindow.Clear()

    def OnMenuExit(self, event):
        self.Close()

    def OnClose(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
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
        if self.consoleWindow:
            self.stackManager.runner.CleanupFromRun()
            self.consoleWindow.Close()
        event.Skip()

    def OnMenuGroup(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.stackManager.GroupSelectedViews()

    def OnMenuUngroup(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.stackManager.UngroupSelectedViews()

    def OnMenuAlign(self, event):
        id = event.GetId()
        dir = ""
        if id == ID_ALIGN_HL: dir = "Left"
        elif id == ID_ALIGN_HC: dir = "HCenter"
        elif id == ID_ALIGN_HR: dir = "Right"
        elif id == ID_ALIGN_VT: dir = "Top"
        elif id == ID_ALIGN_VC: dir = "VCenter"
        elif id == ID_ALIGN_VB: dir = "Bottom"
        self.stackManager.AlignOrDistributeSelectedViews(True, dir)

    def OnMenuDistribute(self, event):
        id = event.GetId()
        dir = ""
        if id == ID_DISTRIBUTE_HL: dir = "Left"
        elif id == ID_DISTRIBUTE_HC: dir = "HCenter"
        elif id == ID_DISTRIBUTE_HS: dir = "HSpacing"
        elif id == ID_DISTRIBUTE_HR: dir = "Right"
        elif id == ID_DISTRIBUTE_VT: dir = "Top"
        elif id == ID_DISTRIBUTE_VC: dir = "VCenter"
        elif id == ID_DISTRIBUTE_VS: dir = "VSpacing"
        elif id == ID_DISTRIBUTE_VB: dir = "Bottom"
        self.stackManager.AlignOrDistributeSelectedViews(False, dir)

    def OnMenuFlipHorizontal(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.stackManager.FlipSelection(True)

    def OnMenuFlipVertical(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.stackManager.FlipSelection(False)

    def OnMenuMoveView(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        if event.GetId() == ID_MOVE_VIEW_FRONT:
            self.stackManager.ReorderSelectedViews("front")
        elif event.GetId() == ID_MOVE_VIEW_FWD:
            self.stackManager.ReorderSelectedViews("fwd")
        elif event.GetId() == ID_MOVE_VIEW_BACK:
            self.stackManager.ReorderSelectedViews("back")
        elif event.GetId() == ID_MOVE_VIEW_END:
            self.stackManager.ReorderSelectedViews("end")

    def OnMenuMoveCard(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        if event.GetId() == ID_MOVE_CARD_FWD:
            self.stackManager.ReorderCurrentCard("fwd")
        elif event.GetId() == ID_MOVE_CARD_BACK:
            self.stackManager.ReorderCurrentCard("back")

    def OnMenuNextCard(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        index = self.stackManager.cardIndex+1
        if index < len(self.stackManager.stackModel.childModels):
            self.stackManager.LoadCardAtIndex(index)

    def OnMenuPrevCard(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        index = self.stackManager.cardIndex-1
        if index >= 0:
            self.stackManager.LoadCardAtIndex(index)

    def OnMenuAddCard(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.stackManager.AddCard()

    def OnMenuDuplicateCard(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        self.stackManager.DuplicateCard()

    def OnMenuRemoveCard(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
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
        self.cardPicker.Fit()

        if wx.Platform == "__WXMAC__":
            self.toolbar.RemoveTool(self.cardPickerToolId)

        # Update toolbar to show 'Run This Card' only when on card 2+
        isShowingTool = self.toolbar.FindById(ID_RUN_FROM)
        if not isShowingTool and self.stackManager.cardIndex > 0:
            icn = embeddedImages.run_card.GetBitmap()
            self.toolbar.InsertTool(1, ID_RUN_FROM, 'Run This Card', icn, wx.NullBitmap)
        elif isShowingTool and self.stackManager.cardIndex == 0:
            self.toolbar.RemoveTool(ID_RUN_FROM)

        if wx.Platform == "__WXMAC__":
            self.cardPickerToolId = self.toolbar.InsertControl(2 if (self.stackManager.cardIndex == 0) else 3, self.cardPicker).GetId()
        self.toolbar.Realize()

    def OnStackContainerFocus(self, event):
        self.stackManager.view.SetFocus()

    def GetDesiredFocus(self, allowEditors):
        f = self.FindFocus()
        if allowEditors:
            views = [self, self.stackContainer, self.stackManager.view, self.splitter, self.cPanel]
            if not f or f in views:
                f = self.stackManager
        else:
            views = [self, self.stackContainer, self.stackManager.view, self.cPanel, self.splitter, self.cPanel.inspector]
            if not f or f in views or isinstance(f, (PythonEditor, wx.lib.buttons.GenBitmapToggleButton)):
                f = self.stackManager
        return f

    def OnSelectAll(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "SelectAll"):
            f.SelectAll()

    def OnCut(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Cut"):
            f.Cut()

    def OnDelete(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Delete"):
            f.Delete()

    def OnCopy(self, event):
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Copy"):
            f.Copy()

    def OnPaste(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        f = self.GetDesiredFocus(True)
        if f and hasattr(f, "Paste"):
            f.Paste()

    def OnUndo(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        f = self.GetDesiredFocus(False)
        if f and hasattr(f, "Undo"):
            if not hasattr(f, "CanUndo") or f.CanUndo():
                f.Undo()
                return
        event.Skip()

    def OnRedo(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
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
        if wx.GetMouseState().LeftIsDown():
            return
        flags = self.findEngine.findData.GetFlags()
        self.findEngine.findData.SetFlags(flags | 1)
        self.findEngine.Find()
        self.findEngine.findData.SetFlags(flags)

    def OnMenuFindPrevious(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
        flags = self.findEngine.findData.GetFlags()
        self.findEngine.findData.SetFlags(flags & ~1)
        self.findEngine.Find()
        self.findEngine.findData.SetFlags(flags)

    def OnFindEvent(self, event):
        self.findEngine.Find()

    def OnReplaceEvent(self, event):
        self.findEngine.Replace()

    def OnReplaceAllEvent(self, event):
        if wx.GetMouseState().LeftIsDown():
            return
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

    def UpdateStatusBar(self, uiView, pos):
        sb = self.GetStatusBar()
        posStr = f"({pos.x}, {pos.y})" if pos else ""
        objStr = f"{uiView.model.GetDisplayType()}: '{uiView.model.GetProperty('name')}'" if uiView else ""
        sb.SetStatusText(posStr, 0)
        sb.SetStatusText(objStr, 1)

    def FinishedStarting(self):
        if not self.filename:
            self.cPanel.ShowContextHelp(self.configInfo["show_context_help"])
            if self.configInfo["last_open_file"] and os.path.exists(self.configInfo["last_open_file"]):
                self.ReadFile(self.configInfo["last_open_file"])
            else:
                self.NewFile()

    def GetCurDir(self):
        cur_dir = None
        if self.configInfo and "last_open_file" in self.configInfo:
            cur_dir = os.path.dirname(self.configInfo["last_open_file"])
        return cur_dir

    def WriteDefaultConfig(self):
        config = configparser.ConfigParser()
        self.configInfo = {"last_open_file": os.path.join(self.GetExamplesDir(), "Welcome.cds"),
                           "last_open_dir": os.path.expanduser('~'),
                           "show_context_help": str(True),
                           "upload_username": "",
                           "upload_token": "",
                           "cardstock_app_version": version.VERSION}
        config['User'] = self.configInfo
        with open(self.full_config_file_path, 'w') as configfile:
            config.write(configfile)

    def WriteConfig(self):
        config = configparser.ConfigParser()
        last_file = self.filename if self.filename else ""
        last_dir = os.path.dirname(self.filename)
        if last_dir and os.path.samefile(last_dir, self.GetExamplesDir()):
            # Don't save example stacks as the last open dir
            if "last_open_dir" in self.configInfo:
                last_dir = self.configInfo["last_open_dir"]
                if not last_dir:
                    last_dir = os.path.expanduser('~')
        self.configInfo = {"last_open_file": last_file,
                           "last_open_dir": last_dir,
                           "show_context_help": str(self.cPanel.IsContextHelpShown()),
                           "upload_username": self.configInfo["upload_username"] or "",
                           "upload_token": self.configInfo["upload_token"] or "",
                           "cardstock_app_version": version.VERSION}
        config['User'] = self.configInfo
        with open(self.full_config_file_path, 'w') as configfile:
            config.write(configfile)

    def GetExamplesDir(self):
        def welcomeExistsHere(path):
            return os.path.exists(os.path.join(path, os.path.join("examples", "Welcome.cds")))

        base_dir = os.path.dirname(__file__)
        if not welcomeExistsHere(base_dir):
            base_dir = os.path.dirname(os.path.dirname(__file__))
            if not welcomeExistsHere(base_dir):
                base_dir = os.path.dirname(sys.executable)
                if not welcomeExistsHere(base_dir) and hasattr(sys, "_MEIPASS"):
                    base_dir = sys._MEIPASS
                    if not welcomeExistsHere(base_dir):
                        return None

        return os.path.abspath(os.path.join(base_dir, "examples"))

    def ReadConfig(self):
        last_open_file = None
        show_context_help = True
        cardstock_app_version = "0"
        if not os.path.exists(self.full_config_file_path) \
                or os.stat(self.full_config_file_path).st_size == 0:
            self.WriteDefaultConfig()
        if os.path.exists(self.full_config_file_path) and os.stat(self.full_config_file_path).st_size > 0:
            config = configparser.ConfigParser()
            config.read(self.full_config_file_path)
            last_open_file = config['User'].get('last_open_file', None)
            last_open_dir = config['User'].get('last_open_dir', None)
            upload_username = config['User'].get('upload_username', None)
            upload_token = config['User'].get('upload_token', None)
            show_context_help = config['User'].get('show_context_help', "True") == "True"
            cardstock_app_version = config['User'].get('cardstock_app_version', "0")

        return {"last_open_file": last_open_file,
                "last_open_dir": last_open_dir,
                "show_context_help": show_context_help,
                "upload_username": upload_username,
                "upload_token": upload_token,
                "cardstock_app_version": cardstock_app_version}

# ----------------------------------------------------------------------


class DesignerApp(wx.App):
    def OnInit(self):
        self.argFilename = None
        self.doneStarting = False
#        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        import locale
        locale.setlocale(locale.LC_ALL, "C")
        self.locale = wx.Locale()
        self.frame = DesignerFrame(None)
        self.frame.app = self
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        self.SetAppDisplayName('CardStock')
        return True

    def MacOpenFile(self, filename):
        self.argFilename = filename
        if self.doneStarting:
            self.frame.OpenFile(self.argFilename)

    def MacReopenApp(self):
        """
        Restore the main frame (if it's minimized) when the Dock icon is
        clicked on OSX.
        """
        top = self.GetTopWindow()
        if top.IsShown():
            if top and top.IsIconized():
                top.Iconize(False)
            if top:
                top.Raise()
        elif self.frame.viewer:
            if self.frame.viewer.IsIconized():
                self.frame.viewer.Iconize(False)
            self.frame.viewer.Raise()

# ----------------------------------------------------------------------


def RunDesigner():
    app = DesignerApp(redirect=False)

    if len(sys.argv) > 1 and not app.argFilename:
        app.argFilename = sys.argv[1]

    if app.argFilename:
        app.frame.ReadFile(app.argFilename)

    app.frame.FinishedStarting()
    app.doneStarting = True
    app.argFilename = None
    # import wx.lib.inspection
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == '__main__':
    if wx.Platform == "__WXMSW__":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        except:
            pass

    RunDesigner()
