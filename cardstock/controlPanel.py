# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.grid
import wx.html
import os
import mediaSearchDialogs
import propertyInspector
from codeInspectorMulti import CodeInspectorContainer
from tools import *
from appCommands import *
from wx.lib import buttons # for generic button classes
from wx.lib.resizewidget import ResizeWidget, EVT_RW_LAYOUT_NEEDED
from pythonEditor import PythonEditor
from uiView import UiView
from embeddedImages import embeddedToolImages
from helpDataGen import HelpData


class ControlPanel(wx.Panel):
    """
    This class implements the control panel for the designer app.  It includes a tool palette for choosing a tool.
    It includes thickness and pen and fill colors for drawing shapes, and an inspector and code editor for editing
    objects.
    """

    BMP_SIZE = 25
    BMP_BORDER = 4

    defaultPanelWidth = 450

    toolNames = ["hand", "button", "field", "webview", "image", "label",
                 "pen", "oval", "rect", "roundrect", "polygon", "line"]
    tooltips = ["Hand (Esc)", "Button (B)", "Text Field (F)", "Web View (W)", "Image (I)", "Text Label (T)",
                "Pen (P)", "Oval (O)", "Rectangle (R)", "Round Rectangle (D)", "Polygon (G)", "Line (L)"]

    def __init__(self, parent, ID, stackManager):
        super().__init__(parent, ID, style=wx.RAISED_BORDER)
        self.stackManager = stackManager
        self.pen_color = "black"
        self.fill_color = "white"
        self.pen_thickness = 4
        self.isContextHelpEnabled = True
        numCols = 12
        spacing = 6

        btnSize = self.FromDIP(wx.Size(self.BMP_SIZE + 2*self.BMP_BORDER,
                          self.BMP_SIZE + 2*self.BMP_BORDER))

        # Make a grid of buttons for the tools.
        self.toolBtns = {}
        toolBitmaps = {}
        for k,v in embeddedToolImages.items():
            b = v.GetBitmap()
            if wx.Platform == "__WXMSW__":
                b.Rescale(b, self.FromDIP(wx.Size(self.BMP_SIZE, self.BMP_SIZE)))
            toolBitmaps[k] = b

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
        self.ci.UpdateShape(wx.Colour(self.pen_color), wx.Colour(self.fill_color), self.pen_thickness)

        # ----------

        self.inspector = propertyInspector.PropertyInspector(self, self.stackManager)
        self.inspector.mergeFontRow = True
        self.inspector.valueChangedFunc = self.InspectorValueChanged
        self.inspector.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridCellSelected)

        self.panelHelp = wx.html.HtmlWindow(self, size=(self.FromDIP(200), self.FromDIP(50)), style=wx.BORDER_SUNKEN)

        self.helpResizer = ResizeWidget(self)
        self.helpResizer.SetColors(pen='blue', fill='blue')
        self.helpResizer.SetManagedChild(self.panelHelp)
        self.panelHelp.Show()

        codeInspectorContainer = CodeInspectorContainer(self, self.stackManager)
        self.codeInspector = codeInspectorContainer.codeInspector
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
        if wx.Platform == "__WXMAC__":
            self.editBox.AddSpacer(4)
        self.editBox.Add(codeInspectorContainer, 1, wx.EXPAND|wx.ALL, spacing)
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
            editor.DecRef()

    def GetInspectorSelection(self):
        if len(self.lastSelectedUiViews) == 1:
            if self.inspector.IsCellEditControlShown():
                row = self.inspector.GetGridCursorRow()
                editor = self.inspector.GetCellEditor(row, 1)
                control = editor.GetControl()
                editor.DecRef()
                if control:
                    start, end = control.GetSelection()
                    text = control.GetStringSelection()
                    return (start, end, text)
        return (None, None, None)

    def OnGridCellSelected(self, event):
        if not self.inspector.isSettingUp:
            if len(self.lastSelectedUiViews) > 0:
                uiView = self.lastSelectedUiViews[0]
                if uiView:
                    key = self.inspector.GetCellValue(event.GetRow(), 0)
                    helpText = HelpData.GetPropertyHelp(uiView.model, key)
                    self.UpdateHelpText(helpText)
        else:
            self.UpdateHelpText("")
        event.Skip()

    def UpdateForUiViews(self, uiViews):
        self.Freeze()
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
        self.Thaw()

    def UpdatedProperty(self, uiView, key):
        if uiView in self.lastSelectedUiViews:
            self.inspector.SetValue(key, uiView.model.GetProperty(key))
            self.inspector.SetValueForKey(key, uiView.model.GetPropertyType(key))

    def UpdateInspectorForUiViews(self, uiViews):
        props = {}
        propTypes = {}
        title = "None"

        self.Freeze()
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

        self.inspector.selectedModels = [ui.model for ui in uiViews]
        self.inspector.SetData(title, props, propTypes)
        self.Layout()
        self.Thaw()

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
        bmp = wx.Bitmap(self.BMP_SIZE, self.FromDIP(thickness))
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

            if tool.name in ["pen", "oval", "rect", "polygon", "line", "roundrect"]:
                self.box.Show(self.drawBox)
                self.box.Hide(self.editBox)
                self.stackManager.SelectUiView(None)
                tool.SetPenColor(self.pen_color)
                tool.SetFillColor(self.fill_color)
                tool.SetThickness(self.pen_thickness)
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
            self.pen_color = colorName
        except:
            colorStr = newColor.GetAsString(flags=wx.C2S_HTML_SYNTAX)
            if colorStr == "#000000": colorStr = "black"
            elif colorStr == "#FFFFFF": colorStr = "white"
            self.pen_color = colorStr
        self.ci.UpdateShape(self.pen_color, self.fill_color, self.pen_thickness)
        self.stackManager.tool.SetPenColor(self.pen_color)

    def OnSetFillColor(self, event):
        newColor = event.GetColour()
        try:
            colorName = newColor.GetAsString(flags=wx.C2S_NAME)
            self.fill_color = colorName
        except:
            colorStr = newColor.GetAsString(flags=wx.C2S_HTML_SYNTAX)
            if colorStr == "#000000": colorStr = "black"
            elif colorStr == "#FFFFFF": colorStr = "white"
            self.fill_color = colorStr
        self.ci.UpdateShape(self.pen_color, self.fill_color, self.pen_thickness)
        self.stackManager.tool.SetFillColor(self.fill_color)

    def OnSetThickness(self, event):
        """
        Use the event ID to set the thickness in the stackManager.
        """
        newThickness = event.GetId()
        # untoggle the old thickness button
        self.thknsBtns[self.pen_thickness].SetToggle(newThickness == self.pen_thickness)
        # set the new color
        self.pen_thickness = newThickness
        self.ci.UpdateShape(wx.Colour(self.pen_color), wx.Colour(self.fill_color), self.pen_thickness)
        self.stackManager.tool.SetThickness(self.pen_thickness)


