import wx
import wx.grid
import wx.html
import os
import mediaSearchDialogs
from tools import *
from commands import *
from wx.lib import buttons # for generic button classes
from wx.lib.resizewidget import ResizeWidget, EVT_RW_LAYOUT_NEEDED
from pythonEditor import PythonEditor
from uiView import UiView
from embeddedImages import embeddedImages
from helpData import HelpData


class ControlPanel(wx.Panel):
    """
    This class implements the control panel for the designer app.  It includes a tool palette for choosing a tool.
    It includes thickness and pen and fill colors for drawing shapes, and an inspector and code editor for editing
    objects.
    """

    BMP_SIZE = 25
    BMP_BORDER = 4

    toolNames = ["hand", "button", "field", "label", "image",
                 "pen", "oval", "rect", "roundrect", "poly", "line"]
    tooltips = ["Hand (Esc)", "Button (B)", "Text Field (F)", "Text Label (T)", "Image (I)",
                "Pen (P)", "Oval (O)", "Rectangle (R)", "Round Rectangle (D)", "Polygon (G)", "Line (L)"]

    def __init__(self, parent, ID, stackManager):
        wx.Panel.__init__(self, parent, ID, style=wx.RAISED_BORDER)
        self.stackManager = stackManager
        self.penColor = "black"
        self.fillColor = "white"
        self.penThickness = 4
        self.isContextHelpEnabled = True
        numCols = 11
        spacing = 6

        btnSize = wx.Size(self.BMP_SIZE + 2*self.BMP_BORDER,
                          self.BMP_SIZE + 2*self.BMP_BORDER)

        # Make a grid of buttons for the tools.
        self.toolBtns = {}
        toolBitmaps = {}
        for k,v in embeddedImages.items():
            toolBitmaps[k] = v.GetBitmap()

        self.toolGrid = wx.GridSizer(cols=numCols, hgap=3, vgap=2)
        for i in range(len(self.toolNames)):
            name = self.toolNames[i]
            b = buttons.GenBitmapToggleButton(self, self.toolNames.index(name), toolBitmaps[name], size=btnSize)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            b.Bind(wx.EVT_BUTTON, self.OnSetTool)
            b.Bind(wx.EVT_ENTER_WINDOW, self.OnToolEnter)
            b.Bind(wx.EVT_LEAVE_WINDOW, self.OnToolExit)
            if wx.Platform == "__WXMSW__":
                tip = wx.ToolTip(self.tooltips[i])
                tip.SetDelay(100)
                b.SetToolTip(tip)
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
        # with the stackManager view so it will be notified when the settings
        # change
        self.ci = ColorIndicator(self)
        self.ci.UpdateLine(wx.Colour(self.penColor), self.penThickness)

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
        self.inspector.SetSelectionMode(wx.grid.Grid.GridSelectNone)

        self.inspector.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnInspectorValueChanged)
        self.inspector.Bind(wx.EVT_KEY_DOWN, self.OnGridEnter)
        self.inspector.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGridClick)
        self.inspector.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridCellSelected)
        self.inspector.Bind(wx.EVT_SIZE, self.OnGridResized)

        self.panelHelp = wx.html.HtmlWindow(self, size=(200, 50), style=wx.BORDER_SUNKEN)

        self.helpResizer = ResizeWidget(self)
        self.helpResizer.SetColors(pen='blue', fill='blue')
        self.helpResizer.SetManagedChild(self.panelHelp)
        self.panelHelp.Show()

        self.handlerPicker = wx.Choice(parent=self)
        self.handlerPicker.Enable(False)
        self.handlerPicker.Bind(wx.EVT_CHOICE, self.OnHandlerChoice)
        self.currentHandler = None

        self.codeEditor = PythonEditor(self, self, self.stackManager, style=wx.BORDER_SUNKEN)
        self.codeEditor.Bind(wx.EVT_IDLE, self.CodeEditorOnIdle)
        self.codeEditor.Bind(wx.EVT_SET_FOCUS, self.CodeEditorFocused)

        self.lastSelectedUiViews = []
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
        self.editBox.Add(self.helpResizer, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.AddSpacer(4)
        self.editBox.Add(self.handlerPicker, 0, wx.EXPAND|wx.ALL, spacing)
        self.editBox.Add(self.codeEditor, 1, wx.EXPAND|wx.ALL, spacing)
        self.editBox.SetSizeHints(self)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.toolGrid, 0, wx.LEFT, spacing)
        self.box.Add(self.drawBox, 0, wx.EXPAND|wx.ALL, spacing)
        self.box.Add(self.editBox, 1, wx.EXPAND|wx.ALL, spacing)
        self.box.SetSizeHints(self)

        self.helpResizer.Bind(EVT_RW_LAYOUT_NEEDED, self.OnRwLayoutNeeded)

        self.UpdateHelpText("")
        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.toolTip = None

    def OnRwLayoutNeeded(self, event):
        self.box.Layout()

    def ShowContextHelp(self, show):
        if self.stackManager.tool.name == "hand":
            self.helpResizer.Show(show)
            self.box.Layout()
        self.isContextHelpEnabled = show

    def ToggleContextHelp(self):
        self.ShowContextHelp(not self.isContextHelpEnabled)

    def IsContextHelpShown(self):
        return self.isContextHelpEnabled

    def UpdateHelpText(self, helpText):
        if helpText:
            self.panelHelp.SetPage("<body bgColor='#EEEEEE'>" + helpText + "</body>")
        else:
            self.panelHelp.SetPage("<body bgColor='#EEEEEE'></body>")

    def OnGridClick(self, event):
        self.inspector.SetGridCursor(event.Row, event.Col)
        event.Skip()

    def SelectInInspectorForPropertyName(self, key, selectStart, selectEnd):
        if len(self.lastSelectedUiViews) == 1:
            lastUi = self.lastSelectedUiViews[0]
            keys = lastUi.model.PropertyKeys()
            self.inspector.SetGridCursor(keys.index(key), 1)
            editor = self.inspector.GetCellEditor(keys.index(key), 1)
            self.inspector.EnableCellEditControl(True)
            control = editor.GetControl()
            control.SetSelection(selectStart, selectEnd)

    def GetInspectorSelection(self):
        if len(self.lastSelectedUiViews) == 1:
            if self.inspector.IsCellEditControlShown():
                row = self.inspector.GetGridCursorRow()
                editor = self.inspector.GetCellEditor(row, 1)
                control = editor.GetControl()
                if control:
                    start, end = control.GetSelection()
                    text = control.GetStringSelection()
                    return (start, end, text)
        return (None, None, None)

    def OnGridCellSelected(self, event):
        if len(self.lastSelectedUiViews) > 0:
            uiView = self.lastSelectedUiViews[0]
            if uiView:
                key = self.inspector.GetCellValue(event.GetRow(), 0)
                helpText = HelpData.GetPropertyHelp(uiView, key)
                self.UpdateHelpText(helpText)
        event.Skip()

    def OnGridEnter(self, event):
        if not self.inspector.IsCellEditControlShown() and \
                (event.GetKeyCode() == wx.WXK_RETURN or event.GetKeyCode() == wx.WXK_NUMPAD_ENTER):
            if self.inspector.GetGridCursorCol() == 0:
                self.inspector.SetGridCursor(self.inspector.GetGridCursorRow(), 1)
            self.inspector.EnableCellEditControl(True)
        else:
            event.Skip()
            if event.GetKeyCode() != wx.WXK_TAB:
                event.StopPropagation()

    def OnHandlerChoice(self, event):
        displayName = self.handlerPicker.GetItems()[self.handlerPicker.GetSelection()]
        displayName = displayName.strip().replace("def ", "")
        keys = list(UiView.handlerDisplayNames.keys())
        vals = list(UiView.handlerDisplayNames.values())
        self.SaveCurrentHandler()
        self.UpdateHandlerForUiViews(self.stackManager.GetSelectedUiViews(), keys[vals.index(displayName)])
        self.codeEditor.SetFocus()

    def SelectInCodeForHandlerName(self, key, selectStart, selectEnd):
        self.SaveCurrentHandler()
        self.UpdateHandlerForUiViews(self.stackManager.GetSelectedUiViews(), key)
        self.codeEditor.SetSelection(selectStart, selectEnd)
        self.codeEditor.ScrollRange(selectStart, selectEnd)
        self.codeEditor.SetFocus()

    def GetCodeEditorSelection(self):
        start, end = self.codeEditor.GetSelection()
        text = self.codeEditor.GetSelectedText()
        return (start, end, text)

    def UpdateForUiViews(self, uiViews):
        if len(uiViews) > 0:
            if uiViews != self.lastSelectedUiViews:
                self.UpdateInspectorForUiViews(uiViews)
                self.lastSelectedUiViews = uiViews.copy()
                self.UpdateHandlerForUiViews(uiViews, None)
        else:
            self.UpdateInspectorForUiViews([])
            self.UpdateHandlerForUiViews([], None)
            self.UpdateHelpText("")
            self.lastSelectedUiViews = []

    def UpdatedProperty(self, uiView, key):
        if len(self.lastSelectedUiViews) == 1 and uiView == self.lastSelectedUiViews[0]:
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
            self.inspector.Refresh()

    def UpdateInspectorForUiViews(self, uiViews):
        # Catch a still-open editor and handle it before we move on to a newly selected uiView
        if self.inspector.IsCellEditControlShown():
            ed = self.inspector.GetCellEditor(self.inspector.GetGridCursorRow(), self.inspector.GetGridCursorCol())
            val = ed.GetValue()
            self.InspectorValueChanged(self.inspector.GetGridCursorRow(), val)
            self.inspector.HideCellEditControl()

        if self.inspector.GetNumberRows() > 0:
            self.inspector.DeleteRows(0, self.inspector.GetNumberRows())

        if len(uiViews) == 0:
            self.inspector.Enable(False)
            self.inspector.SetColLabelValue(0, "None")
            self.inspector.InsertRows(0, 3)
            self.Layout()
            return

        if len(uiViews) == 1:
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

                renderer = None
                editor = None
                if uiView.model.GetPropertyType(k) == "bool":
                    editor = wx.grid.GridCellChoiceEditor(["True", "False"])
                elif uiView.model.GetPropertyType(k) == "choice":
                    editor = wx.grid.GridCellChoiceEditor(uiView.model.GetPropertyChoices(k))
                elif uiView.model.GetPropertyType(k) == "color":
                    editor = GridCellColorEditor(self)
                    renderer = GridCellColorRenderer()
                elif uiView.model.GetPropertyType(k) == "file":
                    editor = GridCellImageFileEditor(self)
                    renderer = GridCellImageFileRenderer()

                if renderer:
                    self.inspector.SetCellRenderer(r, 1, renderer)
                if editor:
                    self.inspector.SetCellEditor(r, 1, editor)
                r+=1

        if len(uiViews) > 1:
            self.inspector.Enable(True)
            self.inspector.SetColLabelValue(0, "Objects")
            keys = uiViews[0].model.PropertyKeys().copy()
            keys.remove("name")
            # Only show properties that exist for all selected objects
            for uiView in uiViews[1:]:
                oKeys = uiView.model.PropertyKeys()
                keys = [k for k in keys if k in oKeys]
            self.inspector.InsertRows(0, len(keys))
            r = 0
            for k in keys:
                self.inspector.SetCellValue(r, 0, k)
                self.inspector.SetReadOnly(r, 0)
                val = uiViews[0].model.GetProperty(k)
                # Only show values for properties that are the same for all selected objects
                for ui in uiViews[1:]:
                    if val != ui.model.GetProperty(k):
                        val = None
                        break
                if val is not None:
                    if uiViews[0].model.GetPropertyType(k) in ["point", "floatpoint", "size"]:
                        l = list(val)
                        l = [int(i) if math.modf(i)[0] == 0 else i for i in l]
                        self.inspector.SetCellValue(r, 1, str(l))
                    else:
                        self.inspector.SetCellValue(r, 1, str(val))
                else:
                    self.inspector.SetCellValue(r, 1, "")

                renderer = None
                editor = None
                if uiViews[0].model.GetPropertyType(k) == "bool":
                    editor = wx.grid.GridCellChoiceEditor(["True", "False"])
                elif uiViews[0].model.GetPropertyType(k) == "choice":
                    editor = wx.grid.GridCellChoiceEditor(uiViews[0].model.GetPropertyChoices(k))
                elif uiViews[0].model.GetPropertyType(k) == "color":
                    editor = GridCellColorEditor(self)
                    renderer = GridCellColorRenderer()
                elif uiViews[0].model.GetPropertyType(k) == "file":
                    editor = GridCellImageFileEditor(self)
                    renderer = GridCellImageFileRenderer()

                if renderer:
                    self.inspector.SetCellRenderer(r, 1, renderer)
                if editor:
                    self.inspector.SetCellEditor(r, 1, editor)
                r += 1

        self.Layout()

    def OnInspectorValueChanged(self, event):
        self.InspectorValueChanged(event.GetRow(),
                                   self.inspector.GetCellValue(event.GetRow(), 1))

    def InspectorValueChanged(self, row, valStr):
        key = self.inspector.GetCellValue(row, 0)
        if len(self.lastSelectedUiViews) == 1:
            uiView = self.lastSelectedUiViews[0]
            oldVal = uiView.model.GetProperty(key)
            val = uiView.model.InterpretPropertyFromString(key, valStr)

            if key == "file":
                uiView.ClearCachedData()

            if val is not None and val != oldVal:
                needsUpdate = False
                if key == "name":
                    origVal = val
                    if uiView.model.type == "card":
                        existingNames = [m.GetProperty("name") for m in self.stackManager.stackModel.childModels]
                        existingNames.remove(uiView.model.GetProperty("name"))
                        val = uiView.model.DeduplicateName(val, existingNames)
                    else:
                        val = self.stackManager.uiCard.model.DeduplicateNameInCard(val, [uiView.model.GetProperty("name")])
                    if val != origVal:
                        needsUpdate = True

                if key == "text":
                    val = val.replace('\r', '\n')
                command = SetPropertyCommand(True, "Set Property", self, self.stackManager.cardIndex, uiView.model, key, val)
                self.stackManager.command_processor.Submit(command)
                if needsUpdate:
                    self.UpdatedProperty(uiView, "")
            else:
                self.UpdatedProperty(uiView, "")
        else: # Multiple views selected
            val = self.lastSelectedUiViews[0].model.InterpretPropertyFromString(key, valStr)
            if val is not None:
                if key == "text":
                    val = val.replace('\r', '\n')
                commands = []
                for uiView in self.lastSelectedUiViews:
                    if key == "file":
                        uiView.ClearCachedData()

                    oldVal = uiView.model.GetProperty(key)
                    if val != oldVal:
                        commands.append(SetPropertyCommand(True, "Set Property", self, self.stackManager.cardIndex,
                                                           uiView.model, key, val))
                if len(commands):
                    self.stackManager.command_processor.Submit(CommandGroup(True, "Set Property", self.stackManager,
                                                                            commands, [ui.model for ui in self.lastSelectedUiViews]))

    def OnGridResized(self, event):
        width, height = self.inspector.GetSize()
        width = width - self.inspector.GetColSize(0) - 1
        if width < 0: width = 0
        self.inspector.SetColSize(1, width)
        event.Skip()

    def UpdateHandlerForUiViews(self, uiViews, handlerName):
        if len(uiViews) != 1:
            self.codeEditor.SetupWithText("")
            self.codeEditor.Enable(False)
            self.handlerPicker.Enable(False)
            self.codeEditor.currentModel = None
            self.codeEditor.currentHandler = None
            return

        if len(self.lastSelectedUiViews) == 0 or uiViews[0] != self.lastSelectedUiViews[0]:
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
                handlerName = uiView.model.initialEditHandler
        if handlerName:
            self.currentHandler = handlerName

        displayNames = []
        for k in uiView.model.GetHandlers().keys():
            decorator = "def " if uiView.model.GetHandler(k) else "       "
            displayNames.append(decorator + UiView.handlerDisplayNames[k])
        self.handlerPicker.SetItems(displayNames)

        self.handlerPicker.SetSelection(list(uiView.model.GetHandlers().keys()).index(self.currentHandler))
        self.codeEditor.SetupWithText(uiView.model.GetHandler(self.currentHandler))
        self.lastCursorSel = self.codeEditor.GetSelection()
        self.codeEditor.EmptyUndoBuffer()
        self.handlerPicker.Enable(True)
        self.codeEditor.Enable(True)
        self.codeEditor.currentModel = uiView.model
        self.codeEditor.currentHandler = self.currentHandler
        self.stackManager.analyzer.RunAnalysis()
        uiView.lastEditedHandler = self.currentHandler

    def SaveCurrentHandler(self):
        if self.codeEditor.HasFocus():
            uiView = self.stackManager.GetSelectedUiViews()[0]
            if uiView:
                oldVal = uiView.model.GetHandler(self.currentHandler)
                newVal = self.codeEditor.GetText()
                newCursorSel = self.codeEditor.GetSelection()

                if newVal != oldVal:
                    command = SetHandlerCommand(True, "Set Handler", self, self.stackManager.cardIndex, uiView.model,
                                                self.currentHandler, newVal, self.lastCursorSel, newCursorSel)
                    self.stackManager.command_processor.Submit(command)
                self.lastCursorSel = newCursorSel

    def CodeEditorFocused(self, event):
        helpText = None
        if len(self.lastSelectedUiViews) == 1:
            helpText = HelpData.GetHandlerHelp(self.lastSelectedUiViews[0], self.currentHandler)
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

    def OnToolEnter(self, event):
        if self.toolTip:
            self.toolTip.Destroy()

        if wx.Platform != "__WXMSW__":
            toolId = event.GetId()
            toolTip = self.tooltips[toolId]
            button = event.GetEventObject()
            pos = button.GetRect().BottomLeft + wx.Size(0, -2)
            tipBg = wx.Window(self, pos=pos + (button.GetSize().Width/2, -1))
            tipBg.Enable(False)
            tipBg.SetBackgroundColour('black')
            tip = wx.StaticText(tipBg, pos=wx.Point(1, 1), label=toolTip)
            tip.Enable(False)
            tip.SetForegroundColour('black')
            tip.SetBackgroundColour('white')
            tipBg.SetSize(tip.GetSize()+(2, 2))
            self.toolTip = tipBg
            event.Skip()

    def OnToolExit(self, event):
        if self.toolTip:
            self.toolTip.Destroy()
            self.toolTip = None
            self.inspector.Refresh()
        event.Skip()

    def OnSetTool(self, event):
        toolId = event.GetId()
        toolName = self.toolNames[toolId]
        self.SetToolByName(toolName)

    def SetToolByName(self, toolName):
        if self.stackManager.tool:
            self.toolBtns[self.stackManager.tool.name].SetToggle(toolName == self.stackManager.tool.name)
        self.toolBtns[toolName].SetToggle(True)

        if not self.stackManager.tool or toolName != self.stackManager.tool.name:
            tool = BaseTool.ToolFromName(toolName, self.stackManager)
            self.stackManager.SetTool(tool)

            if tool.name in ["pen", "oval", "rect", "poly", "line", "roundrect"]:
                self.box.Show(self.drawBox)
                self.box.Hide(self.editBox)
                self.stackManager.SelectUiView(None)
                tool.SetPenColor(self.penColor)
                tool.SetFillColor(self.fillColor)
                tool.SetThickness(self.penThickness)
            elif tool.name == "hand":
                self.box.Hide(self.drawBox)
                self.box.Show(self.editBox)
                self.helpResizer.Show(self.isContextHelpEnabled)
            else:
                self.box.Hide(self.drawBox)
                self.box.Hide(self.editBox)

            self.Layout()
        self.stackManager.view.SetFocus()

    def OnSetPenColor(self, event):
        newColor = event.GetColour()
        try:
            colorName = newColor.GetAsString(flags=wx.C2S_NAME)
            self.penColor = colorName
        except:
            colorStr = newColor.GetAsString(flags=wx.C2S_HTML_SYNTAX)
            if colorStr == "#000000": colorStr = "black"
            elif colorStr == "#FFFFFF": colorStr = "white"
            self.penColor = colorStr
        self.ci.UpdateLine(self.penColor, self.penThickness)
        self.stackManager.tool.SetPenColor(self.penColor)

    def OnSetFillColor(self, event):
        newColor = event.GetColour()
        try:
            colorName = newColor.GetAsString(flags=wx.C2S_NAME)
            self.fillColor = colorName
        except:
            colorStr = newColor.GetAsString(flags=wx.C2S_HTML_SYNTAX)
            if colorStr == "#000000": colorStr = "black"
            elif colorStr == "#FFFFFF": colorStr = "white"
            self.fillColor = colorStr
        self.stackManager.tool.SetFillColor(self.fillColor)

    def OnSetThickness(self, event):
        """
        Use the event ID to set the thickness in the stackManager.
        """
        newThickness = event.GetId()
        # untoggle the old thickness button
        self.thknsBtns[self.penThickness].SetToggle(newThickness == self.penThickness)
        # set the new color
        self.penThickness = newThickness
        self.ci.UpdateLine(wx.Colour(self.penColor), self.penThickness)
        self.stackManager.tool.SetThickness(self.penThickness)


