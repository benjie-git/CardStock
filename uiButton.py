import wx
from uiView import *
from killableThread import RunOnMain

# Native Button Mouse event positions on Mac are offset (?!?)
MAC_BUTTON_OFFSET_HACK = wx.Point(6,4)


class UiButton(UiView):
    """
    This class is a controller that coordinates management of a Button view, based on data from a ButtonModel.
    """

    def __init__(self, parent, stackManager, model):
        self.stackManager = stackManager
        self.button = self.CreateButton(stackManager, model)
        super().__init__(parent, stackManager, model, self.button)

    def GetCursor(self):
        return wx.CURSOR_HAND

    def BindEvents(self, view):
        if view == self.view:
            super().BindEvents(self.button)

    def HackEvent(self, event):
        if wx.Platform == '__WXMAC__' and self.model.GetProperty("border"):
            event.SetPosition(event.GetPosition() - MAC_BUTTON_OFFSET_HACK)
        return event

    def FwdOnMouseDown( self, event): self.stackManager.OnMouseDown( self, self.HackEvent(event))
    def FwdOnMouseMove( self, event): self.stackManager.OnMouseMove( self, self.HackEvent(event))
    def FwdOnMouseUp(   self, event): self.stackManager.OnMouseUp(   self, self.HackEvent(event))

    def CreateButton(self, stackManager, model):
        button = wx.Button(parent=stackManager.view, label="Button", size=model.GetProperty("size"),
                           pos=self.stackManager.ConvRect(model.GetAbsoluteFrame()).BottomLeft,
                           style=(wx.BORDER_DEFAULT if model.GetProperty("border") else wx.BORDER_NONE))
        button.SetLabel(model.GetProperty("title"))
        button.Bind(wx.EVT_BUTTON, self.OnButton)
        button.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        button.SetCursor(wx.Cursor(self.GetCursor()))
        return button

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "title":
            self.button.SetLabel(str(self.model.GetProperty(key)))
        elif key == "border":
            self.stackManager.SelectUiView(None)
            self.stackManager.LoadCardAtIndex(self.stackManager.cardIndex, reload=True)
            self.stackManager.SelectUiView(self.stackManager.GetUiViewByModel(self.model))

    def OnKeyDown(self, event):
        if event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            self.OnButton(event)
        event.Skip()

    def OnButton(self, event):
        if not self.stackManager.isEditing:
            if self.stackManager.runner and self.model.GetHandler("OnClick"):
                self.stackManager.runner.RunHandler(self.model, "OnClick", event)

    def Paint(self, gc):
        if self.stackManager.isEditing:
            gc.SetPen(wx.Pen('Gray', 1, wx.PENSTYLE_DOT))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(self.model.GetAbsoluteFrame())


class ButtonModel(ViewModel):
    """
    This is the model for a Button object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "button"
        self.proxyClass = Button

        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "",
                    "OnClick": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "OnClick"

        self.properties["name"] = "button_1"
        self.properties["title"] = "Button"
        self.properties["border"] = True
        self.propertyTypes["title"] = "string"
        self.propertyTypes["border"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "title", "border", "position", "size"]


class Button(ViewProxy):
    """
    Button proxy objects are the user-accessible objects exposed to event handler code for button objects.
    Based on ProxyView, and adds title, border, and Click().
    """

    @property
    def title(self):
        return self._model.GetProperty("title")
    @title.setter
    def title(self, val):
        if not isinstance(val, str):
            raise TypeError("title must be a string")
        self._model.SetProperty("title", val)

    @property
    def border(self):
        return self._model.GetProperty("border")
    @border.setter
    def border(self, val):
        self._model.SetProperty("border", val)

    def Click(self):
        if self._model.stackManager.runner and self._model.GetHandler("OnClick"):
            self._model.stackManager.runner.RunHandler(self._model, "OnClick", None)
