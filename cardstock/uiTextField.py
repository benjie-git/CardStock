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
        field = self.CreateField(stackManager, model)

        super().__init__(parent, stackManager, model, field)

    def CreateField(self, stackManager, model):
        text = model.GetProperty("text")
        alignment = wx.TE_LEFT
        if model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        pos = self.stackManager.ConvRect(model.GetAbsoluteFrame()).TopLeft
        if model.GetProperty("isMultiline"):
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
        else:
            field = CDSTextCtrl(parent=stackManager.view, size=model.GetProperty("size"), pos=pos,
                                style=wx.TE_PROCESS_ENTER | alignment)
            field.ChangeValue(text)
            field.Bind(wx.EVT_TEXT, self.OnTextChanged)
            field.Bind(CDS_EVT_TEXT_UNDO, self.OnTextChanged)
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
            field.SetEditable(model.GetProperty("isEditable"))
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
        if self.view and self.model.GetProperty("isMultiline"):
            self.view.SetScrollWidth(self.view.GetSize().Width-6)
        if event:
            event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "isMultiline":
            self.StopInlineEditing(notify=False)
            sm = self.stackManager
            sm.SelectUiView(None)
            sm.LoadCardAtIndex(sm.cardIndex, reload=True)
            sm.SelectUiView(sm.GetUiViewByModel(model))
        elif key == "isEditable":
            if self.stackManager.isEditing:
                self.view.SetEditable(False)
            else:
                self.view.SetEditable(model.GetProperty(key))
        elif key == "selectAll":
            self.view.SelectAll()

    def OnTextEnter(self, event):
        if not self.stackManager.isEditing:
            def f():
                if self.stackManager.runner and self.model.GetHandler("OnTextEnter"):
                    self.stackManager.runner.RunHandler(self.model, "OnTextEnter", event)
            wx.CallAfter(f)

    def OnTextChanged(self, event):
        if not self.stackManager.isEditing:
            if not self.settingValueInternally:
                self.model.SetProperty("text", event.GetEventObject().GetValue(), notify=False)
                if self.stackManager.runner and self.model.GetHandler("OnTextChanged"):
                    self.stackManager.runner.RunHandler(self.model, "OnTextChanged", event)
        event.Skip()

    def OnSTCTextChanged(self, event):
        if not self.stackManager.isEditing:
            if event.GetModificationType()%2 == 1:
                if not self.settingValueInternally:
                    self.model.SetProperty("text", event.GetEventObject().GetValue(), notify=False)
                    if self.stackManager.runner and self.model.GetHandler("OnTextChanged"):
                        self.stackManager.runner.RunHandler(self.model, "OnTextChanged", event)
        event.Skip()


CDS_EVT_TEXT_UNDO_TYPE = wx.NewEventType()
CDS_EVT_TEXT_UNDO = wx.PyEventBinder(CDS_EVT_TEXT_UNDO_TYPE, 1)


class CDSTextCtrl(wx.TextCtrl):
    """TextCtrl only handles Undo/Redo on Windows, not Mac or Linux, so add that functionality here."""
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.command_processor = CommandProcessor()
        self.Bind(wx.EVT_TEXT, self.OnTextChanged)
        self.oldText = self.GetValue()
        self.oldSel = self.GetSelection()

    def OnTextChanged(self, event):
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
        handlers = {"OnSetup": "", "OnTextChanged": "", "OnTextEnter": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnTextEnter"

        self.properties["name"] = "field_1"
        self.properties["isEditable"] = True
        self.properties["isMultiline"] = False
        self.properties["fontSize"] = 12

        self.propertyTypes["isEditable"] = "bool"
        self.propertyTypes["isMultiline"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "isEditable", "isMultiline", "position", "size"]

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
            isMultiline = self.GetProperty("isMultiline")
            sel = uiView.view.GetSelection()
            length = len(self.GetProperty("text"))
            s = uiView.view.GetRange(0,sel[0]) + text + uiView.view.GetRange(sel[1], length)
            if isMultiline:
                pos = (uiView.view.GetScrollPos(wx.HORIZONTAL), uiView.view.GetScrollPos(wx.VERTICAL))
            self.SetProperty("text", s)
            uiView.view.SetSelection(sel[0], sel[0]+len(text))
            if isMultiline:
                uiView.view.ScrollToLine(pos[1])
                uiView.view.ScrollToColumn(pos[0])

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


class TextField(TextBaseProxy):
    """
    TextField proxy objects are the user-accessible objects exposed to event handler code for text field objects.
    """

    @property
    def isEditable(self):
        model = self._model
        if not model: return False
        return model.GetProperty("isEditable")
    @isEditable.setter
    def isEditable(self, val):
        model = self._model
        if not model: return
        model.SetProperty("isEditable", bool(val))

    @property
    def isMultiline(self):
        model = self._model
        if not model: return False
        return model.GetProperty("isMultiline")
    @isMultiline.setter
    def isMultiline(self, val):
        model = self._model
        if not model: return
        model.SetProperty("isMultiline", bool(val))

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
    def selectedText(self):
        model = self._model
        if not model: return False
        return model.GetSelectedText()
    @selectedText.setter
    def selectedText(self, val):
        model = self._model
        if not model: return
        if isinstance(val,str):
            model.SetSelectedText(val)
            return
        raise TypeError("selectedText must be a string")

    def SelectAll(self):
        model = self._model
        if not model: return
        model.Notify("selectAll")

    def Enter(self):
        model = self._model
        if not model: return
        if model.didSetDown: return
        if model.stackManager.runner and model.GetHandler("OnTextEnter"):
            model.stackManager.runner.RunHandler(model, "OnTextEnter", None)
