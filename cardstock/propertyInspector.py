# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import wx.grid
from uiView import ViewModel, ViewProxy
from simpleListBox import SimpleListBox
import mediaSearchDialogs
from appCommands import SetPropertyCommand
import os
import math


class PropertyInspector(wx.grid.Grid):
    def __init__(self, parent, stackManager):
        super().__init__(parent, style=wx.WANTS_CHARS)

        self.data = {}
        self.title = ""
        self.types = None
        self.mergeFontRow = False  # Set to True to show Font rows as "Font [b] [i] [u]"
        self.selectedModels = []

        self.stackManager = stackManager
        self.valueChangedFunc = None
        self.objClickedFunc = None
        self.isSettingUp = True

        self.CreateGrid(1, 2)
        self.SetRowSize(0, self.FromDIP(24))
        self.SetColSize(0, self.FromDIP(110))
        self.SetColLabelSize(self.FromDIP(20))
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, "")
        self.SetRowLabelSize(1)
        self.DisableDragRowSize()
        self.DisableDragColSize()
        self.SetSelectionMode(wx.grid.Grid.GridSelectNone)

        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnInspectorValueChanged)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGridClick)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnGridSelect)
        self.Bind(wx.EVT_KEY_DOWN, self.OnGridKeyDown)
        self.Bind(wx.EVT_SIZE, self.OnGridResized)

    def SetData(self, title, data, types=None):
        """ Set the dictionary of properties/items to show in the inspector. """
        self.SaveIfNeeded()
        self.title = title
        self.data = data
        self.types = types if types else {}
        self.UpdateInspector()

    def OnGridClick(self, event):
        self.SetGridCursor(event.Row, event.Col)
        event.Skip()

    def OnGridSelect(self, event):
        self.Refresh(True)
        event.Skip()

    def OnGridResized(self, event):
        width, height = self.GetClientSize()
        width = width - self.GetColSize(0) - 1
        if width < 0:
            width = 0
        self.SetColSize(1, width)
        event.Skip()

    def OnGridKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            if not self.IsCellEditControlShown():
                if not self.IsReadOnly(self.GetGridCursorRow(), 1):
                    if self.GetGridCursorCol() == 0:
                        self.SetGridCursor(self.GetGridCursorRow(), 1)
                    self.EnableCellEditControl(True)
            else:
                ed = self.GetCellEditor(self.GetGridCursorRow(), 1)
                if isinstance(ed, wx.grid.GridCellAutoWrapStringEditor):
                    event.EventObject.WriteText('\n')
                    return
                elif isinstance(ed, GridCellCustomChoiceEditor):
                    ed.GetControl().DoClose(True)
                else:
                    self.DisableCellEditControl()
                ed.DecRef()
                event.StopPropagation()
                return
        elif event.GetKeyCode() in (wx.WXK_UP, wx.WXK_DOWN) and self.IsCellEditControlShown():
            event.StopPropagation()
        else:
            if event.GetKeyCode() == wx.WXK_TAB:
                event.StopPropagation()
            else:
                event.Skip()

    def OnInspectorValueChanged(self, event):
        r = event.GetRow()
        self.InspectorValueChanged(r, self.GetCellValue(r, 1))

    def GetTypeForKey(self, key):
        valType = self.types.get(key)
        if not valType:
            oldVal = self.data[key]
            if isinstance(oldVal, bool): valType = 'bool'
            elif isinstance(oldVal, int): valType = 'int'
            elif isinstance(oldVal, str): valType = 'str'
            elif isinstance(oldVal, float): valType = 'float'
            elif isinstance(oldVal, (wx.Point, wx.RealPoint)): valType = 'point'
            elif isinstance(oldVal, wx.Size): valType = 'size'
            elif isinstance(oldVal, (list, tuple)): valType = 'list'
            elif isinstance(oldVal, set): valType = 'set'
            elif isinstance(oldVal, dict): valType = 'dict'
            elif isinstance(oldVal, (ViewModel, ViewProxy)): valType = 'obj'
            elif callable(oldVal): valType = 'func'

        return valType

    def SaveIfNeeded(self):
        # Catch a still-open editor and handle it before we move on to a newly selected uiView
        if self.IsCellEditControlShown():
            ed = self.GetCellEditor(self.GetGridCursorRow(), self.GetGridCursorCol())
            val = ed.GetValue()
            ed.DecRef()
            self.InspectorValueChanged(self.GetGridCursorRow(), val)
            self.HideCellEditControl()

    def UpdateInspector(self):
        self.SaveIfNeeded()
        (oldRow, oldCol) = self.GetGridCursorCoords()

        noUpdates = wx.grid.GridUpdateLocker(self)
        self.isSettingUp = True
        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())

        if len(self.data) == 0:
            self.SetColLabelValue(0, "None")
            self.InsertRows(0, 1)
            self.SetReadOnly(0, 0)
            self.SetReadOnly(0, 1)
            self.Layout()
            self.isSettingUp = False
            return

        self.SetColLabelValue(0, self.title)
        keys = self.data.keys()
        self.InsertRows(0,len(keys))
        r = 0
        for k in keys:
            self.SetCellValue(r, 0, str(k))
            self.SetReadOnly(r, 0)
            valType = self.GetTypeForKey(k)
            self.SetValueForKey(k, valType)

            if valType in ("static", "func"):
                self.SetReadOnly(r, 1)

            renderer = None
            editor = None

            if valType == "bool":
                editor = GridCellCustomChoiceEditor(["True", "False"])
            elif self.mergeFontRow and k == "font" and valType == "choice":
                editor = GridCellFontEditor(ViewModel.GetPropertyChoices(k), self, self.selectedModels)
                renderer = GridCellFontRenderer(self.selectedModels)
            elif valType == "choice":
                editor = GridCellCustomChoiceEditor(ViewModel.GetPropertyChoices(k))
            elif valType == "color":
                editor = GridCellColorEditor(self)
                renderer = GridCellColorRenderer()
            elif valType == "file":
                editor = GridCellImageFileEditor(self, self.stackManager.runner is None)
                renderer = GridCellImageFileRenderer(self.stackManager.runner is None)
            elif valType in ("obj", "list", "static_list", "dict", "set", "static"):
                editable = (valType not in ("obj", "static_list", "static"))
                editor = GridCellObjectEditor(self, editable)
                renderer = GridCellObjectRenderer()
            elif valType == "text":
                editor = wx.grid.GridCellAutoWrapStringEditor()
                renderer = wx.grid.GridCellAutoWrapStringRenderer()
                self.SetRowSize(r, 200)
            if renderer:
                self.SetCellRenderer(r, 1, renderer)
            if editor:
                self.SetCellEditor(r, 1, editor)
            r += 1

        if len(keys) >= oldRow:
            self.SetGridCursor(oldRow, oldCol)
        self.Layout()
        self.isSettingUp = False

    def SetValueForKey(self, key, valType):
        if key in self.data.keys():
            row = list(self.data.keys()).index(key)
            val = self.data[key]
            if valType in ["point", "floatpoint", "size"]:
                val = [int(i) if math.modf(i)[0] == 0 else i for i in list(val)]
                self.SetCellValue(row, 1, str(val))
            elif valType == "float":
                if isinstance(val, float) and val % 1 == 0:
                    self.SetCellValue(row, 1, str(int(val)))
                else:
                    self.SetCellValue(row, 1, str(val))
            else:
                val = str(val)
                if len(val) > 256:
                    val = val[:253] + "..."
                self.SetCellValue(row, 1, val)

    def SetValue(self, key, val):
        if key in ("is_bold", "is_italic", "is_underlined"):
            self.Refresh(True)
        if key in self.data:
            self.data[key] = val

    def UpdateValues(self):
        """ Update the values for the existing set of data.  (Assumes keys and types have not changed.) """
        self.SaveIfNeeded()
        keys = self.data.keys()
        r = 0
        for k in keys:
            self.SetValueForKey(k, self.GetTypeForKey(k))
            r += 1

    def InspectorValueChanged(self, row, valStr):
        key = list(self.data.keys())[row]
        valType = self.GetTypeForKey(key)
        val = ViewModel.InterpretPropertyFromString(key, valStr, valType)
        if val != None:
            self.data[key] = val
            if self.valueChangedFunc:
                self.valueChangedFunc(key, val)
            self.SetValueForKey(key, valType)
        else:
            self.UpdateValues()


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

        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

        dc.SetPen(wx.Pen('black', 1, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        cpw = grid.FromDIP(COLOR_PATCH_WIDTH)
        dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-cpw, rect.Top+1, cpw, rect.Height-1))


