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
from tools import *
from stackWindow import StackWindow
from controlPanel import ControlPanel
from viewer import ViewerFrame
import helpDialogs
from stackModel import StackModel
from uiCard import CardModel
from findEngineDesigner import FindEngine
from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.realpath(__file__))

# ----------------------------------------------------------------------

ID_RUN = wx.NewIdRef()
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
ID_MOVE_VIEW_FRONT = wx.NewIdRef()
ID_MOVE_VIEW_FWD = wx.NewIdRef()
ID_MOVE_VIEW_BACK = wx.NewIdRef()
ID_MOVE_VIEW_END = wx.NewIdRef()


class DesignerFrame(wx.Frame):
    """
    A stackFrame contains a stackWindow and a ControlPanel and manages
    their layout with a wx.BoxSizer.  A menu and associated event handlers
    provides for saving a stackView to a file, etc.
    """
    title = "CardStock"

    def __init__(self, parent):
        config_folder = os.path.join(os.path.expanduser("~"), '.config')
        os.makedirs(config_folder, exist_ok=True)
        settings_file = "cardstock.conf"
        self.full_config_file_path = os.path.join(config_folder, settings_file)

        super().__init__(parent, -1, self.title, size=(800,600), style=wx.DEFAULT_FRAME_STYLE)
        # self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/stack.png')))
        self.CreateStatusBar()
        self.editMenu = None
        self.MakeMenu()
        self.filename = None
        self.app = None

        toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        toolbar.AddTool(ID_RUN, 'Run', wx.ArtProvider.GetBitmap(wx.ART_FULL_SCREEN), wx.NullBitmap)

        toolbar.AddStretchableSpace()

        self.cardPicker = wx.Choice(parent=toolbar, choices=["Card 1", "Card 2"], size=(200,20))
        self.cardPicker.Bind(wx.EVT_CHOICE, self.OnPickCard)
        toolbar.AddControl(self.cardPicker)

        toolbar.AddTool(ID_ADD_CARD, 'Add Card', wx.ArtProvider.GetBitmap(wx.ART_PLUS), wx.NullBitmap)

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
        self.stackView = StackWindow(self.stackContainer, -1, None)
        self.stackView.SetDesigner(self)

        self.stackView.command_processor.SetEditMenu(self.editMenu)
        self.stackContainer.Bind(wx.EVT_LEFT_DOWN, self.FwdOnMouseDown)
        self.stackContainer.Bind(wx.EVT_LEFT_DCLICK, self.FwdOnMouseDown)
        self.stackContainer.Bind(wx.EVT_MOVE, self.FwdOnMouseMove)
        self.stackContainer.Bind(wx.EVT_LEFT_UP, self.FwdOnMouseDown)
        self.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

        self.cPanel = ControlPanel(self.splitter, -1, self.stackView)
        self.cPanel.Bind(wx.EVT_KEY_DOWN, self.FwdOnKeyDown)
        self.cPanel.Bind(wx.EVT_KEY_UP, self.FwdOnKeyUp)

        self.splitter.SplitVertically(self.stackContainer, self.cPanel)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(self.splitter.GetSize()[0]-600)
        self.splitter.SetSashGravity(0.0)

        self.cPanel.SetSize([600,600])
        self.cPanel.Layout()

        self.cPanel.SetToolByName("hand")

        self.findDlg = None
        self.findEngine = FindEngine(self.stackView)

        self.viewer = None
        self.NewFile()

    def NewFile(self):
        self.filename = None
        stackModel = StackModel(self.stackView)
        newCard = CardModel(self.stackView)
        newCard.SetProperty("name", newCard.DeduplicateName("card_1",
                                                            [m.GetProperty("name") for m in stackModel.childModels]), False)
        stackModel.AppendCardModel(newCard)
        self.stackView.SetStackModel(stackModel)
        self.stackView.SetEditing(True)
        self.Layout()
        stackModel.SetProperty("size", self.stackView.GetSize())
        self.stackView.stackModel.SetDirty(False)
        self.stackView.SelectUiView(self.stackView.uiCard)
        self.stackView.SetFocus()
        self.SetFrameSizeFromModel()
        self.UpdateCardList()

    def SaveFile(self):
        if self.filename:
            data = self.stackView.stackModel.GetData()
            try:
                jsonData = json.dumps(data, indent=2)
                with open(self.filename, 'w') as f:
                    f.write(jsonData)
                self.stackView.stackModel.SetDirty(False)
            except TypeError:
                # e = sys.exc_info()
                # print(e)
                wx.MessageDialog(None, str("Couldn't save file"), "", wx.OK).ShowModal()

    def ReadFile(self, filename):
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                if data:
                    stackModel = StackModel(self.stackView)
                    stackModel.SetData(data)
                    self.stackView.SetDesigner(self)
                    self.filename = filename
                    self.stackView.filename = filename
                    self.stackView.SetStackModel(stackModel)
                    self.stackView.SetEditing(True)
                    self.stackView.SelectUiView(self.stackView.uiCard)
                    self.SetFrameSizeFromModel()
                    self.UpdateCardList()
                    self.stackView.SetFocus()
                    self.SetTitle(self.title + ' -- ' + self.filename)
                    self.WriteConfig()
                    self.cPanel.SetToolByName("hand")
            except:
                # e = sys.exc_info()
                # print(e)
                wx.MessageDialog(None, str("Couldn't read file"), "", wx.OK).ShowModal()


    def SetFrameSizeFromModel(self):
        self.stackContainer.SetSize(self.stackView.GetSize())
        clientSize = (self.stackView.GetSize().Width + self.splitter.GetSashSize() + self.cPanel.GetSize().Width,
                      self.stackView.GetSize().Height)
        self.splitter.SetSize(clientSize)
        self.SetClientSize(clientSize)
        self.splitter.SetSashPosition(self.stackView.GetSize().Width)

    def SetSelectedUiViews(self, views):
        self.cPanel.UpdateForUiViews(views)

    def UpdateSelectedUiViews(self):
        self.cPanel.UpdateInspectorForUiViews(self.stackView.GetSelectedUiViews())
        self.cPanel.UpdateHandlerForUiViews(self.stackView.GetSelectedUiViews(), None)

    def FwdOnMouseDown(self, event):
        self.stackView.OnMouseDown(self.stackView.uiCard, event)

    def FwdOnMouseMove(self, event):
        self.stackView.OnMouseMove(self.stackView.uiCard, event)

    def FwdOnMouseUp(self, event):
        self.stackView.OnMouseUp(self.stackView.uiCard, event)

    def FwdOnKeyDown(self, event):
        self.stackView.OnKeyDown(None, event)

    def FwdOnKeyUp(self, event):
        self.stackView.OnKeyUp(None, event)

    def MakeMenu(self):
        # create the file menu
        # Using the "\tKeyName" syntax automatically creates a
        # wx.AcceleratorTable for this frame and binds the keys to
        # the menu items.
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, "&New Card\tCtrl-N", "Create a new file")
        fileMenu.Append(wx.ID_OPEN, "&Open\tCtrl-O", "Open a Stack")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save the Stack")
        fileMenu.Append(wx.ID_SAVEAS, "Save &As", "Save the Stack in a new file")
        fileMenu.AppendSeparator()
        fileMenu.Append(ID_RUN, "&Run Stack\tCtrl-R", "Run the current Stack")
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
        cardMenu.Append(ID_DUPLICATE_CARD, "&Duplicate Card", "Duplicate Card")
        cardMenu.Append(ID_REMOVE_CARD, "&Remove Card", "Remove Card")
        cardMenu.AppendSeparator()
        cardMenu.Append(ID_MOVE_CARD_FWD, "Move Card &Forward\tCtrl-Shift-]", "Move Card Forward")
        cardMenu.Append(ID_MOVE_CARD_BACK, "Move Card Bac&k\tCtrl-Shift-[", "Move Card Back")

        viewMenu = wx.Menu()
        viewMenu.Append(ID_GROUP, "&Group Objects\tCtrl-3", "Group Objects")
        viewMenu.Append(ID_UNGROUP, "&Ungroup Objects\tCtrl-Shift-3", "Ungroup Objects")
        viewMenu.AppendSeparator()
        viewMenu.Append(ID_MOVE_VIEW_FRONT, "Move to Front\tCtrl-Shift-1", "Move to Front")
        viewMenu.Append(ID_MOVE_VIEW_FWD, "Move &Forward\tCtrl-1", "Move Forward")
        viewMenu.Append(ID_MOVE_VIEW_BACK, "Move Bac&k\tCtrl-2", "Move Back")
        viewMenu.Append(ID_MOVE_VIEW_END, "Move to Back\tCtrl-Shift-2", "Move to Back")

        # and the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "&About", "About")
        helpMenu.Append(wx.ID_HELP, "&Manual", "Manual")
        helpMenu.Append(wx.ID_REFRESH, "&Reference", "Reference")
        helpMenu.Append(wx.ID_CONTEXT_HELP, "&Show/Hide Context Help", "Toggle Context Help")

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
        self.Bind(wx.EVT_MENU, self.OnMenuRun, id=ID_RUN)
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
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_FRONT)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_FWD)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_BACK)
        self.Bind(wx.EVT_MENU, self.OnMenuMoveView, id=ID_MOVE_VIEW_END)


    wildcard = "CardStock files (*.cds)|*.cds|All files (*.*)|*.*"

    def OnMenuNew(self, event):
        if self.stackView.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before starting a New file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        self.NewFile()
        self.SetTitle(self.title)

    def OnMenuOpen(self, event):
        if self.stackView.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Opening a file?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        dlg = wx.FileDialog(self, "Open CardStock file...", os.getcwd(),
                           style=wx.FD_OPEN, wildcard = self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.ReadFile(filename)
        dlg.Destroy()

    def OnMenuSave(self, event):
        if not self.filename:
            self.OnMenuSaveAs(event)
        else:
            self.SaveFile()

    def OnMenuSaveAs(self, event):
        dlg = wx.FileDialog(self, "Save CaardStock file as...", os.getcwd(),
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           wildcard = self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.cds'
            self.filename = filename
            self.stackView.filename = filename
            self.SaveFile()
            self.SetTitle(self.title + ' -- ' + self.filename)
            self.WriteConfig()
        dlg.Destroy()

    def OnMenuRun(self, event):
        if self.viewer:
            self.viewer.Destroy()

        data = self.stackView.stackModel.GetData()
        stackModel = StackModel(None)
        stackModel.SetData(data)

        self.viewer = ViewerFrame(self, stackModel, self.filename)
        self.viewer.designer = self

        self.viewer.Bind(wx.EVT_CLOSE, self.OnViewerClose)
        self.viewer.RunViewer()
        self.viewer.Show(True)
        self.Hide()

    def OnViewerSave(self, stackModel):
        newModel = StackModel(self.stackView)
        newModel.SetData(stackModel.GetData())
        self.stackView.SetStackModel(newModel)

    def OnViewerClose(self, event):
        self.viewer.Destroy()
        self.viewer = None
        self.Show()

    def OnMenuExit(self, event):
        if self.stackView.stackModel.GetDirty():
            r = wx.MessageDialog(None, "There are unsaved changes. Do you want to Save first?",
                                 "Save before Quitting?", wx.YES_NO | wx.CANCEL).ShowModal()
            if r == wx.ID_CANCEL:
                return
            if r == wx.ID_YES:
                self.OnMenuSave(None)

        if self.viewer:
            self.viewer.Destroy()

        self.Close()

    def OnMenuGroup(self, event):
        self.stackView.GroupSelectedViews()

    def OnMenuUngroup(self, event):
        self.stackView.UngroupSelectedViews()

    def OnMenuMoveView(self, event):
        if event.GetId() == ID_MOVE_VIEW_FRONT:
            self.stackView.ReorderSelectedViews("front")
        elif event.GetId() == ID_MOVE_VIEW_FWD:
            self.stackView.ReorderSelectedViews("fwd")
        elif event.GetId() == ID_MOVE_VIEW_BACK:
            self.stackView.ReorderSelectedViews("back")
        elif event.GetId() == ID_MOVE_VIEW_END:
            self.stackView.ReorderSelectedViews("end")

    def OnMenuMoveCard(self, event):
        if event.GetId() == ID_MOVE_CARD_FWD:
            self.stackView.ReorderCurrentCard("fwd")
        elif event.GetId() == ID_MOVE_CARD_BACK:
            self.stackView.ReorderCurrentCard("back")

    def OnMenuNextCard(self, event):
        index = self.stackView.cardIndex+1
        if index < len(self.stackView.stackModel.childModels):
            self.stackView.LoadCardAtIndex(index)

    def OnMenuPrevCard(self, event):
        index = self.stackView.cardIndex-1
        if index >= 0:
            self.stackView.LoadCardAtIndex(index)

    def OnMenuAddCard(self, event):
        self.stackView.AddCard()

    def OnMenuDuplicateCard(self, event):
        self.stackView.DuplicateCard()

    def OnMenuRemoveCard(self, event):
        self.stackView.RemoveCard()

    def OnPickCard(self, event):
        self.stackView.LoadCardAtIndex(event.GetSelection())

    def UpdateCardList(self):
        choices = []
        i = 1
        numCards = len(self.stackView.stackModel.childModels)
        for m in self.stackView.stackModel.childModels:
            choices.append(f"Card {i} of {numCards}: {m.GetProperty('name')}")
            i += 1
        self.cardPicker.SetItems(choices)
        self.cardPicker.SetSelection(self.stackView.cardIndex)

    def OnStackContainerFocus(self, event):
        self.stackView.SetFocus()

    def GetDesiredFocus(self):
        f = self.FindFocus()
        if f == self.cPanel.inspector: f = self.stackView
        if f == self.cPanel.codeEditor: f = self.stackView
        return f

    def OnSelectAll(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.SelectAll()
        elif f and hasattr(f, "SelectAll"):
            f.SelectAll()

    def OnCut(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.CutSelectedViews()
        elif f and hasattr(f, "Cut"):
            f.Cut()

    def OnCopy(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.CopySelectedViews()
        elif f and hasattr(f, "Copy"):
            f.Copy()

    def OnPaste(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.PasteViews()
        elif f and hasattr(f, "Paste"):
            f.Paste()

    def OnUndo(self, event):
        f = self.GetDesiredFocus()
        if f == self.splitter: f = self.stackView
        if f and hasattr(f, "Undo"):
            if not hasattr(f, "CanUndo") or f.CanUndo():
                f.Undo()
                return
        event.Skip()

    def OnRedo(self, event):
        f = self.GetDesiredFocus()
        if f == self.splitter: f = self.stackView
        if f == self.cPanel.codeEditor: f = self.stackView
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
            if config["last_open_file"]:
                self.ReadFile(config["last_open_file"])
            self.cPanel.ShowContextHelp(config["show_context_help"] == "True")

    def WriteConfig(self):
        config = configparser.ConfigParser()
        config['User'] = {"last_open_file": self.filename if self.filename else "",
                          "show_context_help": str(self.cPanel.IsContextHelpShown())}
        with open(self.full_config_file_path, 'w') as configfile:
            config.write(configfile)

    def ReadConfig(self):
        last_open_file = None
        context_help = "True"
        if not os.path.exists(self.full_config_file_path) \
                or os.stat(self.full_config_file_path).st_size == 0:
            self.WriteConfig()
        if os.path.exists(self.full_config_file_path) and os.stat(self.full_config_file_path).st_size > 0:
            config = configparser.ConfigParser()
            config.read(self.full_config_file_path)
            last_open_file = config['User'].get('last_open_file', None)
            context_help = config['User'].get('show_context_help', "True")
        return {"last_open_file": last_open_file, "show_context_help": context_help}

# ----------------------------------------------------------------------


class DesignerApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init() # for InspectionMixin

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
    app.MainLoop()
