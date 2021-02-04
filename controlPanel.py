import wx
import wx.grid
import wx.html
from tools import *
from commands import *
from wx.lib import buttons # for generic button classes
from PythonEditor import PythonEditor
from uiView import UiView
from embeddedImages import embeddedImages
from helpData import HelpData

class ControlPanel(wx.Panel):
    """
    This class implements a very simple control panel for the stackWindow.
    It creates buttons for each of the colors and thickneses supported by
    the stackWindow, and event handlers to set the selected values.  There is
    also a little view that shows an example line in the selected
    values.  Nested sizers are used for layout.
    """

    BMP_SIZE = 25
    BMP_BORDER = 2

    toolNames = ["hand", "button", "field", "label", "image",
                 "pen", "oval", "rect", "round_rect", "line"]
    tooltips = ["Hand", "Button", "Text Field", "Text Label", "Image",
                "Pen", "Oval", "Rectangle", "Round Rectangle", "Line"]

    def __init__(self, parent, ID, stackView):
        wx.Panel.__init__(self, parent, ID, style=wx.RAISED_BORDER)
        self.stackView = stackView
        self.penColor = wx.Colour("black")
        self.fillColor = wx.Colour("white")
        self.penThickness = 4
        numCols = 10
        spacing = 6

        btnSize = wx.Size(self.BMP_SIZE + 2*self.BMP_BORDER,
                          self.BMP_SIZE + 2*self.BMP_BORDER)

        # Make a grid of buttons for the tools.
        self.toolBtns = {}
        toolBitmaps = {}
        for k,v in embeddedImages.items():
            toolBitmaps[k] = v.GetBitmap()

        self.toolGrid = wx.GridSizer(cols=numCols, hgap=3, vgap=2)
        for name in self.toolNames:
            b = buttons.GenBitmapToggleButton(self, self.toolNames.index(name), toolBitmaps[name], size=btnSize)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            b.Bind(wx.EVT_BUTTON, self.OnSetTool)
            self.toolGrid.Add(b, 0)
            self.toolBtns[name] = b
        self.toolBtns["hand"].SetToggle(True)

        self.cGrid = wx.GridSizer(cols=2, hgap=2, vgap=2)
        l = wx.StaticText(parent=self, label="Pen Color:")
        l.SetFont(wx.Font(wx.FontInfo(12).Weight(wx.FONTWEIGHT_BOLD).Family(wx.FONTFAMILY_DEFAULT)))
        self.cGrid.Add(l, wx.SizerFlags().CenterVertical())
        self.penColorPicker = wx.ColourPickerCtrl(parent=self, colour="black", style=wx.CLRP_SHOW_ALPHA, name="Pen")
        self.penColorPicker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnSetPenColor)
        self.cGrid.Add(self.penColorPicker)
        l = wx.StaticText(parent=self, label="Fill Color:")
        l.SetFont(wx.Font(wx.FontInfo(12).Weight(wx.FONTWEIGHT_BOLD).Family(wx.FONTFAMILY_DEFAULT)))
        self.cGrid.Add(l, wx.SizerFlags().CenterVertical())
        self.fillColorPicker = wx.ColourPickerCtrl(parent=self, colour="white", style=wx.CLRP_SHOW_ALPHA, name="Fill")
        self.fillColorPicker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnSetFillColor)
        self.cGrid.Add(self.fillColorPicker)

        # Make a grid of buttons for the thicknesses.  Attach each button
        # event to self.OnSetThickness.  The button ID is the same as the
        # thickness value.
        self.thknsBtns = {}
        self.tGrid = wx.GridSizer(cols=numCols, hgap=2, vgap=2)
        for x in [1,2,4,8,16]:
            bmp = self.MakeLineBitmap(x)
            b = buttons.GenBitmapToggleButton(self, x, bmp, size=btnSize)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            b.Bind(wx.EVT_BUTTON, self.OnSetThickness)
            self.tGrid.Add(b, 0)
            self.thknsBtns[x] = b
        self.thknsBtns[4].SetToggle(True)

        # Make a color indicator view, it is registerd as a listener
        # with the stackView view so it will be notified when the settings
        # change
        self.ci = ColorIndicator(self)
        self.ci.UpdateLine(self.penColor, self.penThickness)

        # ----------

        self.inspector = wx.grid.Grid(self, -1)
        self.inspector.CreateGrid(1, 2)
        self.inspector.SetRowSize(0, 24)
        self.inspector.SetColSize(0, 100)
        self.inspector.SetColLabelSize(20)
        self.inspector.SetColLabelValue(0, "")
        self.inspector.SetColLabelValue(1, "Value")
        self.inspector.SetRowLabelSize(1)
        self.inspector.DisableDragRowSize()
        self.inspector.DisableDragColSize()

        self.inspector.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnInspectorValueChanged)
        self.inspector.Bind(wx.EVT_KEY_DOWN, self.OnGridEnter)
        self.inspector.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGridClick)
        self.inspector.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridCellSelected)
        self.inspector.Bind(wx.EVT_SIZE, self.OnGridResized)

        self.panelHelp = wx.html.HtmlWindow(self, size=(200, 70), style=wx.BORDER_SUNKEN)

        self.handlerPicker = wx.Choice(parent=self)
        self.handlerPicker.Enable(False)
        self.handlerPicker.Bind(wx.EVT_CHOICE, self.OnHandlerChoice)
        self.currentHandler = None

        self.codeEditor = PythonEditor(self, style=wx.BORDER_SUNKEN)
        self.codeEditor.SetSize((150,2000))
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
        self.codeEditor.Bind(wx.EVT_SET_FOCUS, self.CodeEditorFocused)

        self.lastSelectedUiView = None
        self.UpdateInspectorForUiViews([])
        self.UpdateHandlerForUiViews([], None)

        # ----------

        self.drawBox = wx.BoxSizer(wx.VERTICAL)
        self.drawBox.Add(self.cGrid, 0, wx.LEFT, spacing)
        self.drawBox.Add(self.tGrid, 0, wx.LEFT, spacing)
        self.drawBox.Add(self.ci, 0, wx.EXPAND|wx.ALL, spacing)

        self.editBox = wx.BoxSizer(wx.VERTICAL)
        self.editBox.Add(self.inspector, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.AddSpacer(4)
        self.editBox.Add(self.panelHelp, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.AddSpacer(4)
        self.editBox.Add(self.handlerPicker, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.Add(self.codeEditor, 1, wx.EXPAND|wx.ALL, spacing)
        self.editBox.SetSizeHints(self)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.toolGrid, 0, wx.LEFT, spacing)
        self.box.Add(self.drawBox, 0, wx.EXPAND|wx.ALL, spacing)
        self.box.Add(self.editBox, 1, wx.EXPAND|wx.ALL, spacing)
        self.box.SetSizeHints(self)

        self.UpdateHelpText("-")
        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        i = 0
        for k,b in self.toolBtns.items():
            tooltip = wx.ToolTip(self.tooltips[i])
            tooltip.SetAutoPop(2000)
            tooltip.SetDelay(200)
            tooltip.Enable(True)
            b.SetToolTip(tooltip)
            i += 1
        wx.ToolTip.Enable(True)

    def ShowContextHelp(self, show):
        self.panelHelp.Show(show)
        self.box.Layout()

    def ToggleContextHelp(self):
        if self.IsContextHelpShown():
            self.ShowContextHelp(False)
        else:
            self.ShowContextHelp(True)

    def IsContextHelpShown(self):
        return self.panelHelp.IsShown()

    def UpdateHelpText(self, helpText):
        if helpText:
            self.panelHelp.SetPage("<body bgColor='#EEEEEE'>" + helpText + "</body>")
        else:
            self.panelHelp.SetPage("<body bgColor='#EEEEEE'></body>")
        self.panelHelp.SetSize(self.panelHelp.Size.x, self.panelHelp.GetVirtualSize().y)
        self.editBox.Layout()
        self.box.Layout()

    def OnGridClick(self, event):
        self.inspector.SetGridCursor(event.Row, event.Col)
        self.inspector.ClearSelection()
        if self.inspector.GetGridCursorCol() == 1:
            self.inspector.EnableCellEditControl()

    def OnGridCellSelected(self, event):
        self.inspector.ClearSelection()
        uiView = self.lastSelectedUiView
        if uiView:
            keys = uiView.model.PropertyKeys()
            helpText = HelpData.GetPropertyHelp(uiView, keys[event.GetRow()])
            self.UpdateHelpText(helpText)
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
        displayName = displayName.strip().replace("def ", "")
        keys = list(UiView.handlerDisplayNames.keys())
        vals = list(UiView.handlerDisplayNames.values())
        self.SaveCurrentHandler()
        self.UpdateHandlerForUiViews(self.stackView.GetSelectedUiViews(), keys[vals.index(displayName)])

    def UpdateForUiViews(self, uiViews):
        if len(uiViews) == 1:
            lastUi = self.lastSelectedUiView
            if uiViews[0] != lastUi:
                self.UpdateInspectorForUiViews(uiViews)
                self.UpdateHandlerForUiViews(uiViews, None)
                self.lastSelectedUiView = uiViews[0]
        else:
            self.UpdateInspectorForUiViews(uiViews)
            self.UpdateHandlerForUiViews(uiViews, None)
            self.lastSelectedUiView = None

    def UpdatedProperty(self, uiView, key):
        lastUi = self.lastSelectedUiView
        if not lastUi:
            lastUi = self.stackView.uiCard
        if uiView == lastUi:
            keys = uiView.model.PropertyKeys()
            r = 0
            for k in keys:
                if uiView.model.GetPropertyType(k) in ["point", "floatpoint", "size"]:
                    l = list(uiView.model.GetProperty(k))
                    l = [int(i) if math.modf(i)[0] == 0 else i for i in l]
                    self.inspector.SetCellValue(r, 1, str(l))
                else:
                    self.inspector.SetCellValue(r, 1, str(uiView.model.GetProperty(k)))
                r += 1

    def UpdateInspectorForUiViews(self, uiViews):
        # Catch a still-open editor and handle it before we move on to a newly selected uiView
        if self.inspector.IsCellEditControlShown():
            ed = self.inspector.GetCellEditor(self.inspector.GetGridCursorRow(), self.inspector.GetGridCursorCol())
            val = ed.GetValue()
            self.InspectorValueChanged(self.lastSelectedUiView, self.inspector.GetGridCursorRow(), val)
            self.inspector.HideCellEditControl()

        if self.inspector.GetNumberRows() > 0:
            self.inspector.DeleteRows(0, self.inspector.GetNumberRows())

        if len(uiViews) != 1:
            self.inspector.Enable(False)
            self.inspector.SetColLabelValue(0, "Objects" if len(uiViews) else "None")
            return

        self.inspector.Enable(True)
        uiView = uiViews[0]
        self.inspector.SetColLabelValue(0, uiView.model.GetDisplayType())
        keys = uiView.model.PropertyKeys()
        self.inspector.InsertRows(0,len(keys))
        r = 0
        for k in keys:
            self.inspector.SetCellValue(r, 0, k)
            self.inspector.SetReadOnly(r, 0)
            if uiView.model.GetPropertyType(k) in ["point", "floatpoint", "size"]:
                l = list(uiView.model.GetProperty(k))
                l = [int(i) if math.modf(i)[0] == 0 else i for i in l]
                self.inspector.SetCellValue(r, 1, str(l))
            else:
                self.inspector.SetCellValue(r, 1, str(uiView.model.GetProperty(k)))
            if uiView.model.GetPropertyType(k) == "bool":
                editor = wx.grid.GridCellChoiceEditor(["True", "False"])
                self.inspector.SetCellEditor(r, 1, editor)
            elif uiView.model.GetPropertyType(k) == "choice":
                editor = wx.grid.GridCellChoiceEditor(uiView.model.GetPropertyChoices(k))
                self.inspector.SetCellEditor(r, 1, editor)
            elif uiView.model.GetPropertyType(k) == "color":
                self.inspector.SetCellRenderer(r, 1, GridCellColorRenderer())
                self.inspector.SetCellEditor(r, 1, GridCellColorEditor(self))
            r+=1
        self.Layout()

    def OnInspectorValueChanged(self, event):
        uiView = self.stackView.GetSelectedUiViews()[0]
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

    def OnGridResized(self, event):
        width, height = self.inspector.GetSize()
        width = width - self.inspector.GetColSize(0) - 1
        if width < 0: width = 0
        self.inspector.SetColSize(1, width)
        event.Skip()

    def UpdateHandlerForUiViews(self, uiViews, handlerName):
        if len(uiViews) != 1:
            self.codeEditor.SetText("")
            self.codeEditor.Enable(False)
            self.handlerPicker.Enable(False)
            return

        self.codeEditor.Enable(True)
        self.handlerPicker.Enable(True)
        uiView = uiViews[0]

        helpText = HelpData.GetHandlerHelp(uiView, handlerName)
        self.UpdateHelpText(helpText)

        if handlerName == None:
            handlerName = uiView.lastEditedHandler
        if not handlerName:
            for k in uiView.model.GetHandlers().keys():
                if uiView.model.GetHandler(k):
                    handlerName = k
                    break
            else:
                handlerName = list(uiView.model.GetHandlers().keys())[0]
        if handlerName:
            self.currentHandler = handlerName

        displayNames = []
        for k in uiView.model.GetHandlers().keys():
            decorator = "def " if uiView.model.GetHandler(k) else "       "
            displayNames.append(decorator + UiView.handlerDisplayNames[k])
        self.handlerPicker.SetItems(displayNames)

        self.handlerPicker.SetSelection(list(uiView.model.GetHandlers().keys()).index(self.currentHandler))
        self.codeEditor.SetText(uiView.model.GetHandler(self.currentHandler))
        self.codeEditor.EmptyUndoBuffer()
        self.handlerPicker.Enable(True)
        self.codeEditor.Enable(True)
        uiView.lastEditedHandler = self.currentHandler

    def SaveCurrentHandler(self):
        if self.codeEditor.HasFocus():
            uiView = self.stackView.GetSelectedUiViews()[0]
            if uiView:
                oldVal = uiView.model.GetHandler(self.currentHandler)
                newVal = self.codeEditor.GetText()

                if newVal != oldVal:
                    command = SetHandlerCommand(True, "Set Handler", self, self.stackView.cardIndex, uiView.model,
                                                self.currentHandler, newVal)
                    self.stackView.command_processor.Submit(command)

    def CodeEditorFocused(self, event):
        helpText = HelpData.GetHandlerHelp(self.lastSelectedUiView, self.currentHandler)
        self.UpdateHelpText(helpText)
        event.Skip()

    def CodeEditorOnIdle(self, event):
        if self.currentHandler:
            self.SaveCurrentHandler()
        event.Skip()

    def MakeBitmap(self, color):
        """
        We can create a bitmap of whatever we want by simply selecting
        it into a wx.MemoryDC and drawing on it.  In this case we just set
        a background brush and clear the dc.
        """
        bmp = wx.Bitmap(self.BMP_SIZE, self.BMP_SIZE)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(color))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def MakeLineBitmap(self, thickness):
        bmp = wx.Bitmap(self.BMP_SIZE, thickness)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush("black"))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def OnSetTool(self, event):
        toolId = event.GetId()
        toolName = self.toolNames[toolId]
        self.SetToolByName(toolName)
        self.stackView.SetFocus()

    def SetToolByName(self, toolName):
        if self.stackView.tool:
            self.toolBtns[self.stackView.tool.name].SetToggle(toolName == self.stackView.tool.name)
        self.toolBtns[toolName].SetToggle(True)

        if not self.stackView.tool or toolName != self.stackView.tool.name:
            tool = BaseTool.ToolFromName(toolName, self.stackView)
            self.stackView.SetTool(tool)

            if tool.name == "pen" or tool.name == "oval" or tool.name == "rect" or tool.name == "line" or tool.name == "round_rect":
                self.box.Show(self.drawBox)
                self.box.Hide(self.editBox)
                self.stackView.SelectUiView(None)
                tool.SetPenColor(self.penColor)
                tool.SetFillColor(self.fillColor)
                tool.SetThickness(self.penThickness)
            elif tool.name == "hand":
                self.box.Hide(self.drawBox)
                self.box.Show(self.editBox)
            else:
                self.box.Hide(self.drawBox)
                self.box.Hide(self.editBox)


            self.Layout()

    def OnSetPenColor(self, event):
        newColor = event.GetColour()
        self.penColor = newColor
        self.ci.UpdateLine(self.penColor, self.penThickness)
        self.stackView.tool.SetPenColor(self.penColor)

    def OnSetFillColor(self, event):
        newColor = event.GetColour()
        self.fillColor = newColor
        self.stackView.tool.SetFillColor(self.fillColor)

    def OnSetThickness(self, event):
        """
        Use the event ID to set the thickness in the stackView.
        """
        newThickness = event.GetId()
        # untoggle the old thickness button
        self.thknsBtns[self.penThickness].SetToggle(newThickness == self.penThickness)
        # set the new color
        self.penThickness = newThickness
        self.ci.UpdateLine(self.penColor, self.penThickness)
        self.stackView.tool.SetThickness(self.penThickness)


