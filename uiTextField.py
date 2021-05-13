import wx
from uiView import *
from commands import SetPropertyCommand
from uiTextBase import *
import wx.stc as stc
from wx.lib.docview import CommandProcessor, Command
from codeRunnerThread import RunOnMain


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

        if model.GetProperty("multiline"):
            field = stc.StyledTextCtrl(parent=stackManager.view, size=model.GetProperty("size"),
                                       pos=self.stackManager.ConvRect(model.GetAbsoluteFrame()).BottomLeft,
                                       style=alignment | wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
            field.SetUseHorizontalScrollBar(False)
            field.SetTabWidth(3)
            field.SetUseTabs(0)
            field.SetWrapMode(stc.STC_WRAP_WORD)
            field.SetMarginWidth(1, 0)
            field.ChangeValue(text)
            field.Bind(stc.EVT_STC_CHANGE, self.OnTextChanged)
            field.Bind(stc.EVT_STC_ZOOM, self.OnZoom)
            field.EmptyUndoBuffer()
        else:
            field = CDSTextCtrl(parent=stackManager.view, size=model.GetProperty("size"),
                                pos=self.stackManager.ConvRect(model.GetAbsoluteFrame()).BottomLeft,
                                style=wx.TE_PROCESS_ENTER | alignment)
            field.ChangeValue(text)
            field.Bind(wx.EVT_TEXT, self.OnTextChanged)
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
            field.SetEditable(model.GetProperty("editable"))
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

    def StartInlineEditing(self):
        if self.stackManager.isEditing and not self.isInlineEditing:
            self.inlineStartText = self.model.GetProperty("text")
            self.view.SetEditable(True)
            self.view.SetFocus()
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
        if self.view and self.model.GetProperty("multiline"):
            self.view.SetScrollWidth(self.view.GetSize().Width-6)
        if event:
            event.Skip()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "multiline":
            self.StopInlineEditing(notify=False)
            sm = self.stackManager
            sm.SelectUiView(None)
            sm.LoadCardAtIndex(sm.cardIndex, reload=True)
            sm.SelectUiView(sm.GetUiViewByModel(model))
        elif key == "editable":
            if self.stackManager.isEditing:
                self.view.SetEditable(False)
            else:
                self.view.SetEditable(model.GetProperty(key))
        elif key == "selectAll":
            self.view.SelectAll()

    def OnTextEnter(self, event):
        if not self.stackManager.isEditing:
            if self.stackManager.runner and self.model.GetHandler("OnTextEnter"):
                self.stackManager.runner.RunHandler(self.model, "OnTextEnter", event)

    def OnTextChanged(self, event):
        if not self.stackManager.isEditing:
            if not self.settingValueInternally:
                self.model.SetProperty("text", event.GetEventObject().GetValue(), notify=False)
            if self.stackManager.runner and self.model.GetHandler("OnTextChanged"):
                self.stackManager.runner.RunHandler(self.model, "OnTextChanged", event)
        event.Skip()


class CDSTextCtrl(wx.TextCtrl):
    '''TextCtrl only handles Undo/Redo on Windows, not Mac or Liunx, so add that functionality here.'''
    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        if wx.Platform != '__WXMSW__':
            self.command_processor = CommandProcessor()
            self.Bind(wx.EVT_TEXT, self.OnTextChanged)
            self.oldText = self.GetValue()
            self.oldSel = self.GetSelection()
        else:
            self.command_processor = None

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

    def CanUndo(self):
        if wx.Platform != '__WXMSW__':
            return True
        return super().CanUndo()

    def CanRedo(self):
        if wx.Platform != '__WXMSW__':
            return True
        return super().CanRedo()

    def Undo(self):
        if wx.Platform != '__WXMSW__':
            if self.IsEditable():
                self.command_processor.Undo()
                self.oldText = self.GetValue()
        else:
            super().Undo()

    def Redo(self):
        if wx.Platform != '__WXMSW__':
            if self.IsEditable():
                self.command_processor.Redo()
                self.oldText = self.GetValue()
        else:
            super().Redo()


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
        handlers = {"OnSetup": "", "OnTextEnter": "", "OnTextChanged": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnTextEnter"

        self.properties["name"] = "field_1"
        self.properties["editable"] = True
        self.properties["multiline"] = False
        self.properties["fontSize"] = 12

        self.propertyTypes["editable"] = "bool"
        self.propertyTypes["multiline"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "editable", "multiline", "position", "size"]


class TextField(TextBaseProxy):
    """
    TextField proxy objects are the user-accessible objects exposed to event handler code for text field objects.
    """

    @property
    def editable(self):
        model = self._model
        if not model: return False
        return model.GetProperty("editable")
    @editable.setter
    def editable(self, val):
        model = self._model
        if not model: return
        model.SetProperty("editable", val)

    @property
    def multiline(self):
        model = self._model
        if not model: return False
        return model.GetProperty("multiline")
    @multiline.setter
    def multiline(self, val):
        model = self._model
        if not model: return
        model.SetProperty("multiline", val)

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
