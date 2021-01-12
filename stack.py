#!/usr/bin/python

from uiCard import CardModel


class StackModel(object):
    def __init__(self):
        super().__init__()
        self.cardModels = []

    def AddCardModel(self, cardModel):
        self.cardModels.append(cardModel)

    def RemoveCardModel(self, cardModel):
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

    def SetRunner(self, runner):
        for cardModel in self.cardModels:
            cardModel.runner = runner
            for model in cardModel.childModels:
                model.runner = runner

    def GetData(self):
        return {"cards":[m.GetData() for m in self.cardModels]}

    def SetData(self, stackData):
        self.cardModels = []
        for data in stackData["cards"]:
            m = CardModel()
            m.SetData(data)
            self.AddCardModel(m)
