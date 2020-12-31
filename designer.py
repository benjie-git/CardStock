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
import PythonEditor

from six.moves import cPickle as pickle

import wx
import wx.html
import wx.stc as stc
from wx.lib import buttons # for generic button classes
from page import PageWindow
import PythonEditor
import draggableView
import version

from wx.lib.mixins.inspection import InspectionMixin


HERE = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, 'frozen') and sys.frozen:
    HERE = os.path.dirname(os.path.abspath(sys.argv[0]))

#----------------------------------------------------------------------

# There are standard IDs for the menu items we need in this app, or we
# could have used wx.NewId() to autogenerate some new unique ID values
# instead.

idNEW    = wx.ID_NEW
idOPEN   = wx.ID_OPEN
idSAVE   = wx.ID_SAVE
idSAVEAS = wx.ID_SAVEAS
idCLEAR  = wx.ID_CLEAR
idEXIT   = wx.ID_EXIT
idABOUT  = wx.ID_ABOUT



class pageFrame(wx.Frame):
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

        self.page = PageWindow(self, -1, True)
        self.page.SetDesigner(self)
        self.cPanel = ControlPanel(self, -1, self.page)

        # Create a sizer to layout the two windows side-by-side.
        # Both will grow vertically, the page window will grow
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
        else:
            self.cPanel.codeEditor.SetText("")

    def MakeMenu(self):
        # create the file menu
        menu1 = wx.Menu()

        # Using the "\tKeyName" syntax automatically creates a
        # wx.AcceleratorTable for this frame and binds the keys to
        # the menu items.
        menu1.Append(idOPEN, "&Open\tCtrl-O", "Open a page file")
        menu1.Append(idSAVE, "&Save\tCtrl-S", "Save the page")
        menu1.Append(idSAVEAS, "Save &As", "Save the page in a new file")
        menu1.AppendSeparator()
        menu1.Append(idCLEAR, "&Clear", "Clear the current page")
        menu1.AppendSeparator()
        menu1.Append(idEXIT, "E&xit", "Terminate the application")

        # and the help menu
        menu2 = wx.Menu()
        if hasattr(sys, 'frozen'):
            item = menu2.Append(-1, "Check for Update...")
            self.Bind(wx.EVT_MENU, self.OnMenuCheckForUpdate, item)

        menu2.Append(idABOUT, "&About\tCtrl-H", "Display the gratuitous 'about this app' thingamajig")

        # and add them to a menubar
        menuBar = wx.MenuBar()
        menuBar.Append(menu1, "&File")
        menuBar.Append(menu2, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,   self.OnMenuOpen, id=idOPEN)
        self.Bind(wx.EVT_MENU,   self.OnMenuSave, id=idSAVE)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveAs, id=idSAVEAS)
        self.Bind(wx.EVT_MENU,  self.OnMenuClear, id=idCLEAR)
        self.Bind(wx.EVT_MENU,   self.OnMenuExit, id=idEXIT)
        self.Bind(wx.EVT_MENU,  self.OnMenuAbout, id=idABOUT)



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
        self.page.SetLinesData([])
        self.SetTitle(self.title)


    def OnMenuExit(self, event):
        self.Close()


    def OnMenuAbout(self, event):
        dlg = PageAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnMenuCheckForUpdate(self, event):
        wx.GetApp().CheckForUpdate(parentWindow=self)

#----------------------------------------------------------------------


class ControlPanel(wx.Panel):
    """
    This class implements a very simple control panel for the pageWindow.
    It creates buttons for each of the colours and thickneses supported by
    the pageWindow, and event handlers to set the selected values.  There is
    also a little window that shows an example line in the selected
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
        cGrid = wx.GridSizer(cols=numCols, hgap=2, vgap=2)
        for k in keys:
            bmp = self.MakeBitmap(colours[k])
            b = buttons.GenBitmapToggleButton(self, k, bmp, size=btnSize )
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            self.Bind(wx.EVT_BUTTON, self.OnSetColour, b)
            cGrid.Add(b, 0)
            self.clrBtns[colours[k]] = b
        self.clrBtns[colours[keys[0]]].SetToggle(True)


        # Make a grid of buttons for the thicknesses.  Attach each button
        # event to self.OnSetThickness.  The button ID is the same as the
        # thickness value.
        self.thknsBtns = {}
        tGrid = wx.GridSizer(cols=numCols, hgap=2, vgap=2)
        for x in range(1, page.maxThickness+1):
            b = buttons.GenToggleButton(self, x, str(x), size=btnSize)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            self.Bind(wx.EVT_BUTTON, self.OnSetThickness, b)
            tGrid.Add(b, 0)
            self.thknsBtns[x] = b
        self.thknsBtns[1].SetToggle(True)

        # Make a colour indicator window, it is registerd as a listener
        # with the page window so it will be notified when the settings
        # change
        ci = ColourIndicator(self)
        page.AddListener(ci)
        page.Notify()
        self.page = page

        addButton = wx.Button(parent=self, id=-1, label="Button")
        addButton.Bind(wx.EVT_LEFT_DOWN, self.addButtonDown)

        addText = wx.TextCtrl(parent=self, id=-1, value="Text")
        addText.SetEditable(False)
        addText.Bind(wx.EVT_LEFT_DOWN, self.addTextDown)

        self.codeEditor = PythonEditor.CreatePythonEditor(self)
        self.codeEditor.SetSize((150,200))
        self.codeEditor.Bind(stc.EVT_STC_CHANGE, self.codeEditorTextChanged)

        # Make a box sizer and put the two grids and the indicator
        # window in it.
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(addButton, 0, wx.ALL, spacing)
        box.Add(addText, 0, wx.ALL, spacing)
        box.Add(cGrid, 0, wx.ALL, spacing)
        box.Add(tGrid, 0, wx.ALL, spacing)
        box.Add(ci, 0, wx.EXPAND|wx.ALL, spacing)
        box.Add(self.codeEditor, 0, wx.EXPAND|wx.ALL, spacing)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        # Resize this window so it is just large enough for the
        # minimum requirements of the sizer.
        box.Fit(self)

    def codeEditorTextChanged(self, event):
        self.page.GetSelectedUIView().SetHandler("onClick", self.codeEditor.GetText())

    def addButtonDown(self, event):
        self.page.AddUiViewOfType("button")
        event.Skip()

    def addTextDown(self, event):
        self.page.AddUiViewOfType("text")
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



#----------------------------------------------------------------------

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


    def Update(self, colour, thickness):
        """
        The page window calls this method any time the colour
        or line thickness changes.
        """
        self.colour = colour
        self.thickness = thickness
        self.Refresh()  # generate a paint event


    def OnPaint(self, event):
        """
        This method is called when all or part of the window needs to be
        redrawn.
        """
        dc = wx.PaintDC(self)
        if self.colour:
            sz = self.GetClientSize()
            pen = wx.Pen(self.colour, self.thickness)
            dc.SetPen(pen)
            dc.DrawLine(10, int(sz.height/2), int(sz.width-10), int(sz.height/2))


#----------------------------------------------------------------------

class PageAbout(wx.Dialog):
    """ An about box that uses an HTML window """

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


#----------------------------------------------------------------------
#----------------------------------------------------------------------


class PageApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init() # for InspectionMixin

        frame = pageFrame(None)
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

#----------------------------------------------------------------------

if __name__ == '__main__':
    app = PageApp(redirect=False)
    app.MainLoop()

