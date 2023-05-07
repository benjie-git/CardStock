# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import wx
import uiButton
import uiTextField
import uiTextLabel
import uiImage
import uiWebView
import uiShape
import uiGroup
import uiCard


class StackGenerator(object):
    """
    Just some simple class methods for creating UiViews by model,
    and Models by data (a model serialized into a dictionary).
    """

    @classmethod
    def UiViewFromModel(self, parent, stackManager, model):
        if model.type == "button":
            return uiButton.UiButton(parent, stackManager, model)
        elif model.type == "textfield" or model.type == "field":
            return uiTextField.UiTextField(parent, stackManager, model)
        elif model.type == "textlabel" or model.type == "label":
            return uiTextLabel.UiTextLabel(parent, stackManager, model)
        elif model.type == "image":
            return uiImage.UiImage(parent, stackManager, model)
        elif model.type == "webview":
            return uiWebView.UiWebView(parent, stackManager, model)
        elif model.type == "group":
            return uiGroup.UiGroup(parent, stackManager, model)
        elif model.type in ["pen", "line", "oval", "rect", "polygon", "roundrect"]:
            return uiShape.UiShape(parent, stackManager, model)
        return None

    @classmethod
    def ModelFromData(cls, stackManager, data):
        m = None
        if data["type"] == "card":
            m = uiCard.CardModel(stackManager)
        elif data["type"] == "button":
            m = uiButton.ButtonModel(stackManager)
        elif data["type"] == "textfield":
            m = uiTextField.TextFieldModel(stackManager)
        elif data["type"] == "textlabel":
            m = uiTextLabel.TextLabelModel(stackManager)
        elif data["type"] == "image":
            m = uiImage.ImageModel(stackManager)
        elif data["type"] == "webview":
            m = uiWebView.WebViewModel(stackManager)
        elif data["type"] == "group":
            m = uiGroup.GroupModel(stackManager)
        elif data["type"] in ["pen", "line", "oval", "rect", "polygon", "roundrect"]:
            m = uiShape.UiShape.CreateModelForType(stackManager, data["type"])
        m.SetData(data)
        return m

    @classmethod
    def ModelFromType(cls, stackManager, typeStr):
        m = None
        if typeStr == "card":
            m = uiCard.CardModel(stackManager)
        elif typeStr == "button":
            m = uiButton.ButtonModel(stackManager)
        elif typeStr == "textfield" or typeStr == "field":
            m = uiTextField.TextFieldModel(stackManager)
        elif typeStr == "textlabel" or typeStr == "label":
            m = uiTextLabel.TextLabelModel(stackManager)
        elif typeStr == "image":
            m = uiImage.ImageModel(stackManager)
        elif typeStr == "webview":
            m = uiWebView.WebViewModel(stackManager)
        elif typeStr == "group":
            m = uiGroup.GroupModel(stackManager)
        elif typeStr in ["pen", "line", "oval", "rect", "polygon", "roundrect"]:
            m = uiShape.UiShape.CreateModelForType(stackManager, typeStr)
        return m
