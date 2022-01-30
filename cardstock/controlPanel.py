import wx
import wx.grid
import wx.html
import os
import mediaSearchDialogs
import propertyInspector
from codeInspectorMulti import CodeInspector
from tools import *
from appCommands import *
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

    toolNames = ["hand", "button", "field", "label", "webview", "image",
                 "pen", "oval", "rect", "roundrect", "poly", "line"]
    tooltips = ["Hand (Esc)", "Button (B)", "Text Field (F)", "Text Label (T)", "Web View (W)", "Image (I)",
                "Pen (P)", "Oval (O)", "Rectangle (R)", "Round Rectangle (D)", "Polygon (G)", "Line (L)"]

    def __init__(self, parent, ID, stackManager):
        wx.Panel.__init__(self, parent, ID, style=wx.RAISED_BORDER)
        self.stackManager = stackManager
        self.penColor = "black"
        self.fillColor = "white"
        self.penThickness = 4
        self.isContextHelpEnabled = True
        numCols = 12
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
        self.ci.UpdateShape(wx.Colour(self.penColor), wx.Colour(self.fillColor), self.penThickness)

        # ----------

        self.inspector = propertyInspector.PropertyInspector(self, self.stackManager)
        self.inspector.valueChangedFunc = self.InspectorValueChanged
        self.inspector.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridCellSelected)

        self.panelHelp = wx.html.HtmlWindow(self, size=(200, 50), style=wx.BORDER_SUNKEN)

        self.helpResizer = ResizeWidget(self)
        self.helpResizer.SetColors(pen='blue', fill='blue')
        self.helpResizer.SetManagedChild(self.panelHelp)
        self.panelHelp.Show()

        self.codeInspector = CodeInspector(self, self.stackManager)
        self.codeInspector.updateHelpTextFunc = self.UpdateHelpText

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
        self.editBox.Add(self.codeInspector, 1, wx.EXPAND|wx.ALL, spacing)
        self.editBox.SetSizeHints(self)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.toolGrid, 0, wx.LEFT, spacing)
        self.box.Add(self.drawBox, 0, wx.EXPAND|wx.ALL, 0)
        self.box.Add(self.editBox, 1, wx.EXPAND|wx.ALL, 0)
        self.box.SetSizeHints(self)

        self.helpResizer.Bind(EVT_RW_LAYOUT_NEEDED, self.OnRwLayoutNeeded)

        self.UpdateHelpText("")
        self.SetSizer(self.box)

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
        if uiView in self.lastSelectedUiViews:
            self.inspector.SetValue(key, uiView.model.GetProperty(key))
            self.inspector.SetValueForKey(key, uiView.model.GetPropertyType(key))

    def UpdateInspectorForUiViews(self, uiViews):
        props = {}
        propTypes = {}
        title = "None"

        if len(uiViews) == 1:
            uiView = uiViews[0]
            keys = uiView.model.PropertyKeys()
            title = uiView.model.GetDisplayType()
            for k in keys:
                props[k] = uiView.model.GetProperty(k)
                propTypes[k] = uiView.model.GetPropertyType(k)

        elif len(uiViews) > 1:
            title = "Objects"
            keys = uiViews[0].model.PropertyKeys().copy()
            keys.remove("name")
            # Only show properties that exist for all selected objects
            for uiView in uiViews[1:]:
                oKeys = uiView.model.PropertyKeys()
                keys = [k for k in keys if k in oKeys]
            for k in keys:
                val = uiViews[0].model.GetProperty(k)
                propTypes[k] = uiViews[0].model.GetPropertyType(k)
                # Only show values for properties that are the same for all selected objects
                for ui in uiViews[1:]:
                    if val != ui.model.GetProperty(k):
                        val = None
                        break
                if val is not None:
                    props[k] = val
                else:
                    props[k] = ""

        self.inspector.SetData(title, props, propTypes)
        self.Layout()

    def InspectorValueChanged(self, key, val):
        uiView = self.lastSelectedUiViews[0]

        needsUpdate = False
        if val is not None:
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
            elif key == "text":
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
                if len(commands) == 1:
                    command = commands[0]
                else:
                    command = CommandGroup(True, "Set Property", self.stackManager,
                                           commands, [ui.model for ui in self.lastSelectedUiViews])
                self.stackManager.command_processor.Submit(command)
        if needsUpdate:
            self.inspector.SetValue(key, val)

    def UpdateHandlerForUiViews(self, uiViews, handlerName, selection=None):
        if len(uiViews) == 1:
            self.codeInspector.UpdateHandlerForUiView(uiViews[0], handlerName, selection)
        else:
            self.codeInspector.UpdateHandlerForUiView(None, None, None)

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
        self.ci.UpdateShape(self.penColor, self.fillColor, self.penThickness)
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
        self.ci.UpdateShape(self.penColor, self.fillColor, self.penThickness)
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
        self.ci.UpdateShape(wx.Colour(self.penColor), wx.Colour(self.fillColor), self.penThickness)
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
        self.SetMinSize( (60, 60) )
        self.penColor = self.fillColor = self.thickness = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateShape(self, penColor, fillColor, thickness):
        """
        The stackManager view calls this method any time the color
        or line thickness changes.
        """
        self.penColor = penColor
        self.fillColor = fillColor
        self.thickness = thickness
        self.Refresh()  # generate a paint event

    def OnPaint(self, event):
        """
        This method is called when all or part of the view needs to be
        redrawn.
        """
        dc = wx.PaintDC(self)
        if self.penColor and self.fillColor and self.thickness:
            sz = self.GetClientSize()
            dc.SetPen(wx.Pen(self.penColor, self.thickness))
            dc.SetBrush(wx.Brush(self.fillColor))
            dc.DrawRoundedRectangle(10, 10, int(sz.width-20), int(sz.height-20), 10)
