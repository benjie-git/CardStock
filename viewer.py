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
import sys
import json
import wx
import wx.html
from pageWindow import PageWindow
from uiPage import PageModel
import version
from runner import Runner
from stack import StackModel

from wx.lib.mixins.inspection import InspectionMixin

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------


class ViewerFrame(wx.Frame):
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
        self.MakeMenu()
        self.filename = None

        self.stack = StackModel()
        self.stack.AddPageModel(PageModel())
        self.page = PageWindow(self, -1, self.stack.GetPageModel(0))
        self.page.SetEditing(False)

    def ReadFile(self, filename):
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
            if data:
                self.stack.SetData(data)
                self.page.SetModel(self.stack.GetPageModel(0))
                self.SetSize(self.page.uiPage.model.GetProperty("size"))
                self.filename = filename

    def MakeMenu(self):
        # create the file menu
        menu1 = wx.Menu()
        menu1.Append(wx.ID_CLOSE, "&Close\tCtrl-W", "Close Window")

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

        self.Bind(wx.EVT_MENU,   self.OnClose, id=wx.ID_CLOSE)

        self.Bind(wx.EVT_MENU,  self.OnMenuAbout, id=wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU,  self.OnUndo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU,  self.OnRedo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU,  self.OnCut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU,  self.OnCopy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU,  self.OnPaste, id=wx.ID_PASTE)

    def OnClose(self, event):
        self.Destroy()

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
        dlg = PageAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def RunViewer(self, sb):
        runner = Runner(self.page, sb)
        self.page.uiPage.model.runner = runner
        for ui in self.page.uiViews:
            ui.model.runner = runner
        self.page.SetEditing(False)
        self.Show(True)

        if "OnStart" in self.page.uiPage.model.handlers:
            runner.RunHandler(self.page.uiPage.model, "OnStart", None)


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

class ViewerApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init(self) # for InspectionMixin

        self.frame = ViewerFrame(None)
        self.statusbar = self.frame.CreateStatusBar()
        self.SetTopWindow(self.frame)
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
    app = ViewerApp(redirect=False)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        app.frame.ReadFile(filename)
    else:
        print("Usage: python3 viewer.py filename")
        exit(1)
    app.frame.RunViewer(app.statusbar)

    app.MainLoop()

