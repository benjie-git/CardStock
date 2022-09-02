import wx
from uiView import *
from embeddedImages import radio_on, radio_off
from uiTextLabel import wordwrap

# Native Button Mouse event positions on Mac are offset (?!?)
MAC_BUTTON_OFFSET_HACK = wx.Point(6,4)


class UiButton(UiView):
    """
    This class is a controller that coordinates management of a Button view, based on data from a ButtonModel.
    """
    radioOnBmp = None
    radioOffBmp = None

    def __init__(self, parent, stackManager, model):
        self.stackManager = stackManager
        self.button = self.CreateButton(stackManager, model)
        super().__init__(parent, stackManager, model, self.button)
        self.mouseDownInside = False
        if not UiButton.radioOnBmp:
            UiButton.radioOnBmp = radio_on.GetBitmap()
            UiButton.radioOnBmp.SetScaleFactor(2)
            UiButton.radioOffBmp = radio_off.GetBitmap()
            UiButton.radioOffBmp.SetScaleFactor(2)

    def GetCursor(self):
        return wx.CURSOR_HAND

    def HackEvent(self, event):
        if wx.Platform == '__WXMAC__' and self.model.GetProperty("style") == "Border":
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
        if model.GetProperty("style") in ("Borderless", "Radio"):
            return None

        elif model.GetProperty("style") == "Border":
            button = wx.Button(parent=stackManager.view, label="Button", size=model.GetProperty("size"),
                               pos=self.stackManager.ConvRect(model.GetAbsoluteFrame()).BottomLeft,
                               style=wx.BORDER_DEFAULT)
            button.SetLabel(model.GetProperty("title"))
            button.Bind(wx.EVT_BUTTON, self.OnButton)
            button.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
            button.SetCursor(wx.Cursor(self.GetCursor()))
            return button

        elif model.GetProperty("style") == "Checkbox":
            button = wx.CheckBox(parent=stackManager.view, label="Button", size=model.GetProperty("size"),
                                 pos=self.stackManager.ConvRect(model.GetAbsoluteFrame()).BottomLeft)
            button.SetLabel(model.GetProperty("title"))
            button.SetValue(model.GetProperty("is_selected"))
            button.Bind(wx.EVT_CHECKBOX, self.OnCheckbox)
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
        elif key == "style":
            sm = self.stackManager
            sm.SelectUiView(None)
            sm.LoadCardAtIndex(sm.cardIndex, reload=True)
            sm.SelectUiView(sm.GetUiViewByModel(model))
        elif key == "is_selected":
            if self.view:
                self.view.SetValue(model.GetProperty("is_selected"))
            else:
                self.stackManager.view.Refresh()

    def OnMouseDown(self, event):
        style = self.model.GetProperty("style")
        if not self.stackManager.isEditing and style != "Border":
            self.mouseDownInside = True
            self.stackManager.view.Refresh()
            if style == "Radio":
                self.model.SetProperty("is_selected", True)
        super().OnMouseDown(event)

    def OnMouseUpOutside(self, event):
        if self.mouseDownInside and self.model.GetProperty("style") != "Border":
            self.mouseDownInside = False
            if self.stackManager:
                self.stackManager.view.Refresh()

    def OnMouseUp(self, event):
        if self.stackManager and not self.stackManager.isEditing and self.model.GetProperty("style") != "Border":
            if self.mouseDownInside:
                self.OnButton(event)
                self.mouseDownInside = False
                self.stackManager.view.Refresh()
        super().OnMouseUp(event)

    def OnKeyDown(self, event):
        if event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            if self.view and self.model.GetProperty("style") == "Checkbox":
                self.model.SetProperty("is_selected", not self.model.GetProperty("is_selected"))
                self.OnCheckbox(None)
                return
            else:
                self.OnButton(event)
        event.Skip()

    def OnButton(self, event):
        if not self.stackManager.isEditing:
            if self.stackManager.runner and self.model.GetHandler("on_click"):
                self.stackManager.runner.RunHandler(self.model, "on_click", event)

    def OnCheckbox(self, event):
        is_selected = self.view.GetValue()
        self.model.SetProperty("is_selected", is_selected)

    def Paint(self, gc):
        style = self.model.GetProperty("style")

        if style == "Borderless":
            title = self.model.GetProperty("title")
            if len(title):
                (width, height) = self.model.GetProperty("size")
                font = wx.Font(wx.FontInfo(wx.Size(0, 16)).Family(wx.FONTFAMILY_DEFAULT))
                lineHeight = font.GetPixelSize().height
                (startX, startY) = (0, (height+lineHeight)/2)

                lines = wordwrap(title, width, gc)
                line = lines.split("\n")[0]

                gc.SetFont(font)
                gc.SetTextForeground(wx.Colour('#404040' if self.mouseDownInside else 'black'))
                textWidth = gc.GetTextExtent(line).Width
                xPos = startX + (width - textWidth) / 2
                gc.DrawText(line, wx.Point(int(xPos), int(startY)))

        elif style == "Radio":
            (width, height) = self.model.GetProperty("size")

            radioBmp = UiButton.radioOnBmp if self.model.GetProperty("is_selected") else UiButton.radioOffBmp
            gc.DrawBitmap(radioBmp, 2, int((height + radioBmp.ScaledHeight)/2))

            title = self.model.GetProperty("title")
            if len(title):
                font = wx.Font(wx.FontInfo(wx.Size(0, 16)).Family(wx.FONTFAMILY_DEFAULT))
                lineHeight = font.GetPixelSize().height
                startPos = (25, (height+lineHeight)/2)
                gc.SetFont(font)
                gc.SetTextForeground(wx.Colour('black'))
                lines = wordwrap(title, width, gc)
                line = lines.split("\n")[0]
                gc.DrawText(line, startPos)

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
                    "on_click": "",
                    "on_selection_changed": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers
        self.initialEditHandler = "on_click"

        self.properties["name"] = "button_1"
        self.properties["title"] = "Button"
        self.properties["style"] = "Border"
        self.properties["is_selected"] = False

        self.propertyTypes["title"] = "string"
        self.propertyTypes["style"] = "choice"
        self.propertyTypes["is_selected"] = "bool"

        self.UpdatePropKeys("Default")

    def SetProperty(self, key, value, notify=True):
        if key == "style":
            self.UpdatePropKeys(value)
        elif key == "is_selected":
            if value != self.GetProperty("is_selected"):
                if value:
                    for m in self.get_radio_group():
                        if m.GetProperty("is_selected") and m != self:
                            m.SetProperty("is_selected", False)
                if self.stackManager and not self.stackManager.isEditing:
                    if self.stackManager.runner and self.GetHandler("on_selection_changed"):
                        self.stackManager.runner.RunHandler(self, "on_selection_changed", None, value)
        super().SetProperty(key, value, notify)

    def UpdatePropKeys(self, style):
        # Custom property order and mask for the inspector
        if style in ("Border", "Borderless"):
            self.propertyKeys = ["name", "title", "style", "position", "size"]
        else:
            self.propertyKeys = ["name", "title", "style", "is_selected", "position", "size"]

    def get_radio_group(self):
        g = []
        if self.GetProperty("style") == "Radio" and self.parent:
            for m in self.parent.childModels:
                if m.type == "button" and m.GetProperty("style") == "Radio":
                    g.append(m)
        return g

    def get_radio_group_selection(self):
        g = self.get_radio_group()
        for m in g:
            if m.GetProperty("is_selected"):
                return m
        return None


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
    def style(self):
        model = self._model
        if not model: return False
        return model.GetProperty("style")
    @style.setter
    def style(self, val):
        model = self._model
        if not model: return
        model.SetProperty("style", bool(val))

    @property
    def is_selected(self):
        model = self._model
        if not model: return False
        if model.GetProperty("style") in ("Border", "Borderless"):
            return False
        return model.GetProperty("is_selected")
    @is_selected.setter
    def is_selected(self, val):
        model = self._model
        if not model: return
        if model.GetProperty("style") not in ("Border", "Borderless"):
            model.SetProperty("is_selected", bool(val))

    def click(self):
        model = self._model
        if not model: return
        if model.stackManager.runner and model.GetHandler("on_click"):
            model.stackManager.runner.RunHandler(model, "on_click", None)

    def get_radio_group(self):
        model = self._model
        if not model: return []
        return [m.GetProxy() for m in model.get_radio_group()]

    def get_radio_group_selection(self):
        model = self._model
        if model:
            m = model.get_radio_group_selection()
            if m:
                return m.GetProxy()
        return None
