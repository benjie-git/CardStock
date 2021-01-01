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

import sys
import os

from six.moves import cPickle as pickle

import wx
import wx.html
import wx.stc as stc
from wx.lib import buttons # for generic button classes
from page import PageWindow, SoloPageFrame
import PythonEditor
import version

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
        self.codeEditor = None

        self.page = PageWindow(self, -1)
        self.page.SetEditing(True)
        self.page.SetDesigner(self)
        self.cPanel = ControlPanel(self, -1, self.page)

        # Create a sizer to layout the two windows side-by-side.
        # Both will grow vertically, the page view will grow
        # horizontally as well.
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.cPanel, 0, wx.EXPAND)
        box.Add(self.page, 1, wx.EXPAND)

        # Tell the frame that it should layout itself in response to
        # size events using this sizer.
        self.SetSizer(box)

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
        if view:
            self.cPanel.codeEditor.SetText(view.GetHandler("onClick"))
            self.cPanel.codeEditor.Enable(True)
        else:
            self.cPanel.codeEditor.SetText("")
            self.cPanel.codeEditor.Enable(False)

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
        runId = wx.NewId()
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

    def OnMenuRun(self, event):
        frame = SoloPageFrame(None)
        data = {}
        data["lines"] = self.page.GetLinesData()
        data["uiviews"] = self.page.GetUIViewsData()
        data["handlers"] = self.page.GetHandlersData()
        frame.page.LoadFromData(data)
        frame.Show(True)

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

# ----------------------------------------------------------------------


