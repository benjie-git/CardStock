#!/usr/bin/python

from uiView import ViewModel
from uiCard import CardModel


class StackModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "stack"
        self.handlers = {"OnStackStart": ""}
        self.propertyKeys = ["size"]
        self.properties["size"] = [500, 500]
        self.properties["name"] = "stack"
        self.cardModels = []

    def AppendCardModel(self, cardModel):
        cardModel.stackModel = self
        self.cardModels.append(cardModel)

    def InsertCardModel(self, index, cardModel):
        cardModel.stackModel = self
        self.cardModels.insert(index, cardModel)

    def RemoveCardModel(self, cardModel):
        cardModel.stackModel = None
        self.cardModels.remove(cardModel)

    def GetCardModel(self, i):
        return self.cardModels[i]

    def GetDirty(self):
        for card in self.cardModels:
            if card.GetDirty():
                return True
        return False

    def SetDirty(self, dirty):
        for card in self.cardModels:
            card.SetDirty(dirty)

    def GetData(self):
        data = super().GetData()
        data["cards"] = [m.GetData() for m in self.cardModels]
        data["properties"].pop("position")
        data["properties"].pop("name")
        data["CardStock_stack_format"] = 1
        return data

    def SetData(self, stackData):
        super().SetData(stackData)
        self.cardModels = []
        for data in stackData["cards"]:
            m = CardModel(self.stackView)
            m.SetData(data)
            self.AppendCardModel(m)