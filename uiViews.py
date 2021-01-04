#!/usr/bin/python

# This is a draggable View, for adding a UI elements from the palate to the Page.

import wx
from wx.lib.docview import CommandProcessor, Command
import types

class UiView():
    def __init__(self, type, page, uiView):
        self.page = page
        self.view = uiView
        self.type = type
        self.handlers = {}
        self.lastEditedHandler = None
        self.handlers["OnMouseDown"] = ""
        self.handlers["OnMouseMove"] = ""
        self.handlers["OnMouseUp"] = ""
        self.handlers["OnMouseEnter"] = ""
        self.handlers["OnMouseExit"] = ""
        self.properties = {}
        self.customPropKeys = ["size", "position"]
        self.delta = ((0, 0))
        self.isEditing = False
        self.isSelected = False
        self.view.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.view.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
        self.view.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.view.Bind(wx.EVT_MOTION, self.OnMouseMove)
        if self.type != "page":
            self.view.Bind(wx.EVT_MOTION, self.page.uiPage.OnMouseMove)
        self.view.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)

        self.selectionBox = wx.Window(parent=self.view, id=wx.ID_ANY, pos=(0,0), size=self.view.GetSize(), style=0)
        self.selectionBox.Bind(wx.EVT_PAINT, self.OnPaintSelectionBox)
        self.selectionBox.SetBackgroundColour(None)
        self.selectionBox.Enable(False)
        self.selectionBox.Hide()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.selectionBox, 1, wx.EXPAND | wx.ALL, 0)
        #sizer.SetSizeHints(self.view)
        self.view.SetSizer(sizer)

    def SetEditing(self, editing):
        self.isEditing = editing
        self.SetSelected(False)

    def GetSelected(self):
        return self.isSelected

    def SetSelected(self, selected):
        self.isSelected = selected
        self.selectionBox.Show(selected)
        self.view.Refresh()
        self.view.Update()

    def GetHandlers(self):
        return self.handlers

    def GetHandler(self, name):
        if name in self.handlers:
            return self.handlers[name]
        return None

    def SetHandler(self, name, handlerStr):
        self.handlers[name] = handlerStr

    def GetProperty(self, name):
        if name in self.properties:
            return self.properties[name]
        elif name == "position":
            return list(self.view.GetPosition())
        elif name == "size":
            return list(self.view.GetSize())
        return None

    def SetProperty(self, name, value):
        if name in self.properties:
            self.properties[name] = value
        elif name == "position":
            self.view.SetPosition(value)
        elif name == "size":
            self.view.SetSize(value)

    def GetPropertyKeys(self):
        keys = []
        keys.extend(self.properties.keys())
        keys.extend(self.customPropKeys)
        return keys

    def GetProperties(self):
        props = self.properties.copy()
        for k in self.customPropKeys:
            props[k] = self.GetProperty(k)
        return props

    def GetData(self):
        return {"type":self.type,
                "id":self.view.GetId(),
                "handlers":self.handlers,
                "properties":self.GetProperties()}

    def SetData(self, data):
        self.handlers = data["handlers"]
        for k,v in data["properties"].items():
            self.SetProperty(k, v)

    def OnMouseDown(self, event):
        if self.type != "page" and self.isEditing:
            self.view.CaptureMouse()
            x, y = self.page.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
            originx, originy = self.view.GetPosition()
            dx = x - originx
            dy = y - originy
            self.moveOrigin = (originx, originy)
            self.delta = ((dx, dy))
            self.page.SelectUIView(self)
        else:
            if "OnMouseDown" in self.handlers:
                self.page.runner.RunHandler(self, "OnMouseDown", event)
            event.Skip()

    def OnMouseMove(self, event):
        if self.type != "page" and self.isEditing and event.Dragging():
            x, y = self.page.ScreenToClient(self.view.ClientToScreen(event.GetPosition()))
            fp = (x-self.delta[0], y-self.delta[1])
            self.view.Move(fp)
        elif not self.isEditing:
            if "OnMouseMove" in self.handlers:
                self.page.runner.RunHandler(self, "OnMouseMove", event)
            event.Skip()

    def OnMouseUp(self, event):
        if self.type != "page" and self.isEditing and self.view.HasCapture():
            endx, endy = self.view.GetPosition()
            command = MoveUIViewCommand(True, 'Move', self.page, self, (endx-self.moveOrigin[0], endy-self.moveOrigin[1]))
            self.view.SetPosition(self.moveOrigin)
            self.page.command_processor.Submit(command)
            self.view.ReleaseMouse()
        elif not self.isEditing:
            if "OnMouseUp" in self.handlers:
                self.page.runner.RunHandler(self, "OnMouseUp", event)
            event.Skip()

    def OnMouseEnter(self, event):
        if not self.isEditing:
            if "OnMouseEnter" in self.handlers:
                self.page.runner.RunHandler(self, "OnMouseEnter", event)
            event.Skip()

    def OnMouseExit(self, event):
        if not self.isEditing:
            if "OnMouseExit" in self.handlers:
                self.page.runner.RunHandler(self, "OnMouseExit", event)
            event.Skip()

    def OnButton(self, event):
        if not self.isEditing:
            if "OnClick" in self.handlers:
                self.page.runner.RunHandler(self, "OnClick", event)
            event.Skip()

    def OnTextEnter(self, event):
        if not self.isEditing:
            if "OnTextEnter" in self.handlers:
                self.page.runner.RunHandler(self, "OnTextEnter", event)
            event.Skip()

    def OnTextChanged(self, event):
        if not self.isEditing:
            if "OnTextChanged" in self.handlers:
                self.page.runner.RunHandler(self, "OnTextChanged", event)
            event.Skip()

    def OnIdle(self, event):
        if not self.isEditing:
            if "OnIdle" in self.handlers:
                self.page.runner.RunHandler(self, "OnIdle", event)
            event.Skip()

    def OnPaintSelectionBox(self, event):
        dc = wx.PaintDC(self.selectionBox)
        dc.SetPen(wx.Pen('Blue', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('Blue', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle((1, 1), (self.selectionBox.GetSize()[0]-2, self.selectionBox.GetSize()[1]-2))


class UiButton(UiView):
    def __init__(self, page, viewId):
        button = wx.Button(parent=page, id=viewId, label="Button")
        UiView.__init__(self, "button", page, button)

        # Add easier methods to a new Button
        def SetTitle(self, title):
            self.SetLabel(str(title))
        button.SetTitle = types.MethodType(SetTitle, button)

        def GetTitle(self):
            return self.GetLabel()
        button.SetTitle = types.MethodType(GetTitle, button)

        self.properties["name"] = "button_" + str(viewId-999)
        self.customPropKeys.append("title")
        self.SetProperty("title", "Button")

        handlers = {}
        handlers["OnClick"] = ""
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        self.view.Bind(wx.EVT_BUTTON, self.OnButton)

    def GetPropertyKeys(self):
        # Custom property order for the inspector
        return ["name", "title", "position", "size"]

    def GetProperty(self, name):
        if name == "title":
            return self.view.GetLabel()
        return UiView.GetProperty(self, name)

    def SetProperty(self, name, value):
        if name == "title":
            self.view.SetLabel(value)
        else:
            UiView.SetProperty(self,name, value)


class UiTextField(UiView):
    def __init__(self, page, viewId):
        field = wx.TextCtrl(parent=page, id=viewId, value="TextField", style=wx.TE_PROCESS_ENTER)

        # Add easier methods to a new TextCtrl
        def SetText(self, text):
            self.ChangeValue(str(text))
        field.SetText = types.MethodType(SetText, field)

        def GetText(self):
            return self.GetValue()
        field.GetText = types.MethodType(GetText, field)

        UiView.__init__(self, "textfield", page, field)
        self.properties["name"] = "field_" + str(viewId-999)
        self.customPropKeys.append("text")
        self.SetProperty("text", "Text")
        self.properties["editable"] = True

        handlers = {}
        handlers["OnTextEnter"] = ""
        handlers["OnTextChanged"] = ""
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        self.view.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
        self.view.Bind(wx.EVT_CHAR, self.OnTextChanged)

    def GetPropertyKeys(self):
        # Custom property order for the inspector
        return ["name", "text", "editable", "position", "size"]

    def GetProperty(self, name):
        if name == "text":
            return self.view.GetText()
        return UiView.GetProperty(self, name)

    def SetProperty(self, name, value):
        if name == "text":
            self.view.SetText(value)
        else:
            UiView.SetProperty(self,name, value)

    def SetEditing(self, editing):
        UiView.SetEditing(self, editing)
        if editing:
            self.view.SetEditable(False)
        else:
            self.view.SetEditable(self.GetProperty("editable"))


class UiPage(UiView):
    def __init__(self, page):
        UiView.__init__(self, "page", page, page)
        self.properties["name"] = "page_1"
        self.customPropKeys.remove("position")

        handlers = {}
        handlers["OnStart"] = ""
        handlers["OnIdle"] = ""
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

    def GetPropertyKeys(self):
        # Custom property order for the inspector
        return ["name", "size"]


class MoveUIViewCommand(Command):
    dragView = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.page = args[2]
        self.dragView = args[3]
        self.delta = args[4]
        self.viewId = self.dragView.view.GetId()

    def Do(self):
        uiView = self.page.GetUIViewById(self.viewId)
        pos = uiView.view.GetPosition()
        uiView.view.SetPosition((pos[0]+self.delta[0], pos[1]+self.delta[1]))
        return True

    def Undo(self):
        uiView = self.page.GetUIViewById(self.viewId)
        pos = uiView.view.GetPosition()
        uiView.view.SetPosition((pos[0]-self.delta[0], pos[1]-self.delta[1]))
        return True
