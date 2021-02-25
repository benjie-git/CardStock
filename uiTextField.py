import wx
from uiView import *
import wx.stc as stc
from wx.lib.docview import CommandProcessor, Command


class UiTextField(UiView):
    """
    This class is a controller that coordinates management of a TextField view, based on data from a TextFieldModel.
    """

    def __init__(self, parent, stackManager, model=None):
        if not model:
            model = TextFieldModel(stackManager)
            model.SetProperty("name", stackManager.uiCard.model.GetNextAvailableNameInCard("field_"), False)

        self.stackManager = stackManager
        self.field = self.CreateField(stackManager, model)

        super().__init__(parent, stackManager, model, self.field)

    def CreateField(self, stackManager, model):
        text = model.GetProperty("text")
        alignment = wx.TE_LEFT
        if model.GetProperty("alignment") == "Right":
            alignment = wx.TE_RIGHT
        elif model.GetProperty("alignment") == "Center":
            alignment = wx.TE_CENTER

        if model.GetProperty("multiline"):
            field = stc.StyledTextCtrl(parent=stackManager.view, style=alignment | wx.BORDER_SIMPLE | stc.STC_WRAP_WORD)
            field.SetUseHorizontalScrollBar(False)
            field.SetWrapMode(stc.STC_WRAP_WORD)
            field.SetMarginWidth(1, 0)
            field.ChangeValue(text)
            field.Bind(stc.EVT_STC_CHANGE, self.OnTextChanged)
            field.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
            field.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
            field.EmptyUndoBuffer()
        else:
            field = CDSTextCtrl(parent=stackManager.view, style=wx.TE_PROCESS_ENTER | alignment)
            field.ChangeValue(text)
            field.Bind(wx.EVT_TEXT, self.OnTextChanged)
            field.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
            field.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
            field.EmptyUndoBuffer()

        self.BindEvents(field)
        field.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)

        if stackManager.isEditing:
            field.SetEditable(False)
        else:
            field.SetEditable(model.GetProperty("editable"))
        return field

    def SetView(self, view):
        super().SetView(view)

    def GetCursor(self):
        if self.stackManager.isEditing:
            return wx.CURSOR_HAND
        else:
            return wx.CURSOR_IBEAM

    def OnFocus(self, event):
        if not self.stackManager.isEditing:
            self.stackManager.lastFocusedTextField = self
        event.Skip()

    def OnLoseFocus(self, event):
        if self.stackManager.isEditing:
            self.field.SetEditable(False)
        event.Skip()

    def OnResize(self, event):
        if self.field and self.model.GetProperty("multiline"):
                self.field.SetScrollWidth(self.field.GetSize().Width-6)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            wasEditable = self.field.IsEditable()
            if not wasEditable:
                self.field.SetEditable(True)
            self.field.ChangeValue(str(self.model.GetProperty(key)))
            self.field.SetEditable(wasEditable)
            self.field.Refresh(True)
        elif key == "alignment" or key == "multiline":
            self.stackManager.SelectUiView(None)
            self.doNotCache = True
            self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)
            self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(self.model))
        elif key == "editable":
            if self.stackManager.isEditing:
                self.field.SetEditable(False)
            else:
                self.field.SetEditable(model.GetProperty(key))
        elif key == "selectAll":
            self.field.SelectAll()

    def OnTextEnter(self, event):
        if not self.stackManager.isEditing:
            if self.stackManager.runner and self.model.GetHandler("OnTextEnter"):
                self.stackManager.runner.RunHandler(self.model, "OnTextEnter", event)

    def OnTextChanged(self, event):
        self.model.SetProperty("text", event.GetEventObject().GetValue(), notify=False)
        if not self.stackManager.isEditing:
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


class TextFieldModel(ViewModel):
    """
    This is the model for a TextField object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "textfield"
        self.proxyClass = TextFieldProxy

        # Add custom handlers to the top of the list
        handlers = {"OnTextEnter": "", "OnTextChanged": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["editable"] = True
        self.properties["multiline"] = False

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["editable"] = "bool"
        self.propertyTypes["multiline"] = "bool"
        self.propertyChoices["alignment"] = ["Left", "Center", "Right"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "editable", "multiline", "position", "size"]


class TextFieldProxy(ViewProxy):
    """
    TextFieldProxy objects are the user-accessible objects exposed to event handler code for text field objects.
    """

    @property
    def text(self):
        return self._model.GetProperty("text")
    @text.setter
    def text(self, val):
        self._model.SetProperty("text", str(val))

    @property
    def alignment(self):
        return self._model.GetProperty("alignment")
    @alignment.setter
    def alignment(self, val):
        self._model.SetProperty("alignment", val)

    @property
    def editable(self):
        return self._model.GetProperty("editable")
    @editable.setter
    def editable(self, val):
        self._model.SetProperty("editable", val)

    @property
    def multiline(self):
        return self._model.GetProperty("multiline")
    @multiline.setter
    def multiline(self, val):
        self._model.SetProperty("multiline", val)

    def SelectAll(self): self._model.Notify("selectAll")

    def DoEnter(self):
        if self._model.stackManager.runner:
            self._model.stackManager.runner.RunHandler(self._model, "OnTextEnter", None)