# ----------------------------------------------------------------------

class ColorIndicator(wx.Window):
    """
    An instance of this class is used on the ControlPanel to show
    a sample of what the current stackManager line will look like.
    """
    def __init__(self, parent):
        super().__init__(parent, -1, style=wx.SUNKEN_BORDER)
        dipScale = self.FromDIP(1000)/1000.0
        self.SetBackgroundColour(wx.WHITE)
        self.SetMinSize( (60*dipScale, 60*dipScale) )
        self.pen_color = self.fill_color = self.thickness = None
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def UpdateShape(self, pen_color, fill_color, thickness):
        """
        The stackManager view calls this method any time the color
        or line thickness changes.
        """
        self.pen_color = pen_color
        self.fill_color = fill_color
        self.thickness = self.FromDIP(thickness)
        self.Refresh()  # generate a paint event

    def OnPaint(self, event):
        """
        This method is called when all or part of the view needs to be
        redrawn.
        """
        dc = wx.PaintDC(self)
        if self.pen_color and self.fill_color and self.thickness:
            sz = self.GetClientSize()
            dc.SetPen(wx.Pen(self.pen_color, self.thickness))
            dc.SetBrush(wx.Brush(self.fill_color))
            dc.DrawRoundedRectangle(self.FromDIP(10), self.FromDIP(10), int(sz.width-self.FromDIP(20)), int(sz.height-self.FromDIP(20)), self.FromDIP(10))
