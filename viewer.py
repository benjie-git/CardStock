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
from stackWindow import StackWindow
from stackModel import StackModel
from uiCard import CardModel
import version
from runner import Runner

from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------


class ViewerFrame(wx.Frame):
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
        self.filename = None

        self.stackView = StackWindow(self, -1, None)
        self.stackView.SetEditing(False)

    def ReadFile(self, filename):
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
            if data:
                self.stackView.stackModel.SetData(data)
                self.stackView.SetStackModel(self.stackView.stackModel)
                self.SetClientSize(self.stackView.stackModel.GetProperty("size"))
                self.filename = filename

    def SaveFile(self):
        if self.filename:
            data = self.stackView.stackModel.GetData()
            try:
                jsonData = json.dumps(data, indent=2)
                with open(self.filename, 'w') as f:
                    f.write(jsonData)
                self.stackView.stackModel.SetDirty(False)
            except TypeError:
                pass

    def MakeMenu(self):
        # create the file menu
        fileMenu = wx.Menu()
        if self.filename:
            fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save Stack")
        fileMenu.Append(wx.ID_CLOSE, "&Close\tCtrl-W", "Close Stack")

        editMenu = wx.Menu()
        editMenu.Append(wx.ID_UNDO, "&Undo\tCtrl-Z", "Undo Action")
        editMenu.Append(wx.ID_REDO, "&Redo\tCtrl-Shift-Z", "Redo Action")
        editMenu.AppendSeparator()
        editMenu.Append(wx.ID_CUT,  "C&ut\tCtrl-X", "Cut Selection")
        editMenu.Append(wx.ID_COPY, "&Copy\tCtrl-C", "Copy Selection")
        editMenu.Append(wx.ID_PASTE,"&Paste\tCtrl-V", "Paste Selection")

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

    def OnMenuSave(self, event):
        self.SaveFile()

    def OnMenuClose(self, event):
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

    def OnMenuAbout(self, event):
        dlg = CardStockAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def RunViewer(self, sb):
        runner = Runner(self.stackView, sb)
        self.stackView.runner = runner
        self.stackView.SetEditing(False)
        self.SetClientSize(self.stackView.stackModel.GetProperty("size"))
        self.Show(True)

        runner.RunHandler(self.stackView.stackModel, "OnStackStart", None)

        self.MakeMenu()
        self.stackView.LoadCardAtIndex(0, reload=True)




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

class ViewerApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init(self)  # for InspectionMixin

        self.frame = ViewerFrame(None)
        self.statusbar = self.frame.CreateStatusBar()
        self.SetTopWindow(self.frame)
        self.SetAppDisplayName('CardStock')
        self.frame.Show(True)

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
    app = ViewerApp(redirect=False)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        app.frame.ReadFile(filename)
    else:
        print("Usage: python3 viewer.py filename")
        exit(1)
    app.frame.RunViewer(app.statusbar)

    app.MainLoop()
