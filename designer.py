# designer.py
"""
This module implements the PyPageDesigner application.  It takes the
PageWindow and reuses it in a much more
intelligent Frame.  This one has a menu and a statusbar, is able to
save and reload stacks, clear the workspace, and has a simple control
panel for setting color and line thickness in addition to the popup
menu that PageWindow provides.  There is also a nice About dialog
implemented using an wx.html.HtmlWindow.
"""

import os

from six.moves import cPickle as pickle

import wx
import wx.html
from page import PageWindow, SoloPageFrame
from controlPanel import ControlPanel
import version
from runner import Runner

from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------


class PageFrame(wx.Frame):
    """
    A pageFrame contains a pageWindow and a ControlPanel and manages
    their layout with a wx.BoxSizer.  A menu and associated event handlers
    provides for saving a page to a file, etc.
    """
    title = "Page"

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, self.title, size=(800,600),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetIcon(wx.Icon(os.path.join(HERE, 'resources/mondrian.ico')))
        self.CreateStatusBar()
        self.MakeMenu()
        self.filename = None

        toolbar = self.CreateToolBar(style=wx.TB_TEXT)
        toolbar.AddTool(wx.ID_INDEX, 'Edit', wx.ArtProvider.GetBitmap(wx.ART_FIND), wx.NullBitmap)
        toolbar.AddTool(wx.ID_EDIT, 'Draw', wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE), wx.NullBitmap)
        toolbar.AddTool(wx.ID_APPLY, 'Run', wx.ArtProvider.GetBitmap(wx.ART_FULL_SCREEN), wx.NullBitmap)
        toolbar.AddSeparator()

        self.addButton = wx.Button(parent=toolbar, id=wx.ID_ANY, label="Button")
        self.addButton.Bind(wx.EVT_LEFT_DOWN, self.OnMenuAddButton)
        toolbar.AddControl(self.addButton, label="Add Button")

        self.addTextField = wx.TextCtrl(parent=toolbar, id=wx.ID_ANY, value="Text")
        self.addTextField.Bind(wx.EVT_LEFT_DOWN, self.OnMenuAddTextField)
        self.addTextField.SetEditable(False)
        toolbar.AddControl(self.addTextField, label="Add TextField")

        # toolbar.AddTool(wx.ID_FILE1, 'Add Button', wx.ArtProvider.GetBitmap(wx.ART_NEW_DIR), wx.NullBitmap)
        # toolbar.AddTool(wx.ID_FILE2, 'Add Field', wx.ArtProvider.GetBitmap(wx.ART_NEW), wx.NullBitmap)
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnMenuDraw, id=wx.ID_EDIT)
        self.Bind(wx.EVT_TOOL, self.OnMenuEdit, id=wx.ID_INDEX)
        self.Bind(wx.EVT_TOOL, self.OnMenuRun, id=wx.ID_APPLY)
        # self.Bind(wx.EVT_TOOL, self.OnMenuAddButton, id=wx.ID_FILE1)
        # self.Bind(wx.EVT_TOOL, self.OnMenuAddTextField, id=wx.ID_FILE2)

        self.splitter = wx.SplitterWindow(self, id=wx.ID_ANY, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        self.page = PageWindow(self.splitter, -1)
        self.page.SetEditing(True)
        self.page.SetDesigner(self)

        self.cPanel = ControlPanel(self.splitter, -1, self.page)

        self.splitter.SplitVertically(self.page, self.cPanel)
        self.splitter.SetMinimumPaneSize(120)
        self.splitter.SetSashPosition(self.splitter.GetSize()[0]-200)
        self.splitter.SetSashGravity(0.8)

        self.SetSelectedUIView(None)

    def SaveFile(self):
        if self.filename:
            data = {}
            data["lines"] = self.page.GetLinesData()
            data["uiviews"] = self.page.GetUIViewsData()
            data["handlers"] = self.page.GetHandlersData()

            with open(self.filename, 'wb') as f:
                pickle.dump(data, f)

    def ReadFile(self):
        if self.filename:
            self.page.ReadFile(self.filename)

    def SetSelectedUIView(self, view):
        self.cPanel.UpdateForUIView(view)

    def MakeMenu(self):
        # create the file menu
        menu1 = wx.Menu()

        # Using the "\tKeyName" syntax automatically creates a
        # wx.AcceleratorTable for this frame and binds the keys to
        # the menu items.
        menu1.Append(wx.ID_OPEN, "&Open\tCtrl-O", "Open a page file")
        menu1.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save the page")
        menu1.Append(wx.ID_SAVEAS, "Save &As", "Save the page in a new file")
        menu1.AppendSeparator()
        menu1.Append(wx.ID_CLEAR, "&Clear Page", "Clear the current page")
        menu1.AppendSeparator()
        runId = wx.NewIdRef()
        menu1.Append(runId, "&Run Page\tCtrl-R", "Run the current page")
        menu1.AppendSeparator()
        menu1.Append(wx.ID_EXIT, "E&xit", "Terminate the application")

        menu2 = wx.Menu()
        menu2.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        menu2.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        menu2.AppendSeparator()
        menu2.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        menu2.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        menu2.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")

        # and the help menu
        menu3 = wx.Menu()
        menu3.Append(wx.ID_ABOUT, "&About\tCtrl-H", "Display the gratuitous 'about this app' thingamajig")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Edit")
        menuBar.Append(menu3, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,   self.OnMenuOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU,   self.OnMenuSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU,  self.OnMenuClear, id=wx.ID_CLEAR)
        self.Bind(wx.EVT_MENU,  self.OnMenuRun, id=runId)
        self.Bind(wx.EVT_MENU,   self.OnMenuExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU,  self.OnMenuAbout, id=wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU,  self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU,  self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU,  self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU,  self.OnPaste, id=wx.ID_PASTE)

    wildcard = "page files (*.ddl)|*.ddl|All files (*.*)|*.*"

    def OnMenuOpen(self, event):
        dlg = wx.FileDialog(self, "Open page file...", os.getcwd(),
                           style=wx.FD_OPEN, wildcard = self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.ReadFile()
            self.SetTitle(self.title + ' -- ' + self.filename)
        dlg.Destroy()

    def OnMenuSave(self, event):
        if not self.filename:
            self.OnMenuSaveAs(event)
        else:
            self.SaveFile()

    def OnMenuSaveAs(self, event):
        dlg = wx.FileDialog(self, "Save page as...", os.getcwd(),
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           wildcard = self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.ddl'
            self.filename = filename
            self.SaveFile()
            self.SetTitle(self.title + ' -- ' + self.filename)
        dlg.Destroy()

    def OnMenuClear(self, event):
        self.page.ClearAll()
        self.SetTitle(self.title)

    def GetData(self):
        data = {}
        data["lines"] = self.page.GetLinesData()
        data["uiviews"] = self.page.GetUIViewsData()
        data["handlers"] = self.page.GetHandlersData()
        return data

    def OnMenuRun(self, event):
        frame = SoloPageFrame(None)
        sb = frame.CreateStatusBar()
        data = self.GetData()
        frame.page.LoadFromData(data)
        frame.page.SetEditing(False)
        frame.Show(True)

        frame.page.runner = Runner(frame.page, sb)
        if "OnStart" in frame.page.uiPage.handlers:
            frame.page.runner.RunHandler(frame.page.uiPage, "OnStart")

    def OnMenuExit(self, event):
        self.Close()

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
            f.Undo()

    def OnRedo(self, event):
        f = self.FindFocus()
        if f and hasattr(f, "Redo"):
            f.Redo()

    def OnMenuAbout(self, event):
        dlg = PageAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMenuDraw(self, event):
        self.cPanel.SetDrawingMode(True)

    def OnMenuEdit(self, event):
        self.cPanel.SetDrawingMode(False)

    def OnMenuAddButton(self, event):
        if self.page.isEditing and not self.page.isInDrawingMode:
            self.page.AddUiViewOfType("button")
            event.Skip()

    def OnMenuAddTextField(self, event):
        if self.page.isEditing and not self.page.isInDrawingMode:
            self.page.AddUiViewOfType("textfield")
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
    <td align="center"><h1>PyPage %s</h1></td>
</tr>
</table>
</center>
<p><b>PyPage</b> is a tool for learning python using a GUI framework inspired by HyperCard of old.</p>
</body>
</html>
'''

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About PyPage',
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

class PageApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init() # for InspectionMixin

        frame = PageFrame(None)
        frame.Show(True)
        self.SetTopWindow(frame)
        self.SetAppDisplayName('PyPage')
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
    app = PageApp(redirect=False)
    app.MainLoop()

