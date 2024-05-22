# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
from uiView import ViewModel, ViewProxy
from uiCard import CardModel
import version
import migrations
from codeRunnerThread import RunOnMainSync, RunOnMainAsync


class StackModel(ViewModel):
    """
    This is the model for the stack.  It mostly just contains the cards as its children.
    """

    minSize = wx.Size(200, 200)

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.type = "stack"
        self.proxyClass = Stack

        self.properties["name"] = "stack"
        self.properties["can_save"] = False
        self.properties["author"] = ""
        self.properties["info"] = ""

        self.propertyTypes["stack_name"] = 'static'
        self.propertyTypes["can_save"] = 'bool'
        self.propertyTypes["author"] = 'string'
        self.propertyTypes["info"] = 'text'

        self.propertyKeys = ["stack_name", "author", "can_save", "info"]

        self.handlers = {"on_setup": "", "on_exit_stack": ""}
        self.initialEditHandler = "on_setup"

    def GetProperty(self, key):
        if key == "stack_name":
            if self.stackManager.designer and self.stackManager.designer.filename:
                return self.stackManager.designer.filename
            return ""
        else:
            return super().GetProperty(key)

    def AppendCardModel(self, cardModel):
        cardModel.parent = self
        self.childModels.append(cardModel)

    def InsertCardModel(self, index, cardModel):
        cardModel.parent = self
        self.childModels.insert(index, cardModel)

    def InsertNewCard(self, name, atIndex):
        newCard = CardModel(self.stackManager)
        newCard.SetProperty("name", self.DeduplicateName(name, [m.GetProperty("name") for m in self.childModels]))
        newCard.SetProperty("size", self.stackManager.uiCard.model.GetProperty("size"))
        newCard.SetProperty("can_resize", self.stackManager.uiCard.model.GetProperty("can_resize"))
        if atIndex == -1:
            self.AppendCardModel(newCard)
        else:
            self.InsertCardModel(atIndex, newCard)
            newIndex = self.childModels.index(self.stackManager.uiCard.model)
            self.stackManager.cardIndex = newIndex
        return newCard

    def RemoveCardModel(self, cardModel):
        cardModel.parent = None
        self.childModels.remove(cardModel)

    def GetCardModel(self, i):
        return self.childModels[i]

    def GetModelFromPath(self, path):
        parts = path.split('.')
        if len(parts) and parts[0] == "":
            return self
        m = self
        for p in parts:
            found = False
            for c in m.childModels:
                if c.properties['name'] == p:
                    m = c
                    found = True
                    break
            if not found:
                return None
        return m

    def GetData(self):
        data = super().GetData()
        data["cards"] = [m.GetData() for m in self.childModels]
        data["properties"].pop("position")
        data["properties"].pop("size")
        data["properties"].pop("name")
        data["CardStock_stack_format"] = version.FILE_FORMAT_VERSION
        data["CardStock_stack_version"] = version.VERSION
        return data

    def SetData(self, stackData):
        formatVer = stackData["CardStock_stack_format"]
        if formatVer != version.FILE_FORMAT_VERSION:
            migrations.MigrateDataFromFormatVersion(formatVer, stackData)

        super().SetData(stackData)
        self.childModels = []
        for data in stackData["cards"]:
            m = CardModel(self.stackManager)
            m.parent = self
            m.SetData(data)
            self.AppendCardModel(m)

        if formatVer != version.FILE_FORMAT_VERSION:
            migrations.MigrateModelFromFormatVersion(formatVer, self)


class Stack(ViewProxy):
    @property
    def num_cards(self):
        return len(self._model.childModels)

    @property
    def info(self):
        return self._model.GetProperty("info")

    @property
    def current_card(self):
        if self._model.didSetDown: return None
        return self._model.stackManager.uiCard.model.GetProxy()

    def card_with_number(self, number):
        model = self._model
        if model.didSetDown: return None
        if not isinstance(number, int):
            raise TypeError("card_with_number(): number is not an int")
        if number < 1 or number > len(model.childModels):
            raise ValueError("card_with_number(): number is out of bounds")
        return model.childModels[number-1].GetProxy()

    def return_from_stack(self, result=None):
        self._model.stackManager.runner.return_from_stack(result)

    def get_setup_value(self):
        return self._model.stackManager.runner.GetStackSetupValue()

    def broadcast_message(self, message):
        if not self._model: return
        if not isinstance(message, str):
            raise TypeError("broadcast_message(): message must be a string")

        for c in self._model.childModels:
            c.broadcast_message(message)

    @RunOnMainAsync
    def show_info(self):
        self._model.stackManager.ShowStackInfo()

    def add_card(self, name="card", atNumber=0):
        if not isinstance(name, str):
            raise TypeError("add_card(): name is not a string")
        atNumber = int(atNumber)
        if atNumber < 0 or atNumber > len(self._model.childModels)+1:
            raise ValueError("add_card(): atNumber is out of bounds")

        @RunOnMainSync
        def func():
            if self._model.didSetDown: return None
            return self._model.InsertNewCard(name, atNumber-1).GetProxy()
        return func()
