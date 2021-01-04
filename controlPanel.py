import wx
import wx.stc as stc
import wx.grid
from wx.lib import buttons # for generic button classes
import PythonEditor
import ast


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
        self.page = page

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

        # ----------

        self.inspector = wx.grid.Grid(self, -1)
        self.inspector.CreateGrid(1, 2)
        self.inspector.SetRowSize(0, 24)
        self.inspector.SetColSize(0, 70)
        self.inspector.SetColLabelSize(20)
        self.inspector.SetColLabelValue(0, "Inspector")
        self.inspector.SetColLabelValue(1, "Value")
        self.inspector.SetRowLabelSize(1)
        self.inspector.DisableDragRowSize()

        self.inspector.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.InspectorValueChanged)
        self.inspector.Bind(wx.EVT_KEY_DOWN, self.OnGridEnter)

        self.handlerPicker = wx.Choice(parent=self, id=wx.ID_ANY)
        self.handlerPicker.Enable(False)
        self.handlerPicker.Bind(wx.EVT_CHOICE, self.OnHandlerChoice)
        self.currentHandler = None

        self.codeEditor = PythonEditor.CreatePythonEditor(self)
        self.codeEditor.SetSize((150,2000))
        self.codeEditor.Bind(stc.EVT_STC_CHANGE, self.CodeEditorTextChanged)

        self.lastSelectedUIView = None
        self.UpdateInspectorForUIView(None)
        self.UpdateHandlerForUIView(None, None)

        # ----------

        self.drawBox = wx.BoxSizer(wx.VERTICAL)
        self.drawBox.Add(self.cGrid, 0, wx.RIGHT, spacing)
        self.drawBox.Add(self.tGrid, 0, wx.RIGHT, spacing)
        self.drawBox.Add(self.ci, 0, wx.EXPAND|wx.ALL, spacing)

        self.editBox = wx.BoxSizer(wx.VERTICAL)
        self.editBox.Add(self.inspector, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.AddSpacer(10)
        self.editBox.Add(self.handlerPicker, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.Add(self.codeEditor, 1, wx.EXPAND|wx.ALL, spacing)
        self.editBox.SetSizeHints(self)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.drawBox, 0, wx.EXPAND|wx.ALL, spacing)
        self.box.Add(self.editBox, 1, wx.EXPAND|wx.ALL, spacing)
        self.box.SetSizeHints(self)

        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.SetDrawingMode(False)

    def OnSetDrawingMode(self, event):
        drawMode = (event.GetId() == 2)
        self.SetDrawingMode(drawMode)

    def SetDrawingMode(self, drawMode):
        if drawMode:
            self.box.Show(self.drawBox)
            self.box.Hide(self.editBox)
            self.page.SelectUIView(None)
        else:
            self.box.Hide(self.drawBox)
            self.box.Show(self.editBox)

        self.Layout()
        self.page.SetDrawingMode(drawMode)

    def OnGridEnter(self, event):
        if not self.inspector.IsCellEditControlShown() and \
                (event.GetKeyCode() == wx.WXK_RETURN or event.GetKeyCode() == wx.WXK_NUMPAD_ENTER):
            if self.inspector.GetGridCursorCol() == 1:
                self.inspector.EnableCellEditControl()
        else:
            event.Skip()

    def CodeEditorTextChanged(self, event):
        uiView = self.page.GetSelectedUIView()
        if not uiView:
            uiView = self.page.uiPage
        uiView.SetHandler(self.currentHandler, self.codeEditor.GetText())

    def OnHandlerChoice(self, event):
        self.UpdateHandlerForUIView(self.page.GetSelectedUIView(),
                                    self.handlerPicker.GetItems()[self.handlerPicker.GetSelection()])

    def UpdateForUIView(self, uiView):
        if uiView != self.lastSelectedUIView:
            self.UpdateInspectorForUIView(uiView)
            self.UpdateHandlerForUIView(uiView, None)
            self.lastSelectedUIView = uiView

    def UpdateInspectorForUIView(self, uiView):
        if self.inspector.GetNumberRows() > 0:
            self.inspector.DeleteRows(0, self.inspector.GetNumberRows())
        if not uiView:
            uiView = self.page.uiPage
        keys = uiView.GetPropertyKeys()
        self.inspector.InsertRows(0,len(keys))
        r = 0
        for k in keys:
            self.inspector.SetCellValue(r, 0, k)
            self.inspector.SetReadOnly(r, 0)
            self.inspector.SetCellValue(r, 1, str(uiView.GetProperty(k)))
            r+=1
        self.Layout()

    def InspectorValueChanged(self, event):
        uiView = self.page.GetSelectedUIView()
        if not uiView:
            uiView = self.page.uiPage
        key = self.inspector.GetCellValue(event.GetRow(), 0)
        oldVal = uiView.GetProperty(key)
        valStr = self.inspector.GetCellValue(event.GetRow(), 1)
        val = valStr

        try:
            if isinstance(oldVal, bool):
                val = valStr[0].upper() == "T"
            elif isinstance(oldVal, int):
                val = int(valStr)
            elif isinstance(oldVal, float):
                val = float(valStr)
            elif isinstance(oldVal, list):
                val = ast.literal_eval(valStr)
        except:
            val = oldVal # On any conversion failure, use old value

        uiView.SetProperty(key, val)
        self.inspector.SetCellValue(event.GetRow(), 1, str(val))

    def UpdateHandlerForUIView(self, uiView, handlerName):
        if not uiView:
            uiView = self.page.uiPage
        if handlerName == None:
            handlerName = uiView.lastEditedHandler
        if handlerName:
            self.currentHandler = handlerName
        if uiView.GetHandler(handlerName) == None:
            self.currentHandler = list(uiView.GetHandlers().keys())[0]
        self.handlerPicker.SetItems(list(uiView.GetHandlers().keys()))
        self.handlerPicker.SetStringSelection(self.currentHandler)
        self.codeEditor.SetText(uiView.GetHandler(self.currentHandler))
        self.handlerPicker.Enable(True)
        self.codeEditor.Enable(True)
        uiView.lastEditedHandler = self.currentHandler

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