class GridCellColorEditor(wx.grid.GridCellTextEditor):
    def __init__(self, inspector):
        super().__init__()
        self.inspector = inspector

    def StartingClick(self):
        self.row = self.inspector.GetGridCursorRow()
        self.col = self.inspector.GetGridCursorCol()
        text = self.inspector.GetCellValue(self.row, self.col)
        x,y = self.inspector.ScreenToClient(wx.GetMousePosition())
        cpw = self.inspector.FromDIP(COLOR_PATCH_WIDTH)
        if x > self.inspector.GetSize().Width - cpw:
            data = wx.ColourData()
            data.SetColour(text)
            data.SetChooseAlpha(True)
            dlg = wx.ColourDialog(self.inspector, data)
            if dlg.ShowModal() == wx.ID_OK:
                color = dlg.GetColourData().GetColour().GetAsString(flags=wx.C2S_HTML_SYNTAX)
                self.UpdateColor(color)

    def UpdateColor(self, color):
        self.inspector.SetCellValue(self.row, self.col, color)
        self.inspector.InspectorValueChanged(self.row, color)


class GridCellImageFileRenderer(wx.grid.GridCellStringRenderer):
    fileBmp = None
    clipArtBmp = None

    def __init__(self, showClipArtButton):
        super().__init__()
        self.showClipArtButton = showClipArtButton

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

        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

        bw = grid.FromDIP(BUTTON_WIDTH)

        if self.showClipArtButton:
            dc.DrawRectangle(wx.Rect(rect.Left + rect.Width - bw * 2, rect.Top + 1, bw, rect.Height - 1))
            if not self.clipArtBmp:
                self.clipArtBmp = wx.ArtProvider.GetBitmap(wx.ART_CUT, size=wx.Size(rect.Height, rect.Height))
            dc.DrawBitmap(self.clipArtBmp, wx.Point(int(rect.Left + rect.Width - bw - ((bw + self.clipArtBmp.Width) / 2)), rect.Top))

        dc.DrawRectangle(wx.Rect(int(rect.Left + rect.Width - bw), rect.Top + 1, bw, rect.Height - 1))
        if not self.fileBmp:
            self.fileBmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, size=wx.Size(rect.Height, rect.Height))
        dc.DrawBitmap(self.fileBmp, wx.Point(int(rect.Left + rect.Width - ((bw + self.fileBmp.Width) / 2)), rect.Top))