# ----------------------------------------------------------------------

class ColorIndicator(wx.Window):
    """
    An instance of this class is used on the ControlPanel to show
    a sample of what the current stackView line will look like.
    """
    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        self.SetMinSize( (45, 45) )
        self.color = self.thickness = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateLine(self, color, thickness):
        """
        The stackView view calls this method any time the color
        or line thickness changes.
        """
        self.color = color
        self.thickness = thickness
        self.Refresh()  # generate a paint event

    def OnPaint(self, event):
        """
        This method is called when all or part of the view needs to be
        redrawn.
        """
        dc = wx.PaintDC(self)
        if self.color:
            sz = self.GetClientSize()
            pen = wx.Pen(self.color, self.thickness)
            dc.SetPen(pen)
            dc.DrawLine(10, int(sz.height/2), int(sz.width-10), int(sz.height/2))


COLOR_PATCH_WIDTH = 70

class GridCellColorRenderer(wx.grid.GridCellStringRenderer):
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text = grid.GetCellValue(row, col)
        color = wx.Colour(text)
        if not color.IsOk(): color = wx.Colour('white')

        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        else:
            bg = attr.GetBackgroundColour()
            fg = attr.GetTextColour()
        dc.SetTextBackground(bg)
        dc.SetTextForeground(fg)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(bg, wx.SOLID))
        dc.DrawRectangle(rect)
        dc.SetPen(wx.Pen('black', 1, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-COLOR_PATCH_WIDTH, rect.Top, COLOR_PATCH_WIDTH, rect.Height))

        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)


class GridCellColorEditor(wx.grid.GridCellTextEditor):
    def __init__(self, cPanel):
        super().__init__()
        self.cPanel = cPanel
        self.grid = cPanel.inspector

    def StartingClick(self):
        self.row = self.grid.GetGridCursorRow()
        self.col = self.grid.GetGridCursorCol()
        text = self.grid.GetCellValue(self.row, self.col)
        x,y = self.grid.ScreenToClient(wx.GetMousePosition())
        if x > self.grid.GetSize().Width - COLOR_PATCH_WIDTH:
            data = wx.ColourData()
            data.SetColour(text)
            data.SetChooseAlpha(True)
            dlg = wx.ColourDialog(self.grid, data)
            if dlg.ShowModal() == wx.ID_OK:
                color = dlg.GetColourData().GetColour().GetAsString(flags=wx.C2S_HTML_SYNTAX)
                self.UpdateColor(color)

    def UpdateColor(self, color):
        self.grid.SetCellValue(self.row, self.col, color)
        self.cPanel.InspectorValueChanged(self.cPanel.lastSelectedUiView, self.row, color)
