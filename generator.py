import wx
import uiButton
import uiTextField
import uiTextLabel
import uiImage
import uiShape
import uiGroup
import uiCard


class StackGenerator(object):
    @classmethod
    def UiViewFromModel(self, parent, stackView, model):
        if model.type == "button":
            return uiButton.UiButton(parent, stackView, model)
        elif model.type == "textfield" or type == "field":
            return uiTextField.UiTextField(parent, stackView, model)
        elif model.type == "textlabel" or type == "label":
            return uiTextLabel.UiTextLabel(parent, stackView, model)
        elif model.type == "image":
            return uiImage.UiImage(parent, stackView, model)
        elif model.type == "group":
            return uiGroup.UiGroup(parent, stackView, model)
        elif model.type in ["pen", "line", "oval", "rect", "roundrect"]:
            return uiShape.UiShape(parent, stackView, type, model)
        return None

    @classmethod
    def ModelFromData(cls, stackView, data):
        m = None
        if data["type"] == "card":
            m = uiCard.CardModel(stackView)
        elif data["type"] == "button":
            m = uiButton.ButtonModel(stackView)
        elif data["type"] == "textfield":
            m = uiTextField.TextFieldModel(stackView)
        elif data["type"] == "textlabel":
            m = uiTextLabel.TextLabelModel(stackView)
        elif data["type"] == "image":
            m = uiImage.ImageModel(stackView)
        elif data["type"] == "group":
            m = uiGroup.GroupModel(stackView)
        elif data["type"] in ["pen", "line", "oval", "rect", "roundrect"]:
            m = uiShape.UiShape.CreateModelForType(stackView, data["type"])
        m.SetData(data)
        return m