class GridCellImageFileEditor(wx.grid.GridCellTextEditor):
    def __init__(self, inspector, showClipArtButton):
        super().__init__()
        self.inspector = inspector
        self.showClipArtButton = showClipArtButton

    wildcard = "Image Files (*.jpeg,*.jpg,*.png,*.gif,*.bmp)|*.jpeg;*.jpg;*.png;*.gif;*.bmp"

    def StartingClick(self):
        self.row = self.inspector.GetGridCursorRow()
        self.col = self.inspector.GetGridCursorCol()
        text = self.inspector.GetCellValue(self.row, self.col)
        x,y = self.inspector.ScreenToClient(wx.GetMousePosition())
        bw = self.inspector.FromDIP(BUTTON_WIDTH)
        if x > self.inspector.GetSize().Width - bw:
            startDir = ""
            if self.inspector.stackManager.filename:
                startDir = os.path.dirname(self.inspector.stackManager.filename)
            startFile = ""
            if text:
                if self.inspector.stackManager.filename:
                    cdsFileDir = os.path.dirname(self.inspector.stackManager.filename)
                    path = os.path.join(cdsFileDir, text)
                    startDir = os.path.dirname(path)
                    startFile = os.path.basename(path)
            dlg = wx.FileDialog(self.inspector, "Choose Image file...", defaultDir=startDir,
                                defaultFile=startFile, style=wx.FD_OPEN, wildcard=self.wildcard)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                if self.inspector.stackManager.filename:
                    cdsFileDir = os.path.dirname(self.inspector.stackManager.filename)
                    try:
                        filename = os.path.relpath(filename, cdsFileDir)
                    except:
                        pass
                self.UpdateFile(filename)
            dlg.Destroy()
        elif self.showClipArtButton and x > self.inspector.GetSize().Width - bw*2:
            if not self.inspector.stackManager.filename:
                wx.MessageDialog(self.inspector.stackManager.designer,
                                 "Please save your stack before downloading an Image.",
                                 "Unsaved Stack", wx.OK).ShowModal()
                return

            def onImageLoaded(path):
                self.UpdateFile(path)

            dlg = mediaSearchDialogs.ImageSearchDialog(self.inspector.GetTopLevelParent(),
                                                       self.inspector.stackManager.designer.GetCurDir(),
                                                       onImageLoaded)
            dlg.RunModal()


    def UpdateFile(self, filename):
        self.inspector.SetCellValue(self.row, self.col, filename)
        self.inspector.InspectorValueChanged(self.row, filename)