# ----------------------------------------------------------------------

class ColorIndicator(wx.Window):
    """
    An instance of this class is used on the ControlPanel to show
    a sample of what the current stackManager line will look like.
    """
    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetBackgroundColour(wx.WHITE)
        self.SetMinSize( (45, 45) )
        self.color = self.thickness = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateLine(self, color, thickness):
        """
        The stackManager view calls this method any time the color
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
BUTTON_WIDTH = 50

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
        dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-COLOR_PATCH_WIDTH, rect.Top+1, COLOR_PATCH_WIDTH, rect.Height-1))

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
        self.cPanel.InspectorValueChanged(self.row, color)


# class GridCellFileRenderer(wx.grid.GridCellStringRenderer):
#     fileBmp = None
#
#     def Draw(self, grid, attr, dc, rect, row, col, isSelected):
#         text = grid.GetCellValue(row, col)
#
#         if isSelected:
#             bg = grid.GetSelectionBackground()
#             fg = grid.GetSelectionForeground()
#         else:
#             bg = attr.GetBackgroundColour()
#             fg = attr.GetTextColour()
#         dc.SetTextBackground(bg)
#         dc.SetTextForeground(fg)
#         dc.SetPen(wx.TRANSPARENT_PEN)
#         dc.SetBrush(wx.Brush(bg, wx.SOLID))
#         dc.DrawRectangle(rect)
#         dc.SetPen(wx.Pen('black', 1, wx.PENSTYLE_SOLID))
#         dc.SetBrush(wx.Brush('white', wx.SOLID))
#         dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-BUTTON_WIDTH, rect.Top+1, BUTTON_WIDTH, rect.Height-1))
#         if not self.fileBmp:
#             self.fileBmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, size=wx.Size(rect.Height, rect.Height))
#         dc.DrawBitmap(self.fileBmp, wx.Point(rect.Left + rect.Width-((BUTTON_WIDTH+self.fileBmp.Width)/2), rect.Top))
#
#         hAlign, vAlign = attr.GetAlignment()
#         dc.SetFont(attr.GetFont())
#         grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)
#
#
# class GridCellFileEditor(wx.grid.GridCellTextEditor):
#     def __init__(self, cPanel):
#         super().__init__()
#         self.cPanel = cPanel
#         self.grid = cPanel.inspector
#
#     wildcard = "Image Files (*.jpeg,*.jpg,*.png,*.gif,*.bmp)|*.jpeg;*.jpg;*.png;*.gif;*.bmp"
#
#     def StartingClick(self):
#         self.row = self.grid.GetGridCursorRow()
#         self.col = self.grid.GetGridCursorCol()
#         text = self.grid.GetCellValue(self.row, self.col)
#         x,y = self.grid.ScreenToClient(wx.GetMousePosition())
#         if x > self.grid.GetSize().Width - BUTTON_WIDTH:
#             startDir = ""
#             if self.cPanel.stackManager.filename:
#                 startDir = os.path.dirname(self.cPanel.stackManager.filename)
#             startFile = ""
#             if text:
#                 if self.cPanel.stackManager.filename:
#                     cdsFileDir = os.path.dirname(self.cPanel.stackManager.filename)
#                     path = os.path.join(cdsFileDir, text)
#                     startDir = os.path.dirname(path)
#                     startFile = os.path.basename(path)
#             dlg = wx.FileDialog(self.cPanel, "Choose Image file...", defaultDir=startDir,
#                                 defaultFile=startFile, style=wx.FD_OPEN, wildcard=self.wildcard)
#             if dlg.ShowModal() == wx.ID_OK:
#                 filename = dlg.GetPath()
#                 if self.cPanel.stackManager.filename:
#                     cdsFileDir = os.path.dirname(self.cPanel.stackManager.filename)
#                     try:
#                         filename = os.path.relpath(filename, cdsFileDir)
#                     except:
#                         pass
#                 self.UpdateFile(filename)
#             dlg.Destroy()
#
#     def UpdateFile(self, filename):
#         self.grid.SetCellValue(self.row, self.col, filename)
#         self.cPanel.InspectorValueChanged(self.row, filename)


class GridCellImageFileRenderer(wx.grid.GridCellStringRenderer):
    fileBmp = None
    clipArtBmp = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        text = grid.GetCellValue(row, col)

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
        dc.SetBrush(wx.Brush('white', wx.SOLID))

        dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-BUTTON_WIDTH*2, rect.Top+1, BUTTON_WIDTH, rect.Height-1))
        if not self.clipArtBmp:
            self.clipArtBmp = wx.ArtProvider.GetBitmap(wx.ART_CUT, size=wx.Size(rect.Height, rect.Height))
        dc.DrawBitmap(self.clipArtBmp, wx.Point(rect.Left + rect.Width-BUTTON_WIDTH-((BUTTON_WIDTH+self.clipArtBmp.Width)/2), rect.Top))

        dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-BUTTON_WIDTH, rect.Top+1, BUTTON_WIDTH, rect.Height-1))
        if not self.fileBmp:
            self.fileBmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, size=wx.Size(rect.Height, rect.Height))
        dc.DrawBitmap(self.fileBmp, wx.Point(rect.Left + rect.Width-((BUTTON_WIDTH+self.fileBmp.Width)/2), rect.Top))

        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)


class GridCellImageFileEditor(wx.grid.GridCellTextEditor):
    def __init__(self, cPanel):
        super().__init__()
        self.cPanel = cPanel
        self.grid = cPanel.inspector

    wildcard = "Image Files (*.jpeg,*.jpg,*.png,*.gif,*.bmp)|*.jpeg;*.jpg;*.png;*.gif;*.bmp"

    def StartingClick(self):
        self.row = self.grid.GetGridCursorRow()
        self.col = self.grid.GetGridCursorCol()
        text = self.grid.GetCellValue(self.row, self.col)
        x,y = self.grid.ScreenToClient(wx.GetMousePosition())
        if x > self.grid.GetSize().Width - BUTTON_WIDTH:
            startDir = ""
            if self.cPanel.stackManager.filename:
                startDir = os.path.dirname(self.cPanel.stackManager.filename)
            startFile = ""
            if text:
                if self.cPanel.stackManager.filename:
                    cdsFileDir = os.path.dirname(self.cPanel.stackManager.filename)
                    path = os.path.join(cdsFileDir, text)
                    startDir = os.path.dirname(path)
                    startFile = os.path.basename(path)
            dlg = wx.FileDialog(self.cPanel, "Choose Image file...", defaultDir=startDir,
                                defaultFile=startFile, style=wx.FD_OPEN, wildcard=self.wildcard)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                if self.cPanel.stackManager.filename:
                    cdsFileDir = os.path.dirname(self.cPanel.stackManager.filename)
                    try:
                        filename = os.path.relpath(filename, cdsFileDir)
                    except:
                        pass
                self.UpdateFile(filename)
            dlg.Destroy()
        elif x > self.grid.GetSize().Width - BUTTON_WIDTH*2:
            if not self.cPanel.stackManager.filename:
                wx.MessageDialog(self.cPanel.stackManager.designer,
                                 "Please save your stack before pasting an Image.",
                                 "Unsaved Stack", wx.OK).ShowModal()
                return

            def onImageLoaded(path):
                self.UpdateFile(path)

            dlg = mediaSearchDialogs.ImageSearchDialog(self.cPanel.stackManager.designer,
                                                       self.cPanel.stackManager.designer.GetCurDir(),
                                                       onImageLoaded)
            dlg.RunModal()


    def UpdateFile(self, filename):
        self.grid.SetCellValue(self.row, self.col, filename)
        self.cPanel.InspectorValueChanged(self.row, filename)
