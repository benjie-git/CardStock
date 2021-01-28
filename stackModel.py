#!/usr/bin/python

from uiView import ViewModel
from uiCard import CardModel


class StackModel(ViewModel):
    def __init__(self, stackView):
        super().__init__(stackView)
        self.type = "stack"
        self.handlers = {"OnSetup": ""}
        self.propertyKeys = ["size"]
        self.properties["size"] = [500, 500]
        self.properties["name"] = "stack"

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
        return data

    def SetData(self, stackData):
        super().SetData(stackData)
        self.childModels = []
        for data in stackData["cards"]:
            m = CardModel(self.stackView)
            m.SetData(data)
            self.AppendCardModel(m)

    # --------- User-accessible view methods -----------

    def GetNumCards(self): return len(self.childModels)
