#!/usr/bin/python

import wx
from uiView import ViewModel, ViewProxy
from uiCard import CardModel
import version
from killableThread import RunOnMain

class StackModel(ViewModel):
    """
    This is the model for the stack.  It mostly just contains the cards as its children.
    """

    minSize = wx.Size(200, 200)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "stack"
        self.proxyClass = Stack

        self.properties["size"] = wx.Size(500, 500)
        self.properties["name"] = "stack"
        self.properties["canSave"] = False
        self.properties["canResize"] = True

        self.propertyTypes["canSave"] = 'bool'
        self.propertyTypes["canResize"] = 'bool'

        self.propertyKeys = []

        self.handlers = {"OnSetup": ""}

    def AppendCardModel(self, cardModel):
        cardModel.parent = self
        self.childModels.append(cardModel)

    def InsertCardModel(self, index, cardModel):
        cardModel.parent = self
        self.childModels.insert(index, cardModel)

    def InsertNewCard(self, name, atIndex):
        card = CardModel(self.stackManager)
        card.SetProperty("name", self.DeduplicateName(name, [m.GetProperty("name") for m in self.childModels]))
        if atIndex == -1:
            self.AppendCardModel(card)
        else:
            self.InsertCardModel(atIndex, card)
            newIndex = self.childModels.index(self.stackManager.uiCard.model)
            self.stackManager.cardIndex = newIndex
        return card

    def RemoveCardModel(self, cardModel):
        cardModel.parent = None
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


class Stack(ViewProxy):
    @property
    def numCards(self):
        return len(self._model.childModels)

    @property
    def currentCard(self):
        return self._model.stackManager.uiCard.model.GetProxy()

    @RunOnMain
    def AddCard(self, name="card", atIndex=-1):
        if not isinstance(name, str):
            raise TypeError("name is not a string")
        atIndex = int(atIndex)
        if atIndex < -1 or atIndex > len(self._model.childModels)-1:
            raise ValueError("atIndex is out of bounds")
        return self._model.InsertNewCard(name, atIndex).GetProxy()
