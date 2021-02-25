import wx
from uiView import *
import generator


class UiCard(UiView):
    """
    This class is a controller that coordinates management of the stack view while this card is shown,
    based on data from a CardModel.
    The UiCard.view is the same wx.Window as the stackManager.view.
    There is only ever one UiCard, and it gets its model replaced with another CardModel when switching cards.
    """

    def __init__(self, parent, stackManager, model):
        if not model.GetProperty("name"):
            model.SetProperty("name", model.GetNextAvailableNameInCard("card_"), False)

        super().__init__(parent, stackManager, model, stackManager.view)
        self.stackManager.stackModel.SetProperty("size", self.view.GetSize(), False)
        bg = wx.Colour(self.model.GetProperty("bgColor"))
        if not bg:
            bg = wx.Colour('white')
        self.view.SetBackgroundColour(bg)

    def SetView(self, view):
        super().SetView(view)
        self.model.SetProperty("size", self.view.GetSize(), False)
        bg = wx.Colour(self.model.GetProperty("bgColor"))
        if not bg:
            bg = wx.Colour('white')
        self.view.SetBackgroundColour(bg)

    def SetModel(self, model):
        super().SetModel(model)
        if self.view:
            bg = wx.Colour(self.model.GetProperty("bgColor"))
            if not bg:
                bg = wx.Colour('white')
            self.view.SetBackgroundColour(bg)

    def GetCursor(self):
        return None

    def OnResize(self, event):
        self.stackManager.stackModel.SetProperty("size", self.view.GetSize())

    def PaintSelectionBox(self, gc):
        if self.isSelected and self.stackManager.tool.name == "hand":
            f = self.model.GetAbsoluteFrame()
            gc.SetPen(wx.Pen('Blue', 3, wx.PENSTYLE_SHORT_DASH))
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.DrawRectangle(f.Deflate(1))

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush('blue', wx.BRUSHSTYLE_SOLID))
            box = self.GetResizeBoxRect()
            gc.DrawRectangle(wx.Rect(box.TopLeft + f.TopLeft, box.Size))

    def GetResizeBoxRect(self):
        # the resize box/handle should hang out of the frame, to allow grabbing it from behind
        # native widgets which can obscure the full frame.
        s = self.model.GetProperty("size")
        return wx.Rect(s.width-12, s.height-12, 12, 12)

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "name":
            self.stackManager.designer.UpdateCardList()
        elif key == "bgColor":
            bg = wx.Colour(self.model.GetProperty(key))
            if not bg:
                bg = wx.Colour('white')
            self.view.SetBackgroundColour(bg)
            self.view.Refresh(True)

    def OnKeyDown(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnKeyDown"):
            self.stackManager.runner.RunHandler(self.model, "OnKeyDown", event)

    def OnKeyUp(self, event):
        if self.stackManager.runner and self.model.GetHandler("OnKeyUp"):
            self.stackManager.runner.RunHandler(self.model, "OnKeyUp", event)

    def OnIdle(self, event):
        super().OnIdle(event)
        for child in self.stackManager.uiViews:
            child.OnIdle(event)


class CardModel(ViewModel):
    """
    The CardModel allows access to a few properties that actually live in the stack.  This is because the Designer
    allows editing cards, but not the stack model itself.  These properties are size, canSave, and canResize.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "card"
        self.proxyClass = CardProxy
        # Add custom handlers to the top of the list
        handlers = {"OnSetup": "", "OnShowCard": "", "OnHideCard": "", "OnKeyDown": "", "OnKeyUp": ""}
        for k,v in self.handlers.items():
            handlers[k] = v
        self.handlers = handlers

        # Custom property order and mask for the inspector
        self.properties["bgColor"] = "white"
        self.propertyKeys = ["name", "bgColor", "size", "canSave", "canResize"]

        self.propertyTypes["bgColor"] = "color"
        self.propertyTypes["canSave"] = 'bool'
        self.propertyTypes["canResize"] = 'bool'

    def SetProperty(self, key, value, notify=True):
        if key in ["size", "canSave", "canResize"]:
            self.parent.SetProperty(key, value, notify)
        else:
            super().SetProperty(key, value, notify)

    def GetProperty(self, key):
        if key in ["size", "canSave", "canResize"]:
            return self.parent.GetProperty(key)
        else:
            return super().GetProperty(key)

    def GetFrame(self):
        s = self.parent.GetProperty("size")
        return wx.Rect((0,0), s)

    def GetAbsoluteFrame(self):
        return self.GetFrame()

    def GetAllChildModels(self):
        allModels = []
        for child in self.childModels:
            allModels.append(child)
            if child.type == "group":
                allModels.extend(child.GetAllChildModels())
        return allModels

    def GetDirty(self):
        if self.isDirty:
            return True
        for child in self.GetAllChildModels():
            if child.isDirty:
                return True
        return False

    def SetDirty(self, isDirty):
        if isDirty:
            self.isDirty = True
        else:
            self.isDirty = False
            for child in self.GetAllChildModels():
                child.isDirty = False

    def GetData(self):
        data = super().GetData()
        data["childModels"] = []
        for m in self.childModels:
            data["childModels"].append(m.GetData())
        data["properties"].pop("size")
        data["properties"].pop("position")
        return data

    def SetData(self, data):
        super().SetData(data)
        for childData in data["childModels"]:
            self.childModels.append(generator.StackGenerator.ModelFromData(self.stackManager, childData))

    def AddChild(self, model):
        self.childModels.append(model)
        self.isDirty = True

    def RemoveChild(self, model):
        self.childModels.remove(model)
        self.isDirty = True

    def GetDedupNameList(self, name, exclude):
        names = [m.properties["name"] for m in self.GetAllChildModels()]
        for n in exclude:
            if n in names:
                names.remove(n)
        return names

    def DeduplicateNameInCard(self, name, exclude=None, include=None):
        if exclude is None: exclude = []
        if include is None: include = []
        names = self.GetDedupNameList(name, exclude)
        names.extend(include)
        return super().DeduplicateName(name, names)

    def GetNextAvailableNameInCard(self, name, exclude=None):
        if exclude is None: exclude = []
        names = self.GetDedupNameList(name, exclude)
        return super().GetNextAvailableName(name, names)


class CardProxy(ViewProxy):
    """
    CardProxy objects are the user-accessible objects exposed to event handler code for card objects.
    """

    @property
    def bgColor(self):
        return self._model.GetProperty("bgColor")
    @bgColor.setter
    def bgColor(self, val):
        self._model.SetProperty("bgColor", val)

    @property
    def index(self):
        return self._model.parent.childModels.index(self._model)

    def AnimateBgColor(self, duration, endVal, onFinished=None):
        origVal = wx.Colour(self.bgColor)
        endVal = wx.Colour(endVal)
        if origVal.IsOk() and endVal.IsOk() and endVal != origVal:
            origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
            endParts = [endVal.Red(), endVal.Green(), endVal.Blue(), endVal.Alpha()]
            offsets = [endParts[i]-origParts[i] for i in range(4)]
            def f(progress):
                self.bgColor = [origParts[i]+offsets[i]*progress for i in range(4)]
            self._model.AddAnimation("bgColor", duration, f, onFinished)
        else:
            self._model.AddAnimation("bgColor", duration, None, onFinished)