class ControlPanel(wx.Panel):
    """
    This class implements a very simple control panel for the pageWindow.
    It creates buttons for each of the colours and thickneses supported by
    the pageWindow, and event handlers to set the selected values.  There is
    also a little view that shows an example line in the selected
    values.  Nested sizers are used for layout.
    """

    BMP_SIZE = 16
    BMP_BORDER = 3

    def __init__(self, parent, ID, page):
        wx.Panel.__init__(self, parent, ID, style=wx.RAISED_BORDER)

        numCols = 4
        spacing = 4

        btnSize = wx.Size(self.BMP_SIZE + 2*self.BMP_BORDER,
                          self.BMP_SIZE + 2*self.BMP_BORDER)

        # Make a grid of buttons for each colour.  Attach each button
        # event to self.OnSetColour.  The button ID is the same as the
        # key in the colour dictionary.
        self.clrBtns = {}
        colours = page.menuColours
        keys = list(colours.keys())
        keys.sort()
        self.cGrid = wx.GridSizer(cols=numCols, hgap=2, vgap=2)
        for k in keys:
            bmp = self.MakeBitmap(colours[k])
            b = buttons.GenBitmapToggleButton(self, k, bmp, size=btnSize )
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            self.Bind(wx.EVT_BUTTON, self.OnSetColour, b)
            self.cGrid.Add(b, 0)
            self.clrBtns[colours[k]] = b
        self.clrBtns[colours[keys[0]]].SetToggle(True)

        # Make a grid of buttons for the thicknesses.  Attach each button
        # event to self.OnSetThickness.  The button ID is the same as the
        # thickness value.
        self.thknsBtns = {}
        self.tGrid = wx.GridSizer(cols=numCols, hgap=2, vgap=2)
        for x in range(1, page.maxThickness+1):
            b = buttons.GenToggleButton(self, x, str(x), size=btnSize)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            self.Bind(wx.EVT_BUTTON, self.OnSetThickness, b)
            self.tGrid.Add(b, 0)
            self.thknsBtns[x] = b
        self.thknsBtns[1].SetToggle(True)

        # Make a colour indicator view, it is registerd as a listener
        # with the page view so it will be notified when the settings
        # change
        self.ci = ColourIndicator(self)
        page.AddListener(self.ci)
        page.Notify()
        self.page = page

        self.addButton = wx.Button(parent=self, id=wx.ID_ANY, label="Button")
        self.addButton.Bind(wx.EVT_LEFT_DOWN, self.AddButtonDown)

        self.addTextField = wx.TextCtrl(parent=self, id=wx.ID_ANY, value="Text")
        self.addTextField.SetEditable(False)
        self.addTextField.Bind(wx.EVT_LEFT_DOWN, self.AddTextDown)

        self.codeEditor = PythonEditor.CreatePythonEditor(self)
        self.codeEditor.SetSize((150,200))
        self.codeEditor.Bind(stc.EVT_STC_CHANGE, self.CodeEditorTextChanged)

        self.modeSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.modeButtons = []
        b = buttons.GenToggleButton(self, 1, "Hand", size=(45,28))
        b.SetBezelWidth(1)
        b.SetUseFocusIndicator(False)
        self.Bind(wx.EVT_BUTTON, self.OnSetDrawingMode, b)
        self.modeSizer.Add(b, 0, wx.ALL, spacing)
        self.modeButtons.append(b)
        b = buttons.GenToggleButton(self, 2, "Pen", size=(45,28))
        b.SetBezelWidth(1)
        b.SetUseFocusIndicator(False)
        self.Bind(wx.EVT_BUTTON, self.OnSetDrawingMode, b)
        self.modeSizer.Add(b, 0, wx.ALL, spacing)
        self.modeButtons.append(b)
        self.modeButtons[0].SetToggle(True)

        # Make a box sizer and put the two grids and the indicator
        # view in it.
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.modeSizer, 0, wx.ALL, spacing)
        self.box.Add(self.addButton, 0, wx.ALL, spacing)
        self.box.Add(self.addTextField, 0, wx.ALL, spacing)
        self.box.Add(self.cGrid, 0, wx.ALL, spacing)
        self.box.Add(self.tGrid, 0, wx.ALL, spacing)
        self.box.Add(self.ci, 0, wx.EXPAND|wx.ALL, spacing)
        self.box.Add(self.codeEditor, 0, wx.EXPAND|wx.ALL, spacing)
        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.SetDrawingMode(False)

    def OnSetDrawingMode(self, event):
        drawMode = (event.GetId() == 2)
        self.SetDrawingMode(drawMode)

    def SetDrawingMode(self, drawMode):
        if drawMode:
            self.box.Show(self.cGrid)
            self.box.Show(self.tGrid)
            self.box.Show(self.ci)
            self.box.Hide(self.addButton)
            self.box.Hide(self.addTextField)
            self.box.Hide(self.codeEditor)
            self.modeButtons[0].SetToggle(False)
            self.modeButtons[1].SetToggle(True)
            self.page.SelectUIView(None)
        else:
            self.box.Hide(self.cGrid)
            self.box.Hide(self.tGrid)
            self.box.Hide(self.ci)
            self.box.Show(self.addButton)
            self.box.Show(self.addTextField)
            self.box.Show(self.codeEditor)
            self.modeButtons[0].SetToggle(True)
            self.modeButtons[1].SetToggle(False)
        self.box.Layout()
        # Resize this view so it is just large enough for the
        # minimum requirements of the sizer.
        self.box.Fit(self)
        self.page.SetDrawingMode(drawMode)

    def CodeEditorTextChanged(self, event):
        if self.page.GetSelectedUIView():
            self.page.GetSelectedUIView().SetHandler("onClick", self.codeEditor.GetText())

    def AddButtonDown(self, event):
        self.page.AddUiViewOfType("button")
        event.Skip()

    def AddTextDown(self, event):
        self.page.AddUiViewOfType("textfield")
        event.Skip()

    def MakeBitmap(self, colour):
        """
        We can create a bitmap of whatever we want by simply selecting
        it into a wx.MemoryDC and drawing on it.  In this case we just set
        a background brush and clear the dc.
        """
        bmp = wx.Bitmap(self.BMP_SIZE, self.BMP_SIZE)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(colour))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def OnSetColour(self, event):
        """
        Use the event ID to get the colour, set that colour in the page.
        """
        colour = self.page.menuColours[event.GetId()]
        if colour != self.page.colour:
            # untoggle the old colour button
            self.clrBtns[self.page.colour].SetToggle(False)
        # set the new colour
        self.page.SetColour(colour)

    def OnSetThickness(self, event):
        """
        Use the event ID to set the thickness in the page.
        """
        thickness = event.GetId()
        if thickness != self.page.thickness:
            # untoggle the old thickness button
            self.thknsBtns[self.page.thickness].SetToggle(False)
        # set the new colour
        self.page.SetThickness(thickness)


# ----------------------------------------------------------------------

class ColourIndicator(wx.Window):
    """
    An instance of this class is used on the ControlPanel to show
    a sample of what the current page line will look like.
    """
    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        self.SetMinSize( (45, 45) )
        self.colour = self.thickness = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateLine(self, colour, thickness):
        """
        The page view calls this method any time the colour
        or line thickness changes.
        """
        self.colour = colour
        self.thickness = thickness
        self.Refresh()  # generate a paint event

    def OnPaint(self, event):
        """
        This method is called when all or part of the view needs to be
        redrawn.
        """
        dc = wx.PaintDC(self)
        if self.colour:
            sz = self.GetClientSize()
            pen = wx.Pen(self.colour, self.thickness)
            dc.SetPen(pen)
            dc.DrawLine(10, int(sz.height/2), int(sz.width-10), int(sz.height/2))


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

