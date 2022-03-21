import browser
import wx_compat as wx
from models import *
from views import *
import runner
import json


class StackManager(object):
    def __init__(self, canvas, fabric):
        super().__init__(self)

        canvas.preserveObjectStacking = True
        canvas.selection = False
        self.canvas = canvas

        self.fabric = fabric
        self.stackModel = None
        self.uiCard = UiCard(None, self, None)
        self.cardIndex = 0
        self.runner = runner.Runner(self)

    def LoadFromStr(self, stackStr):
        stackJSON = json.loads(stackStr)
        self.Load(stackJSON)

    def Load(self, stackJSON):
        self.stackModel = StackModel(self)
        stackDict = stackJSON
        self.stackModel.SetData(stackDict)
        s = self.stackModel.GetProperty("size")
        self.canvas.setWidth(s.width)
        self.canvas.setHeight(s.height)
        self.LoadCardAtIndex(0)

    def LoadCardAtIndex(self, cardIndex):
        if len(self.stackModel.childModels) > cardIndex:
            self.cardIndex = cardIndex
            card = self.stackModel.childModels[cardIndex]
            self.runner.SetupForCard(card)
            self.uiCard.Load(card)

    def ConvPoint(self, p):
        cardSize = self.uiCard.model.GetProperty("size")
        return wx.Point(p.x, cardSize.height - p.y)

    def ConvRect(self, r):
        cardSize = self.uiCard.model.GetProperty("size")
        return wx.Rect(r.x, cardSize.height - (r.y+r.height), r.width, r.height)

    def GetViewForModel(self, model):
        def FindSubView(uiView):
            if uiView.model == model:
                return uiView
            for ui in uiView.uiViews.values():
                found = FindSubView(ui)
                if found:
                    return found
            return None
        return FindSubView(self.uiCard)

    def OnPropertyChanged(self, model, key):
        ui = self.GetViewForModel(model)
        if ui:
            ui.OnPropertyChanged(key)

    @classmethod
    def ModelFromData(cls, stackManager, data):
        m = None
        if data["type"] == "card":
            m = CardModel(stackManager)
        elif data["type"] == "button":
            m = ButtonModel(stackManager)
        elif data["type"] == "textfield":
            m = TextFieldModel(stackManager)
        elif data["type"] == "textlabel":
            m = TextLabelModel(stackManager)
        elif data["type"] == "image":
            m = ImageModel(stackManager)
        elif data["type"] == "webview":
            m = WebViewModel(stackManager)
        elif data["type"] == "group":
            m = GroupModel(stackManager)
        elif data["type"] in ["pen", "line"]:
            m = LineModel(stackManager, data["type"])
        elif data["type"] in ["rect", "oval", "polygon"]:
            m = ShapeModel(stackManager, data["type"])
        elif data["type"] == "roundrect":
            m = RoundRectModel(stackManager, data["type"])

        m.SetData(data)
        return m

    @classmethod
    def ModelFromType(cls, stackManager, typeStr):
        m = None
        if typeStr == "card":
            m = CardModel(stackManager)
        elif typeStr == "button":
            m = ButtonModel(stackManager)
        elif typeStr == "textfield" or typeStr == "field":
            m = TextFieldModel(stackManager)
        elif typeStr == "textlabel" or typeStr == "label":
            m = TextLabelModel(stackManager)
        elif typeStr == "image":
            m = ImageModel(stackManager)
        elif typeStr == "webview":
            m = WebViewModel(stackManager)
        elif typeStr == "group":
            m = GroupModel(stackManager)
        elif typeStr in ["pen", "line"]:
            m = LineModel(stackManager, typeStr)
        elif typeStr in ["rect", "oval", "polygon"]:
            m = ShapeModel(stackManager, typeStr)
        elif typeStr == "roundrect":
            m = RoundRectModel(stackManager, typeStr)

        return m

    @classmethod
    def UiViewFromModel(cls, parent, stackManager, model):
        if model.type == "button":
            return UiButton(parent, stackManager, model)
        elif model.type == "textfield" or model.type == "field":
            return UiTextField(parent, stackManager, model)
        elif model.type == "textlabel" or model.type == "label":
            return UiTextLabel(parent, stackManager, model)
        elif model.type == "image":
            return UiImage(parent, stackManager, model)
        elif model.type == "webview":
            return UiWebView(parent, stackManager, model)
        elif model.type == "group":
            return UiGroup(parent, stackManager, model)
        elif model.type in ["line", "pen", "oval", "rect", "roundrect", "polygon"]:
            return UiShape(parent, stackManager, model)
        return None
