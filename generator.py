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
        elif model.type in ["pen", "line", "oval", "rect", "round_rect"]:
            return uiShape.UiShape(parent, stackView, type, model)
        return None

    @classmethod
    def ModelFromData(cls, data):
        m = None
        if data["type"] == "card":
            m = uiCard.CardModel()
        elif data["type"] == "button":
            m = uiButton.ButtonModel()
        elif data["type"] == "textfield":
            m = uiTextField.TextFieldModel()
        elif data["type"] == "textlabel":
            m = uiTextLabel.TextLabelModel()
        elif data["type"] == "image":
            m = uiImage.ImageModel()
        elif data["type"] == "group":
            m = uiGroup.GroupModel()
        elif data["type"] in ["pen", "line", "oval", "rect", "round_rect"]:
            m = uiShape.UiShape.CreateModelForType(data["type"])
        m.SetData(data)
        return m
