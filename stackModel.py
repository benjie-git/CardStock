#!/usr/bin/python

import wx
from uiView import ViewModel, ViewProxy
from uiCard import CardModel
import version

class StackModel(ViewModel):
    """
    This is the model for the stack.  It mostly just contains the cards as its children.
    """

    minSize = wx.Size(200, 200)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "stack"
        self.proxyClass = StackProxy

        self.properties["size"] = wx.Size(500, 500)
        self.properties["name"] = "stack"
        self.properties["canSave"] = False
        self.properties["canResize"] = True

        self.propertyTypes["canSave"] = 'bool'
        self.propertyTypes["canResize"] = 'bool'

        self.propertyKeys = []

        self.handlers = {"OnSetup": ""}

    def AppendCardModel(self, cardModel):
        cardModel.stackModel = self
        self.childModels.append(cardModel)

    def InsertCardModel(self, index, cardModel):
        cardModel.stackModel = self
        self.childModels.insert(index, cardModel)

    def RemoveCardModel(self, cardModel):
        cardModel.stackModel = None
        self.childModels.remove(cardModel)

    def GetCardModel(self, i):
        return self.childModels[i]

    def GetDirty(self):
        for card in self.childModels:
            if card.GetDirty():
                return True
        return False

    def SetDirty(self, dirty):
        for card in self.childModels:
            card.SetDirty(dirty)

    def GetData(self):
        data = super().GetData()
        data["cards"] = [m.GetData() for m in self.childModels]
        data["properties"].pop("position")
        data["properties"].pop("name")
        data["CardStock_stack_format"] = 1
        data["CardStock_stack_version"] = version.VERSION
        return data

    def SetData(self, stackData):
        super().SetData(stackData)
        self.childModels = []
        for data in stackData["cards"]:
            m = CardModel(self.stackManager)
            m.SetData(data)
            self.AppendCardModel(m)


class StackProxy(ViewProxy):
    @property
    def numCards(self):
        return len(self._model.childModels)
