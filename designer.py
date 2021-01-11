# designer.py
"""
This module implements the PyPageDesigner application.  It takes the
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
from stackWindow import StackWindow
from controlPanel import ControlPanel
from viewer import ViewerFrame
import version
from stack import StackModel
from uiPage import PageModel

from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------


class DesignerFrame(wx.Frame):
    """
    A pageFrame contains a pageWindow and a ControlPanel and manages
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
        toolbar.AddTool(wx.ID_INDEX, 'Edit', wx.ArtProvider.GetBitmap(wx.ART_FIND), wx.NullBitmap)
        toolbar.AddTool(wx.ID_EDIT, 'Draw', wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE), wx.NullBitmap)
        toolbar.AddTool(wx.ID_APPLY, 'Run', wx.ArtProvider.GetBitmap(wx.ART_FULL_SCREEN), wx.NullBitmap)
        toolbar.AddSeparator()

        self.addButton = wx.Button(parent=toolbar, id=wx.ID_ANY, label="Button")
        self.addButton.Bind(wx.EVT_LEFT_DOWN, self.OnMenuAddButton)
        toolbar.AddControl(self.addButton, label="Add Button")

        self.addTextField = wx.TextCtrl(parent=toolbar, id=wx.ID_ANY, value="TextField", style=wx.TE_CENTER)
        self.addTextField.Bind(wx.EVT_LEFT_DOWN, self.OnMenuAddTextField)
        self.addTextField.SetEditable(False)
        toolbar.AddControl(self.addTextField, label="Add TextField")

        self.addTextLabel = wx.StaticText(parent=toolbar, id=wx.ID_ANY, label="TextLabel", style=wx.ALIGN_CENTER)
        self.addTextLabel.Bind(wx.EVT_LEFT_DOWN, self.OnMenuAddTextLabel)
        toolbar.AddControl(self.addTextLabel, label="Add TextLabel")

        toolbar.AddTool(wx.ID_FILE1, 'Add Image', wx.ArtProvider.GetBitmap(wx.ART_NEW), wx.NullBitmap)

        # toolbar.AddTool(wx.ID_FILE1, 'Add Button', wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR), wx.NullBitmap)
        # toolbar.AddTool(wx.ID_FILE2, 'Add Field', wx.ArtProvider.GetBitmap(wx.ART_NEW), wx.NullBitmap)
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnMenuDraw, id=wx.ID_EDIT)
        self.Bind(wx.EVT_TOOL, self.OnMenuEdit, id=wx.ID_INDEX)
        self.Bind(wx.EVT_TOOL, self.OnMenuRun, id=wx.ID_APPLY)
        self.Bind(wx.EVT_TOOL, self.OnMenuAddImage, id=wx.ID_FILE1)

        self.splitter = wx.SplitterWindow(self, id=wx.ID_ANY, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        stackModel = StackModel()
        stackModel.AddPageModel(PageModel())
        self.stackView = StackWindow(self.splitter, -1, stackModel)
        self.stackView.SetEditing(True)
        self.stackView.SetDesigner(self)

        self.stackView.command_processor.SetEditMenu(self.editMenu)

        self.cPanel = ControlPanel(self.splitter, -1, self.stackView)

        self.splitter.SplitVertically(self.stackView, self.cPanel)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(self.splitter.GetSize()[0]-200)
        self.splitter.SetSashGravity(0.8)

        self.viewer = None

        self.stackView.SetFocus()
        self.SetSelectedUiView(self.stackView.uiPage)
        self.Layout()
        self.stackView.stackModel.SetDirty(False)

    def NewFile(self):
        self.filename = None
        stackModel = StackModel()
        pm = PageModel()
        stackModel.AddPageModel(pm)
        self.stackView.SetStackModel(stackModel)
        self.stackView.SetEditing(True)
        self.Layout()
        pm.SetProperty("size", self.stackView.GetSize())
        self.stackView.stackModel.SetDirty(False)
        self.stackView.SelectUiView(self.stackView.uiPage)

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
                self.stackView.SetStackModel(stackModel)
                self.stackView.SetSize(self.stackView.uiPage.model.GetProperty("size"))
                self.stackView.SetEditing(True)
                self.stackView.SetDesigner(self)
                self.stackView.SelectUiView(self.stackView.uiPage)
                self.SetFrameSizeFromModel()

    def SetFrameSizeFromModel(self):
        self.splitter.SetSize((self.stackView.GetSize().Width + self.splitter.GetSashSize() + self.cPanel.GetSize().Width,
                               self.stackView.GetSize().Height))
        self.SetClientSize(self.splitter.GetSize())

    def SetSelectedUiView(self, view):
        self.cPanel.UpdateForUiView(view)

    def UpdateSelectedUiView(self):
        self.cPanel.UpdateInspectorForUiView(self.stackView.GetSelectedUiView())
        self.cPanel.UpdateHandlerForUiView(self.stackView.GetSelectedUiView(), None)

    def MakeMenu(self):
        # create the file menu
        menu1 = wx.Menu()

        # Using the "\tKeyName" syntax automatically creates a
        # wx.AcceleratorTable for this frame and binds the keys to
        # the menu items.
        menu1.Append(wx.ID_NEW, "&New Page\tCtrl-N", "Create a new file")
        menu1.Append(wx.ID_OPEN, "&Open\tCtrl-O", "Open a Stack")
        menu1.AppendSeparator()
        menu1.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save the Stack")
        menu1.Append(wx.ID_SAVEAS, "Save &As", "Save the Stack in a new file")
        menu1.AppendSeparator()
        runId = wx.NewIdRef()
        menu1.Append(runId, "&Run Page\tCtrl-R", "Run the current Stack")
        menu1.AppendSeparator()
        menu1.Append(wx.ID_EXIT, "E&xit", "Terminate the application")

        menu2 = wx.Menu()
        menu2.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        menu2.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        menu2.AppendSeparator()
        menu2.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        menu2.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        menu2.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")
        self.editMenu = menu2

        # and the help menu
        menu3 = wx.Menu()
        menu3.Append(wx.ID_ABOUT, "&About\tCtrl-H", "Display the gratuitous 'about this app' thingamajig")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,  self.OnMenuNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU,   self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU,   self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU,  self.OnMenuRun, id=runId)
        self.Bind(wx.EVT_MENU,   self.OnMenuExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU,  self.OnMenuAbout, id=wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU,  self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU,  self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU,  self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU,  self.OnPaste, id=wx.ID_PASTE)

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
        self.viewer.SetClientSize(self.stackView.uiPage.model.GetProperty("size"))
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
        if f and hasattr(f, "Undo"):
            if not hasattr(f, "CanUndo") or f.CanUndo():
                f.Undo()
                return
        event.Skip()

    def OnRedo(self, event):
        f = self.GetDesiredFocus()
        if f == self.cPanel.codeEditor: f = self.stackView
        if f and hasattr(f, "Redo"):
            if not hasattr(f, "CanRedo") or f.CanRedo():
                f.Redo()
                return
        event.Skip()

    def OnMenuAbout(self, event):
        dlg = PageAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMenuDraw(self, event):
        self.cPanel.SetDrawingMode(True)

    def OnMenuEdit(self, event):
        self.cPanel.SetDrawingMode(False)

    def OnMenuAddButton(self, event):
        if self.stackView.uiPage.isEditing and not self.stackView.isInDrawingMode:
            self.stackView.AddUiViewOfType("button")
            event.Skip()

    def OnMenuAddTextField(self, event):
        if self.stackView.uiPage.isEditing and not self.stackView.isInDrawingMode:
            self.stackView.AddUiViewOfType("textfield")
            event.Skip()

    def OnMenuAddTextLabel(self, event):
        if self.stackView.uiPage.isEditing and not self.stackView.isInDrawingMode:
            self.stackView.AddUiViewOfType("textlabel")
            event.Skip()

    def OnMenuAddImage(self, event):
        if self.stackView.uiPage.isEditing and not self.stackView.isInDrawingMode:
            self.stackView.AddUiViewOfType("image")
            event.Skip()


# ----------------------------------------------------------------------



class PageAbout(wx.Dialog):
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