class GridCellCustomChoiceEditor(wx.grid.GridCellEditor):
    def __init__(self, choices):
        super().__init__()
        self.choices = choices
        self._listBox = None

    def Create(self, parent, id, evtHandler):
        self._listBox = SimpleListBox(parent, False, id=id)
        self._listBox.SetupWithItems(self.choices, 0, 0)
        self.SetControl(self._listBox)
        if evtHandler:
            self._listBox.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        self._listBox.SetPosition((rect.x, rect.y))

    def BeginEdit(self, row, col, grid):
        startValue = grid.GetTable().GetValue(row, col)
        self._listBox.doneFunc = self.OnHandlerPickerDone
        self._listBox.SetStringSelection(startValue)
        self._listBox.SetFocus()

    def EndEdit(self, row, col, grid, oldVal):
        changed = False
        if self._listBox.selection is not None:
            val = self._listBox.items[self._listBox.selection]
            if val != oldVal:
                changed = True
            grid.GetTable().SetValue(row, col, val)  # update the table
        return changed

    def ApplyEdit(self, row, col, grid):
        if self._listBox.selection is not None:
            val = self._listBox.items[self._listBox.selection]
            grid.GetTable().SetValue(row, col, val)  # update the table

    def Reset(self):
        pass

    def Clone(self):
        return GridCellCustomChoiceEditor(self.choices)

    def StartingKey(self, event):
        for c in self.choices:
            if ord(c[0].lower()) == event.GetKeyCode():
                self._listBox.SetStringSelection(c)
                break

    def OnHandlerPickerDone(self, index, text):
        if text:
            self._listBox.SetSelection(index)

class GridCellObjectEditor(wx.grid.GridCellTextEditor):
    def __init__(self, inspector, editable):
        super().__init__()
        self.inspector = inspector
        self.editable = editable

    def StartingClick(self):
        self.row = self.inspector.GetGridCursorRow()
        self.col = self.inspector.GetGridCursorCol()
        x,y = self.inspector.ScreenToClient(wx.GetMousePosition())
        if x > self.inspector.GetSize().Width - self.inspector.FromDIP(BUTTON_WIDTH):
            self.inspector.HideCellEditControl()
            self.inspector.objClickedFunc(self.row)
        else:
            super().StartingClick()

    def BeginEdit(self, row, col, grid):
        if not self.editable:
            self.inspector.HideCellEditControl()
        else:
            super().BeginEdit(row, col, grid)


class GridCellObjectRenderer(wx.grid.GridCellStringRenderer):
    objBmp = None

    def __init__(self):
        super().__init__()

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

        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)
        bw = grid.FromDIP(BUTTON_WIDTH)

        dc.DrawRectangle(wx.Rect(rect.Left + rect.Width-bw, rect.Top+1, bw, rect.Height-1))
        if not self.objBmp:
            self.objBmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, size=wx.Size(rect.Height, rect.Height))
        dc.DrawBitmap(self.objBmp, wx.Point(int(rect.Left + rect.Width-((bw+self.objBmp.Width)/2)), rect.Top))


