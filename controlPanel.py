import wx
import wx.stc as stc
import wx.grid
from wx.lib import buttons # for generic button classes
from PythonEditor import PythonEditor
from uiView import UiView
from wx.lib.docview import Command


class ControlPanel(wx.Panel):
    """
    This class implements a very simple control panel for the stackWindow.
    It creates buttons for each of the colours and thickneses supported by
    the stackWindow, and event handlers to set the selected values.  There is
    also a little view that shows an example line in the selected
    values.  Nested sizers are used for layout.
    """

    BMP_SIZE = 16
    BMP_BORDER = 3

    def __init__(self, parent, ID, stackView):
        wx.Panel.__init__(self, parent, ID, style=wx.RAISED_BORDER)
        self.stackView = stackView

        numCols = 4
        spacing = 4

        btnSize = wx.Size(self.BMP_SIZE + 2*self.BMP_BORDER,
                          self.BMP_SIZE + 2*self.BMP_BORDER)

        # Make a grid of buttons for each colour.  Attach each button
        # event to self.OnSetColour.  The button ID is the same as the
        # key in the colour dictionary.
        self.clrBtns = {}
        colours = stackView.menuColours
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
        for x in range(1, stackView.maxThickness+1):
            b = buttons.GenToggleButton(self, x, str(x), size=btnSize)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            self.Bind(wx.EVT_BUTTON, self.OnSetThickness, b)
            self.tGrid.Add(b, 0)
            self.thknsBtns[x] = b
        self.thknsBtns[1].SetToggle(True)

        # Make a colour indicator view, it is registerd as a listener
        # with the stackView view so it will be notified when the settings
        # change
        self.ci = ColourIndicator(self)
        stackView.AddListener(self.ci)
        stackView.Notify()

        # ----------

        self.inspector = wx.grid.Grid(self, -1)
        self.inspector.CreateGrid(1, 2)
        self.inspector.SetRowSize(0, 24)
        self.inspector.SetColSize(0, 70)
        self.inspector.SetColSize(1, 130)
        self.inspector.SetColLabelSize(20)
        self.inspector.SetColLabelValue(0, "Inspector")
        self.inspector.SetColLabelValue(1, "Value")
        self.inspector.SetRowLabelSize(1)
        self.inspector.DisableDragRowSize()

        self.inspector.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnInspectorValueChanged)
        self.inspector.Bind(wx.EVT_KEY_DOWN, self.OnGridEnter)
        self.inspector.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGridClick)

        self.handlerPicker = wx.Choice(parent=self, id=wx.ID_ANY)
        self.handlerPicker.Enable(False)
        self.handlerPicker.Bind(wx.EVT_CHOICE, self.OnHandlerChoice)
        self.currentHandler = None

        self.codeEditor = PythonEditor(self)
        self.codeEditor.SetSize((150,2000))
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)

        self.lastSelectedUiView = None
        self.UpdateInspectorForUiView(None)
        self.UpdateHandlerForUiView(None, None)

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
            self.stackView.SelectUiView(None)
        else:
            self.box.Hide(self.drawBox)
            self.box.Show(self.editBox)

        self.Layout()
        self.stackView.SetDrawingMode(drawMode)

    def OnGridClick(self, event):
        self.inspector.SetGridCursor(event.Row, event.Col)
        if self.inspector.GetGridCursorCol() == 1:
            self.inspector.EnableCellEditControl()
        event.Skip()

    def OnGridEnter(self, event):
        if not self.inspector.IsCellEditControlShown() and \
                (event.GetKeyCode() == wx.WXK_RETURN or event.GetKeyCode() == wx.WXK_NUMPAD_ENTER):
            if self.inspector.GetGridCursorCol() == 0:
                self.inspector.SetGridCursor(self.inspector.GetGridCursorRow(), 1)
            self.inspector.EnableCellEditControl()
        else:
            event.Skip()

    def OnHandlerChoice(self, event):
        displayName = self.handlerPicker.GetItems()[self.handlerPicker.GetSelection()]
        keys = list(UiView.handlerDisplayNames.keys())
        vals = list(UiView.handlerDisplayNames.values())
        self.SaveCurrentHandler()
        self.UpdateHandlerForUiView(self.stackView.GetSelectedUiView(), keys[vals.index(displayName)])

    def UpdateForUiView(self, uiView):
        lastUi = self.lastSelectedUiView
        if uiView != lastUi:
            self.UpdateInspectorForUiView(uiView)
            self.UpdateHandlerForUiView(uiView, None)
            self.lastSelectedUiView = uiView

    def UpdatedProperty(self, uiView, key):
        if not uiView:
            uiView = self.stackView.uiCard
        lastUi = self.lastSelectedUiView
        if not lastUi:
            lastUi = self.stackView.uiCard
        if uiView == lastUi:
            keys = uiView.model.PropertyKeys()
            r = 0
            for k in keys:
                self.inspector.SetCellValue(r, 1, str(uiView.model.GetProperty(k)))
                r += 1

    def UpdateInspectorForUiView(self, uiView):
        # Catch a still-open editor and handle it before we move on to a newly selectd uiView
        if self.inspector.IsCellEditControlShown():
            ed = self.inspector.GetCellEditor(self.inspector.GetGridCursorRow(), self.inspector.GetGridCursorCol())
            val = ed.GetValue()
            self.InspectorValueChanged(self.lastSelectedUiView, self.inspector.GetGridCursorRow(), val)
            self.inspector.HideCellEditControl()

        if self.inspector.GetNumberRows() > 0:
            self.inspector.DeleteRows(0, self.inspector.GetNumberRows())
        if not uiView:
            uiView = self.stackView.uiCard
        keys = uiView.model.PropertyKeys()
        self.inspector.InsertRows(0,len(keys))
        r = 0
        for k in keys:
            self.inspector.SetCellValue(r, 0, k)
            self.inspector.SetReadOnly(r, 0)
            self.inspector.SetCellValue(r, 1, str(uiView.model.GetProperty(k)))
            if uiView.model.GetPropertyType(k) == "bool":
                editor = wx.grid.GridCellChoiceEditor(["True", "False"])
                self.inspector.SetCellEditor(r, 1, editor)

            elif uiView.model.GetPropertyType(k) == "choice":
                editor = wx.grid.GridCellChoiceEditor(uiView.model.GetPropertyChoices(k))
                self.inspector.SetCellEditor(r, 1, editor)
            r+=1
        self.Layout()

    def OnInspectorValueChanged(self, event):
        uiView = self.stackView.GetSelectedUiView()
        self.InspectorValueChanged(uiView, event.GetRow(),
                                   self.inspector.GetCellValue(event.GetRow(), 1))

    def InspectorValueChanged(self, uiView, row, valStr):
        key = self.inspector.GetCellValue(row, 0)
        oldVal = uiView.model.GetProperty(key)

        val = uiView.model.InterpretPropertyFromString(key, valStr)
        if val is not None and val != oldVal:
            if key == "name":
                val = self.stackView.uiCard.model.DeduplicateNameInCard(val, [uiView.model.GetProperty("name")])

            command = SetPropertyCommand(True, "Set Property", self, self.stackView.cardIndex, uiView.model, key, val)
            self.stackView.command_processor.Submit(command)
        else:
            self.UpdatedProperty(uiView, "")

    def UpdateHandlerForUiView(self, uiView, handlerName):
        if not uiView:
            uiView = self.stackView.uiCard
        if handlerName == None:
            handlerName = uiView.lastEditedHandler
        if handlerName:
            self.currentHandler = handlerName
        if uiView.model.GetHandler(handlerName) == None:
            self.currentHandler = list(uiView.model.GetHandlers().keys())[0]

        self.handlerPicker.SetItems([UiView.handlerDisplayNames[k] for k in uiView.model.GetHandlers().keys()])
        self.handlerPicker.SetStringSelection(UiView.handlerDisplayNames[self.currentHandler])
        self.codeEditor.SetText(uiView.model.GetHandler(self.currentHandler))
        self.codeEditor.EmptyUndoBuffer()
        self.handlerPicker.Enable(True)
        self.codeEditor.Enable(True)
        uiView.lastEditedHandler = self.currentHandler

    def SaveCurrentHandler(self):
        if self.codeEditor.HasFocus():
            uiView = self.stackView.GetSelectedUiView()
            if uiView:
                oldVal = uiView.model.GetHandler(self.currentHandler)
                newVal = self.codeEditor.GetText()

                if newVal != oldVal:
                    command = SetHandlerCommand(True, "Set Handler", self, self.stackView.cardIndex, uiView.model,
                                                self.currentHandler, newVal)
                    self.stackView.command_processor.Submit(command)

    def CodeEditorOnIdle(self, event):
        if self.currentHandler:
            self.SaveCurrentHandler()
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
        Use the event ID to get the colour, set that colour in the stackView.
        """
        colour = self.stackView.menuColours[event.GetId()]
        if colour != self.stackView.colour:
            # untoggle the old colour button
            self.clrBtns[self.stackView.colour].SetToggle(False)
        # set the new colour
        self.stackView.SetColour(colour)

    def OnSetThickness(self, event):
        """
        Use the event ID to set the thickness in the stackView.
        """
        thickness = event.GetId()
        if thickness != self.stackView.thickness:
            # untoggle the old thickness button
            self.thknsBtns[self.stackView.thickness].SetToggle(False)
        # set the new colour
        self.stackView.SetThickness(thickness)


# ----------------------------------------------------------------------

class ColourIndicator(wx.Window):
    """
    An instance of this class is used on the ControlPanel to show
    a sample of what the current stackView line will look like.
    """
    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        self.SetMinSize( (45, 45) )
        self.colour = self.thickness = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateLine(self, colour, thickness):
        """
        The stackView view calls this method any time the colour
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


class SetPropertyCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.cPanel = args[2]
        self.cardIndex = args[3]
        self.model = args[4]
        self.key = args[5]
        self.newVal = args[6]
        self.oldVal = self.model.GetProperty(self.key)
        self.hasRun = False

    def Do(self):
        self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
        if self.hasRun:
            uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
            self.cPanel.stackView.SelectUiView(uiView)
        self.model.SetProperty(self.key, self.newVal)
        self.hasRun = True
        return True

    def Undo(self):
        self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
        if self.hasRun:
            uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
            self.cPanel.stackView.SelectUiView(uiView)
        self.model.SetProperty(self.key, self.oldVal)
        return True


class SetHandlerCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.cPanel = args[2]
        self.cardIndex = args[3]
        self.model = args[4]
        self.key = args[5]
        self.newVal = args[6]
        self.oldVal = self.model.GetHandler(self.key)
        self.hasRun = False

    def Do(self):
        self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
        if self.hasRun:
            uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
            self.cPanel.stackView.SelectUiView(uiView)

        self.model.SetHandler(self.key, self.newVal)

        if self.hasRun:
            self.cPanel.UpdateHandlerForUiView(uiView, self.key)

        self.hasRun = True
        return True

    def Undo(self):
        self.cPanel.stackView.LoadCardAtIndex(self.cardIndex)
        uiView = self.cPanel.stackView.GetUiViewByModel(self.model)
        self.cPanel.stackView.SelectUiView(uiView)

        self.model.SetHandler(self.key, self.oldVal)

        self.cPanel.UpdateHandlerForUiView(uiView, self.key)
        return True
