import wx
from uiView import *
from uiTextLabel import wordwrap

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
        self.mouseDownInside = False

    def GetCursor(self):
        return wx.CURSOR_HAND

    def HackEvent(self, event):
        if wx.Platform == '__WXMAC__' and self.model.GetProperty("has_border"):
            event.SetPosition(event.GetPosition() - MAC_BUTTON_OFFSET_HACK)
        return event

    def FwdOnMouseDown(self, event):
        self.stackManager.OnMouseDown( self, self.HackEvent(event))

    def FwdOnMouseMove(self, event):
        self.stackManager.OnMouseMove( self, self.HackEvent(event))

    def FwdOnMouseUp(self, event):
        self.stackManager.OnMouseUp(   self, self.HackEvent(event))
        if wx.Platform == "__WXMAC__":
            event.Skip(False)  # Fix double MouseUp events on Mac

    def CreateButton(self, stackManager, model):
        if not model.GetProperty("has_border"):
            return None

        button = wx.Button(parent=stackManager.view, label="Button", size=model.GetProperty("size"),
                           pos=self.stackManager.ConvRect(model.GetAbsoluteFrame()).BottomLeft,
                           style=wx.BORDER_DEFAULT)
        button.SetLabel(model.GetProperty("title"))
        button.Bind(wx.EVT_BUTTON, self.OnButton)
        button.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        button.SetCursor(wx.Cursor(self.GetCursor()))
        return button

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "title":
            if self.button:
                self.button.SetLabel(str(self.model.GetProperty(key)))
            else:
                self.stackManager.view.Refresh()
        elif key == "has_border":
            sm = self.stackManager
            sm.SelectUiView(None)
            sm.LoadCardAtIndex(sm.cardIndex, reload=True)
            sm.SelectUiView(sm.GetUiViewByModel(model))

    def OnMouseDown(self, event):
        if not self.stackManager.isEditing and not self.button:
            self.mouseDownInside = True
            self.stackManager.view.Refresh()
        super().OnMouseDown(event)

    def OnMouseUpOutside(self, event):
        if not self.button and self.mouseDownInside:
            self.mouseDownInside = False
            if self.stackManager:
                self.stackManager.view.Refresh()

    def OnMouseUp(self, event):
        if self.stackManager and not self.stackManager.isEditing and not self.button:
            if self.mouseDownInside:
                self.OnButton(event)
                self.mouseDownInside = False
                self.stackManager.view.Refresh()
        super().OnMouseUp(event)

    def OnKeyDown(self, event):
        if event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            self.OnButton(event)
        event.Skip()

    def OnButton(self, event):
        if not self.stackManager.isEditing:
            if self.stackManager.runner and self.model.GetHandler("on_click"):
                self.stackManager.runner.RunHandler(self.model, "on_click", event)

    def Paint(self, gc):
        if not self.button:
            title = self.model.GetProperty("title")
            if len(title):
                (width, height) = self.model.GetProperty("size")
                font = wx.Font(wx.FontInfo(wx.Size(0, 15)).Family(wx.FONTFAMILY_DEFAULT))
                lineHeight = font.GetPixelSize().height
                (startX, startY) = (0, (height+lineHeight)/2)

                lines = wordwrap(title, width, gc)
                line = lines.split("\n")[0]

                gc.SetFont(font)
                gc.SetTextForeground(wx.Colour('#404040' if self.mouseDownInside else 'black'))
                textWidth = gc.GetTextExtent(line).Width
                xPos = startX + (width - textWidth) / 2
                gc.DrawText(line, wx.Point(xPos, startY))

        super().Paint(gc)


class ButtonModel(ViewModel):
    """
    This is the model for a Button object.
    """

    minSize = wx.Size(34,20)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "button"
        self.proxyClass = Button

        # Add custom handlers to the top of the list
        handlers = {"on_setup": "",
                    "on_click": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_click"

        self.properties["name"] = "button_1"
        self.properties["title"] = "Button"
        self.properties["has_border"] = True
        self.propertyTypes["title"] = "string"
        self.propertyTypes["has_border"] = "bool"

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "title", "has_border", "position", "size"]


class Button(ViewProxy):
    """
    Button proxy objects are the user-accessible objects exposed to event handler code for button objects.
    Based on ProxyView, and adds title, border, and Click().
    """

    @property
    def title(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("title")
    @title.setter
    def title(self, val):
        model = self._model
        if not model: return
        model.SetProperty("title", str(val))

    @property
    def has_border(self):
        model = self._model
        if not model: return False
        return model.GetProperty("has_border")
    @has_border.setter
    def has_border(self, val):
        model = self._model
        if not model: return
        model.SetProperty("has_border", bool(val))

    def click(self):
        model = self._model
        if not model: return
        if model.stackManager.runner and model.GetHandler("on_click"):
            model.stackManager.runner.RunHandler(model, "on_click", None)
