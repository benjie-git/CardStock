# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from uiView import *
from appCommands import SetPropertyCommand
from uiTextBase import *
import wx.stc as stc
from wx.lib.docview import CommandProcessor, Command


class CDSSTC(stc.StyledTextCtrl):
    def SetPosition(self, pt):
        # Fix positioning bug in STC at coords (x,-1) and (-1,y)
        if pt[0] == -1:
            pt[0] = 0
        if pt[1] == -1:
            pt[1] = 0
        super().SetPosition(pt)


class UiTextField(UiTextBase):
    """
    This class is a controller that coordinates management of a TextField view, based on data from a TextFieldModel.
    """

    def __init__(self, parent, stackManager, model):
        self.stackManager = stackManager
        self.isInlineEditing = False
        self.inlineStartText = None
        stackManager.view.Freeze()
        field = self.CreateField(stackManager, model)
        super().__init__(parent, stackManager, model, field)
        stackManager.view.Thaw()

    def CreateField(self, stackManager, model):
        text = model.GetProperty("text")
        alignment = wx.TE_LEFT
        if model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        pos = self.stackManager.ConvRect(model.GetAbsoluteFrame()).TopLeft
        field = CDSSTC(parent=stackManager.view, size=model.GetProperty("size"), pos=pos,
                                   style=alignment | wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
        field.SetUseHorizontalScrollBar(False)
        field.SetTabWidth(3)
        field.SetUseTabs(0)
        field.SetWrapMode(stc.STC_WRAP_WORD)
        field.SetMarginWidth(1, 0)
        field.ChangeValue(text)
        field.Bind(stc.EVT_STC_MODIFIED, self.OnSTCTextChanged)
        field.Bind(stc.EVT_STC_ZOOM, self.OnZoom)
        field.Bind(wx.EVT_KEY_DOWN, self.OnSTCKeyDown)
        field.EmptyUndoBuffer()

        self.BindEvents(field)
        field.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        field.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        field.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        field.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.UpdateFont(model, field)

        if stackManager.isEditing:
            field.SetEditable(False)
        else:
            field.SetEditable(model.GetProperty("is_editable"))
        return field

    def GetCursor(self):
        if self.stackManager.isEditing and not self.isInlineEditing:
            return wx.CURSOR_HAND
        else:
            return wx.CURSOR_IBEAM

    def OnFocus(self, event):
        if not self.stackManager.isEditing:
            self.stackManager.lastFocusedTextField = self
        event.Skip()

    def OnZoom(self, event):
        z = event.GetEventObject().GetZoom()
        if z != 0:
            event.GetEventObject().SetZoom(0)

    def OnSTCKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.OnTextEnter(event)
            if not self.model.GetProperty("is_multiline"):
                return
        event.Skip()

    def StartInlineEditing(self):
        if self.stackManager.isEditing and not self.isInlineEditing:
            self.inlineStartText = self.model.GetProperty("text")
            self.view.SetEditable(True)
            self.view.SetFocus()
            self.view.SelectAll()
            self.isInlineEditing = True
            self.stackManager.inlineEditingView = self

    def StopInlineEditing(self, notify=True):
        if self.stackManager.isEditing and self.isInlineEditing:
            self.isInlineEditing = False
            endText = self.view.GetValue()
            self.view.SetValue(self.inlineStartText)
            command = SetPropertyCommand(True, "Set Property", self.stackManager.designer.cPanel, self.stackManager.cardIndex, self.model,
                                         "text", endText)
            self.stackManager.command_processor.Submit(command)
            self.view.SetEditable(False)
            self.view.SetSelection(0,0)
            self.stackManager.inlineEditingView = None
            self.stackManager.view.SetFocus()

    def OnResize(self, event):
        if self.view:
            self.view.SetScrollWidth(self.view.GetSize().Width-6)
        if event:
            event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "is_editable":
            if self.stackManager.isEditing:
                self.view.SetEditable(False)
            else:
                self.view.SetEditable(model.GetProperty(key))
        elif key == "selectAll":
            self.view.SelectAll()

    def OnTextEnter(self, event):
        if not self.stackManager.isEditing:
            def f():
                if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_text_enter"):
                    self.stackManager.runner.RunHandler(self.model, "on_text_enter", event)
            wx.CallAfter(f)

    def OnSTCTextChanged(self, event):
        if not self.stackManager.isEditing:
            if event.GetModificationType()%2 == 1:
                t = event.GetEventObject().GetValue()
                if not self.model.GetProperty("is_multiline"):
                    if '\n' in t or '\r' in t:
                        t = t.replace('\r', '')
                        t = t.replace('\n', '')
                        wx.CallAfter(self.view.SetText, t)
                        return
                if not self.settingValueInternally:
                    self.model.SetProperty("text", t, notify=False)
                    if not self.stackManager.isEditing and self.stackManager.runner and self.model.GetHandler("on_text_changed"):
                        self.stackManager.runner.RunHandler(self.model, "on_text_changed", event)
        event.Skip()


CDS_EVT_TEXT_UNDO_TYPE = wx.NewEventType()
CDS_EVT_TEXT_UNDO = wx.PyEventBinder(CDS_EVT_TEXT_UNDO_TYPE, 1)


class CDSTextCtrl(wx.TextCtrl):
    """TextCtrl only handles Undo/Redo on Windows, not Mac or Linux, so add that functionality here."""
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.command_processor = CommandProcessor()
        self.Bind(wx.EVT_TEXT, self.on_text_changed)
        self.oldText = self.GetValue()
        self.oldSel = self.GetSelection()

    def on_text_changed(self, event):
        newText = self.GetValue()
        newSel = self.GetSelection()
        command = TextEditCommand(True, "Change Text", self, self.oldText, newText, self.oldSel, newSel)
        self.command_processor.Submit(command)
        self.oldText = newText
        self.oldSel = newSel
        event.Skip()

    def EmptyUndoBuffer(self):
        if self.command_processor:
            self.command_processor.ClearCommands()
        self.oldText = self.GetValue()
        self.oldSel = self.GetSelection()

    def CanUndo(self):
        return self.command_processor.CanUndo()

    def CanRedo(self):
        return self.command_processor.CanRedo()

    def Undo(self):
        if self.IsEditable():
            self.command_processor.Undo()
            self.oldText = self.GetValue()
            event = wx.PyCommandEvent(CDS_EVT_TEXT_UNDO_TYPE, self.GetId())
            event.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(event)

    def Redo(self):
        if self.IsEditable():
            self.command_processor.Redo()
            self.oldText = self.GetValue()
            event = wx.PyCommandEvent(CDS_EVT_TEXT_UNDO_TYPE, self.GetId())
            event.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(event)


class TextEditCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.textView = args[2]
        self.oldText = args[3]
        self.newText = args[4]
        self.oldSel = args[5]
        self.newSel = args[6]
        self.didRun = False

    def Do(self):
        if self.didRun:
            self.textView.ChangeValue(self.newText)
            self.textView.SetSelection(*self.newSel)
        self.didRun = True
        return True

    def Undo(self):
        self.textView.ChangeValue(self.oldText)
        self.textView.SetSelection(*self.oldSel)
        return True


class TextFieldModel(TextBaseModel):
    """
    This is the model for a TextField object.
    """

    minSize = wx.Size(32,20)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textfield"
        self.proxyClass = TextField

        # Add custom handlers to the top of the list
        handlers = {"on_setup": "", "on_text_changed": "", "on_text_enter": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_text_enter"

        self.properties["name"] = "field_1"
        self.properties["is_editable"] = True
        self.properties["is_multiline"] = False
        self.properties["font_size"] = 12

        self.propertyTypes["is_editable"] = "bool"
        self.propertyTypes["is_multiline"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "font_size", "text_color", "is_editable", "is_multiline", "position", "size"]

    @RunOnMainSync
    def GetSelectedText(self):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.view:
            return uiView.view.GetStringSelection()
        else:
            return ""

    @RunOnMainSync
    def SetSelectedText(self, text):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.view:
            is_multiline = self.GetProperty("is_multiline")
            sel = uiView.view.GetSelection()
            length = len(self.GetProperty("text"))
            s = uiView.view.GetRange(0,sel[0]) + text + uiView.view.GetRange(sel[1], length)
            pos = (uiView.view.GetScrollPos(wx.HORIZONTAL), uiView.view.GetScrollPos(wx.VERTICAL))
            self.SetProperty("text", s)
            uiView.view.SetSelection(sel[0], sel[0]+len(text))
            if is_multiline:
                uiView.view.ScrollToLine(pos[1])
                uiView.view.ScrollToColumn(pos[0])

    def IndexToRowCol(self, field, index):
        if not field:
            uiView = self.stackManager.GetUiViewByModel(self)
            if uiView and uiView.view:
                field = uiView.view
        (inBounds, col, row) = field.PositionToXY(index)
        if not inBounds:
            row = field.GetNumberOfLines() - 1
            col = field.GetLineLength(row)
        return (row, col)

    def RowColToIndex(self, field, row, col):
        if not field:
            uiView = self.stackManager.GetUiViewByModel(self)
            if uiView and uiView.view:
                field = uiView.view
        pos = field.XYToPosition(col, row)
        if pos == -1:
            pos = field.GetLastPosition()
        return pos

    @RunOnMainSync
    def GetSelection(self):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.view:
            return uiView.view.GetSelection()
        else:
            return (0,0)

    @RunOnMainSync
    def SetSelection(self, start_index, end_index):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.view:
            uiView.view.SetSelection(start_index, end_index)

    @RunOnMainSync
    def GetTextPositionAtAbsolutePoint(self, ptAbs):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.view:
            field = uiView.view
            f = self.GetAbsoluteFrame()
            ptRel = wx.Point(self.stackManager.view.FromDIP(int(ptAbs[0] - f.Left)-2),
                             self.stackManager.view.FromDIP(int(f.Height - (ptAbs[1] - f.Top)-2)))
            index = field.HitTestPos(ptRel)[1]
            return index
        return 0

    @RunOnMainSync
    def GetAbsolutePointAtTextPosition(self, index):
        uiView = self.stackManager.GetUiViewByModel(self)
        if uiView and uiView.view:
            field = uiView.view
            f = self.GetAbsoluteFrame()
            ptRel = field.PointFromPosition(index)
            ptAbs = wx.Point(self.stackManager.view.ToDIP(int(ptRel[0] + f.Left)+2),
                             self.stackManager.view.ToDIP(int((f.Height - ptRel[1]) + f.Top - 2 - self.properties["font_size"]/2)))
            return ptAbs
        return (0,0)



class TextField(TextBaseProxy):
    """
    TextField proxy objects are the user-accessible objects exposed to event handler code for text field objects.
    """

    @property
    def is_editable(self):
        model = self._model
        if not model: return False
        return model.GetProperty("is_editable")
    @is_editable.setter
    def is_editable(self, val):
        model = self._model
        if not model: return
        model.SetProperty("is_editable", bool(val))

    @property
    def is_multiline(self):
        model = self._model
        if not model: return False
        return model.GetProperty("is_multiline")
    @is_multiline.setter
    def is_multiline(self, val):
        model = self._model
        if not model: return
        model.SetProperty("is_multiline", bool(val))

    @property
    def selection(self):
        model = self._model
        if not model: return False
        return model.GetSelection()
    @selection.setter
    def selection(self, val):
        model = self._model
        if not model: return
        if isinstance(val, (list, tuple)) and len(val) == 2:
            if isinstance(val[0], int) and isinstance(val[1], int):
                model.SetSelection(val[0], val[1])
                return
        raise TypeError("selection must be a list of 2 numbers (start_position, end_position)")

    @property
    def selected_text(self):
        model = self._model
        if not model: return False
        return model.GetSelectedText()
    @selected_text.setter
    def selected_text(self, val):
        model = self._model
        if not model: return
        if isinstance(val,str):
            model.SetSelectedText(val)
            return
        raise TypeError("selected_text must be a string")

    def point_to_index(self, point):
        model = self._model
        if not model: return None
        return model.GetTextPositionAtAbsolutePoint(point)

    def index_to_point(self, index):
        model = self._model
        if not model: return None
        return model.GetAbsolutePointAtTextPosition(index)

    @RunOnMainSync
    def index_to_row_col(self, index):
        model = self._model
        if not model: return (0,0)
        return model.IndexToRowCol(None, index)

    @RunOnMainSync
    def row_col_to_index(self, row, col):
        model = self._model
        if not model: return 0
        return model.RowColToIndex(None, row, col)

    @property
    @RunOnMainSync
    def has_focus(self):
        model = self._model
        if not model: return False

        uiView = model.stackManager.GetUiViewByModel(model)
        if uiView and uiView.view:
            return uiView.view.HasFocus()
        return False

    def select_all(self):
        model = self._model
        if not model: return
        model.Notify("selectAll")

    def enter(self):
        model = self._model
        if not model: return
        if model.didSetDown: return
        if not model.stackManager.isEditing and model.stackManager.runner and model.GetHandler("on_text_enter"):
            model.stackManager.runner.RunHandler(model, "on_text_enter", None)

    def focus(self):
        model = self._model
        if not model: return

        if not model.stackManager.isEditing and model.stackManager.runner:
            model.stackManager.runner.SetFocus(self)
