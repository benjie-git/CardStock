# designer.py
"""
This module implements the PyStackDesigner application.  It takes the
StackWindow and reuses it in a much more
intelligent Frame.  This one has a menu and a statusbar, is able to
save and reload stacks, clear the workspace, and has a simple control
panel for setting color and line thickness in addition to the popup
menu that StackWindow provides.  There is also a nice About dialog
implemented using an wx.html.HtmlWindow.
"""

import os
import sys
import json
import wx
import wx.html
from tools import *
from stackWindow import StackWindow
from controlPanel import ControlPanel
from viewer import ViewerFrame
import version
from stack import StackModel
from uiCard import CardModel

from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------

ID_RUN = wx.NewIdRef()
ID_EDIT = wx.NewIdRef()
ID_NEXT_CARD = wx.NewIdRef()
ID_PREV_CARD = wx.NewIdRef()
ID_ADD_CARD = wx.NewIdRef()
ID_DUPLICATE_CARD = wx.NewIdRef()
ID_REMOVE_CARD = wx.NewIdRef()
ID_MOVE_CARD_FWD = wx.NewIdRef()
ID_MOVE_CARD_BACK = wx.NewIdRef()
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
        wx.Frame.__init__(self, parent, -1, self.title, size=(800,600),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/mondrian.ico')))
        self.CreateStatusBar()
        self.editMenu = None
        self.MakeMenu()
        self.filename = None
        self.app = None

        toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        toolbar.AddTool(ID_RUN, 'Run', wx.ArtProvider.GetBitmap(wx.ART_FULL_SCREEN), wx.NullBitmap)

        toolbar.AddStretchableSpace()

        self.cardPicker = wx.Choice(parent=toolbar, id=wx.ID_ANY, choices=["Card 1", "Card 2"], size=(200,20))
        self.cardPicker.Bind(wx.EVT_CHOICE, self.OnPickCard)
        toolbar.AddControl(self.cardPicker)

        toolbar.AddTool(ID_ADD_CARD, 'Add Card', wx.ArtProvider.GetBitmap(wx.ART_PLUS), wx.NullBitmap)

        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnMenuRun, id=ID_RUN)

        self.splitter = wx.SplitterWindow(self, id=wx.ID_ANY, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        stackModel = StackModel()
        stackModel.AppendCardModel(CardModel())
        self.stackContainer = wx.Window(self.splitter)
        self.stackContainer.SetBackgroundColour("#E0E0E0")
        self.stackContainer.Bind(wx.EVT_SET_FOCUS, self.OnStackContainerFocus)
        self.stackView = StackWindow(self.stackContainer, -1, stackModel)
        self.stackView.SetDesigner(self)

        self.stackView.command_processor.SetEditMenu(self.editMenu)

        self.cPanel = ControlPanel(self.splitter, -1, self.stackView)

        self.splitter.SplitVertically(self.stackContainer, self.cPanel)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(self.splitter.GetSize()[0]-400)
        self.splitter.SetSashGravity(1.0)

        self.cPanel.SetSize([400,400])
        self.cPanel.Layout()

        self.cPanel.SetToolByName("hand")

        self.viewer = None
        self.NewFile()

    def NewFile(self):
        self.filename = None
        stackModel = StackModel()
        newCard = CardModel()
        newCard.SetProperty("name", newCard.DeduplicateName("card_1",
                                                            [m.GetProperty("name") for m in stackModel.cardModels]))
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

            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.stackView.stackModel.SetDirty(False)

    def ReadFile(self):
        if self.filename:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            if data:
                stackModel = StackModel()
                stackModel.SetData(data)
                self.stackView.SetDesigner(self)
                self.stackView.SetStackModel(stackModel)
                self.stackView.SetEditing(True)
                self.stackView.SelectUiView(self.stackView.uiCard)
                self.SetFrameSizeFromModel()
                self.UpdateCardList()
                self.stackView.SetFocus()

    def SetFrameSizeFromModel(self):
        self.stackContainer.SetSize(self.stackView.GetSize())
        clientSize = (self.stackView.GetSize().Width + self.splitter.GetSashSize() + self.cPanel.GetSize().Width,
                      self.stackView.GetSize().Height)
        self.splitter.SetSize(clientSize)
        self.SetClientSize(clientSize)

    def SetSelectedUiView(self, view):
        self.cPanel.UpdateForUiView(view)

    def UpdateSelectedUiView(self):
        self.cPanel.UpdateInspectorForUiView(self.stackView.GetSelectedUiView())
        self.cPanel.UpdateHandlerForUiView(self.stackView.GetSelectedUiView(), None)

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
        fileMenu.Append(ID_RUN, "&Run Card\tCtrl-R", "Run the current Stack")
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "E&xit", "Terminate the application")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")
        self.editMenu = editMenu

        cardMenu = wx.Menu()
        cardMenu.Append(ID_NEXT_CARD, "&Next Card\tCtrl-]", "Next Card")
        cardMenu.Append(ID_PREV_CARD, "&Previous Card\tCtrl-[", "Previous Card")
        cardMenu.AppendSeparator()
        cardMenu.Append(ID_ADD_CARD, "&Add Card\tCtrl-+", "Add Card")
        cardMenu.Append(ID_DUPLICATE_CARD, "&Duplicate Card", "Duplicate Card")
        cardMenu.Append(ID_REMOVE_CARD, "&Remove Card", "Remove Card")
        cardMenu.AppendSeparator()
        cardMenu.Append(ID_MOVE_CARD_FWD, "Move Card &Forward", "Move Card Forward")
        cardMenu.Append(ID_MOVE_CARD_BACK, "Move Card Bac&k", "Move Card Back")
        self.editMenu = cardMenu

        viewMenu = wx.Menu()
        viewMenu.Append(ID_MOVE_VIEW_FRONT, "Move to Front", "Move to Front")
        viewMenu.Append(ID_MOVE_VIEW_FWD, "Move &Forward", "Move Forward")
        viewMenu.Append(ID_MOVE_VIEW_BACK, "Move Bac&k", "Move Back")
        viewMenu.Append(ID_MOVE_VIEW_END, "Move to Back", "Move to Back")
        self.editMenu = viewMenu

        # and the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(wx.ID_ABOUT, "&About\tCtrl-H", "Display the gratuitous 'about this app' thingamajig")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(cardMenu, "&Cards")
        menuBar.Append(viewMenu, "&Views")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,  self.OnMenuNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU,   self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU,   self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU,  self.OnMenuRun, id=ID_RUN)
        self.Bind(wx.EVT_MENU,   self.OnMenuExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU,  self.OnMenuAbout, id=wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU,  self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU,  self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU,  self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU,  self.OnPaste, id=wx.ID_PASTE)

        self.Bind(wx.EVT_MENU,  self.OnMenuNextCard, id=ID_NEXT_CARD)
        self.Bind(wx.EVT_MENU,  self.OnMenuPrevCard, id=ID_PREV_CARD)
        self.Bind(wx.EVT_MENU,  self.OnMenuAddCard, id=ID_ADD_CARD)
        self.Bind(wx.EVT_MENU,  self.OnMenuDuplicateCard, id=ID_DUPLICATE_CARD)
        self.Bind(wx.EVT_MENU,  self.OnMenuRemoveCard, id=ID_REMOVE_CARD)
        self.Bind(wx.EVT_MENU,  self.OnMenuMoveCard, id=ID_MOVE_CARD_FWD)
        self.Bind(wx.EVT_MENU,  self.OnMenuMoveCard, id=ID_MOVE_CARD_BACK)

        self.Bind(wx.EVT_MENU,  self.OnMenuMoveView, id=ID_MOVE_VIEW_FRONT)
        self.Bind(wx.EVT_MENU,  self.OnMenuMoveView, id=ID_MOVE_VIEW_FWD)
        self.Bind(wx.EVT_MENU,  self.OnMenuMoveView, id=ID_MOVE_VIEW_BACK)
        self.Bind(wx.EVT_MENU,  self.OnMenuMoveView, id=ID_MOVE_VIEW_END)


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
            self.OpenFile(filename)
        dlg.Destroy()

    def OpenFile(self, filename):
        self.filename = filename
        self.ReadFile()
        self.SetTitle(self.title + ' -- ' + self.filename)

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
            self.SaveFile()
            self.SetTitle(self.title + ' -- ' + self.filename)
        dlg.Destroy()

    def OnMenuRun(self, event):
        if self.viewer:
            self.viewer.Destroy()
        self.viewer = ViewerFrame(self)
        sb = self.viewer.CreateStatusBar()
        data = self.stackView.stackModel.GetData()

        stack = StackModel()
        stack.SetData(data)
        self.viewer.stackView.SetStackModel(stack)
        self.viewer.stackView.SetEditing(False)
        self.viewer.Bind(wx.EVT_CLOSE, self.OnViewerClose)
        self.viewer.SetClientSize(self.stackView.stackModel.GetProperty("size"))
        self.viewer.RunViewer(sb)

    def OnViewerClose(self, event):
        self.viewer.Destroy()
        self.viewer = None

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

    def OnMenuMoveView(self, event):
        if event.GetId() == ID_MOVE_VIEW_FRONT:
            self.stackView.ReorderSelectedView("front")
        elif event.GetId() == ID_MOVE_VIEW_FWD:
            self.stackView.ReorderSelectedView("fwd")
        elif event.GetId() == ID_MOVE_VIEW_BACK:
            self.stackView.ReorderSelectedView("back")
        elif event.GetId() == ID_MOVE_VIEW_END:
            self.stackView.ReorderSelectedView("end")

    def OnMenuMoveCard(self, event):
        if event.GetId() == ID_MOVE_CARD_FWD:
            self.stackView.ReorderCurrentCard("fwd")
        elif event.GetId() == ID_MOVE_CARD_BACK:
            self.stackView.ReorderCurrentCard("back")

    def OnMenuNextCard(self, event):
        index = self.stackView.cardIndex+1
        if index < len(self.stackView.stackModel.cardModels):
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
        numCards = len(self.stackView.stackModel.cardModels)
        for m in self.stackView.stackModel.cardModels:
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

    def OnCut(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.CutView()
        elif f and hasattr(f, "Cut"):
            f.Cut()

    def OnCopy(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.CopyView()
        elif f and hasattr(f, "Copy"):
            f.Copy()

    def OnPaste(self, event):
        f = self.FindFocus()
        if f == self.stackView:
            self.stackView.PasteView()
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

    def OnMenuAbout(self, event):
        dlg = CardStockAbout(self)
        dlg.ShowModal()
        dlg.Destroy()


# ----------------------------------------------------------------------



class CardStockAbout(wx.Dialog):
    """ An about box that uses an HTML view """

    text = '''
<html>
<body bgcolor="#60acac">
<center><table bgcolor="#455481" width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center"><h1>CardStock %s</h1></td>
</tr>
</table>
</center>
<p><b>CardStock</b> is a tool for learning python using a GUI framework inspired by HyperCard of old.</p>
</body>
</html>
'''

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About CardStock',
                          size=(420, 380) )

        html = wx.html.HtmlWindow(self, -1)
        html.SetPage(self.text % version.VERSION)
        button = wx.Button(self, wx.ID_OK, "Okay")

        # Set up the layout with a Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html, wx.SizerFlags(1).Expand().Border(wx.ALL, 5))
        sizer.Add(button, wx.SizerFlags(0).Align(wx.ALIGN_CENTER).Border(wx.BOTTOM, 5))
        self.SetSizer(sizer)
        self.Layout()

        self.CentreOnParent(wx.BOTH)
        wx.CallAfter(button.SetFocus)


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
        app.frame.OpenFile(filename)
    app.MainLoop()