class GridCellFontRenderer(wx.grid.GridCellStringRenderer):
    def __init__(self, textObjs):
        super().__init__()
        self.textObjs = textObjs

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
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

        text = grid.GetCellValue(row, col)
        hAlign, vAlign = attr.GetAlignment()
        dc.SetFont(attr.GetFont())
        grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

        is_bold = self.textObjs[0].GetProperty("is_bold") if len(self.textObjs) else False
        dc.SetPen(wx.Pen('grey', 1, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('grey' if is_bold else 'white', wx.SOLID))
        cpw = grid.FromDIP(COLOR_PATCH_WIDTH)
        styleRect = wx.Rect(int(rect.Left + rect.Width-cpw), rect.Top+1, int(cpw/3-2), rect.Height-1)
        dc.DrawRectangle(styleRect)
        dc.SetFont(attr.GetFont().Bold())
        styleRect.Position -= (0, 2)
        grid.DrawTextRectangle(dc, "b", styleRect, wx.ALIGN_CENTER, vAlign)

        is_italic = self.textObjs[0].GetProperty("is_italic") if len(self.textObjs) else False
        dc.SetPen(wx.Pen('grey', 1, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('grey' if is_italic else 'white', wx.SOLID))
        styleRect = wx.Rect(int(rect.Left + rect.Width-2*cpw/3+1), rect.Top+1, int(cpw/3-2), rect.Height-1)
        dc.DrawRectangle(styleRect)
        dc.SetFont(attr.GetFont().Italic())
        styleRect.Position -= (0, 2)
        grid.DrawTextRectangle(dc, "i", styleRect, wx.ALIGN_CENTER, vAlign)

        showIsUnderlined = True
        for m in self.textObjs:
            if m.type != "textlabel":
                showIsUnderlined = False
                break
        if showIsUnderlined:
            is_underlined = self.textObjs[0].GetProperty("is_underlined") if len(self.textObjs) else False
            dc.SetPen(wx.Pen('grey', 1, wx.PENSTYLE_SOLID))
            dc.SetBrush(wx.Brush('grey' if is_underlined else 'white', wx.SOLID))
            styleRect = wx.Rect(int(rect.Left + rect.Width-cpw/3+2), rect.Top+1, int(cpw/3-2), rect.Height-1)
            dc.DrawRectangle(styleRect)
            dc.SetFont(attr.GetFont().Underlined())
            styleRect.Position -= (0, 2)
            grid.DrawTextRectangle(dc, "u", styleRect, wx.ALIGN_CENTER, vAlign)


class GridCellFontEditor(GridCellCustomChoiceEditor):
    def __init__(self, choices, inspector, textObjs):
        super().__init__(choices)
        self.textObjs = textObjs
        self.inspector = inspector

    def StartingClick(self):
        self.row = self.inspector.GetGridCursorRow()
        self.col = self.inspector.GetGridCursorCol()
        x,y = self.inspector.ScreenToClient(wx.GetMousePosition())
        cpw = self.inspector.FromDIP(COLOR_PATCH_WIDTH)
        if x > self.inspector.GetSize().Width - cpw/3:
            self.inspector.HideCellEditControl()
            showingIsUnderlined = True
            for m in self.textObjs:
                if m.type != "textlabel":
                    showingIsUnderlined = False
                    break
            if showingIsUnderlined:
                is_underlined = self.textObjs[0].GetProperty("is_underlined") if len(self.textObjs) else False
                for obj in self.textObjs:
                    command = SetPropertyCommand(True, "Set Property", self.inspector.stackManager.designer.cPanel,
                                                 self.inspector.stackManager.cardIndex, obj,
                                                 "is_underlined", not is_underlined)
                    self.inspector.stackManager.command_processor.Submit(command)
        elif x > self.inspector.GetSize().Width - 2 * cpw / 3:
            self.inspector.HideCellEditControl()
            is_italic = self.textObjs[0].GetProperty("is_italic") if len(self.textObjs) else False
            for obj in self.textObjs:
                command = SetPropertyCommand(True, "Set Property", self.inspector.stackManager.designer.cPanel,
                                             self.inspector.stackManager.cardIndex, obj,
                                             "is_italic", not is_italic)
                self.inspector.stackManager.command_processor.Submit(command)
        elif x > self.inspector.GetSize().Width - cpw:
            self.inspector.HideCellEditControl()
            is_bold = self.textObjs[0].GetProperty("is_bold") if len(self.textObjs) else False
            for obj in self.textObjs:
                command = SetPropertyCommand(True, "Set Property", self.inspector.stackManager.designer.cPanel,
                                             self.inspector.stackManager.cardIndex, obj,
                                             "is_bold", not is_bold)
                self.inspector.stackManager.command_processor.Submit(command)
        else:
            super().StartingClick()
