import wx
import wx.stc as stc
from uiView import *


class UiTextBase(UiView):
    """
    This class is the abstract base controller for UiTextLabel and UiTextField.
    """

    def __init__(self, parent, stackManager, model, view):
        super().__init__(parent, stackManager, model, view)
        self.isInlineEditing = False
        self.inlineEditor = None
        self.font = None
        self.textColor = None
        self.settingValueInternally = False

    def DestroyView(self):
        self.StopInlineEditing(notify=False)
        super().DestroyView()

    def OnPropertyChanged(self, model, key):
        super().OnPropertyChanged(model, key)
        if key == "text":
            if self.model.type == "textlabel":
                self.stackManager.view.Refresh()
            else:
                if self.view:
                    wasEditable = self.view.IsEditable()
                    if not wasEditable:
                        self.view.SetEditable(True)
                    self.settingValueInternally = True
                    self.view.ChangeValue(str(self.model.GetProperty(key)))
                    self.settingValueInternally = False
                    self.view.SetEditable(wasEditable)
                    self.view.Refresh()
            self.OnResize(None)
        elif key in ["font", "fontSize", "textColor", "autoShrink"]:
            self.UpdateFont(model, self.view)
            self.OnResize(None)
            if self.view:
                self.view.Refresh()
            else:
                self.stackManager.view.Refresh()
        elif key == "alignment":
            if self.model.type == "textlabel":
                self.stackManager.view.Refresh()
            else:
                sm = self.stackManager
                sm.SelectUiView(None)
                sm.LoadCardAtIndex(sm.cardIndex, reload=True)
                sm.SelectUiView(sm.GetUiViewByModel(model))

    def ScaleFontSize(self, fontSize, view):
        # Adjust font sizes by platform
        if wx.Platform == '__WXMAC__':
            platformScale = 1.2 if isinstance(view, stc.StyledTextCtrl) else 1.4
        elif wx.Platform == '__WXMSW__':
            platformScale = 1.0 if isinstance(view, stc.StyledTextCtrl) else 1.2
        else:
            platformScale = 0.9 if isinstance(view, stc.StyledTextCtrl) else 1.4
        return max(1, int(fontSize * platformScale))

    def UpdateFont(self, model, view):
        familyName = model.GetProperty("font")

        size = self.ScaleFontSize(model.GetProperty("fontSize"), view)
        font = wx.Font(wx.FontInfo(wx.Size(0, size)).Family(self.FamilyForName(familyName)))
        color = wx.Colour(model.GetProperty("textColor"))
        if color.IsOk():
            colorStr = color.GetAsString(flags=wx.C2S_HTML_SYNTAX)
        else:
            colorStr = 'black'

        if view == None:
            self.font = font
            self.textColor = colorStr
            self.stackManager.view.Refresh()
        elif not isinstance(view, stc.StyledTextCtrl):
            view.SetFont(font)
            view.SetForegroundColour(colorStr)
        else:
            fontName = font.GetNativeFontInfoUserDesc()
            if "'" in fontName:
                # Multi-word faceName gets single-quoted
                fontName = font.GetNativeFontInfoUserDesc().split("'")[1]
            else:
                fontName = font.GetNativeFontInfoUserDesc().split(" ")[0]
            spec = f"fore:{colorStr},face:{fontName},size:{size}"
            view.StyleSetSpec(stc.STC_STYLE_DEFAULT, spec)
            view.StyleClearAll()

    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.StopInlineEditing()
        elif event.GetKeyCode() == wx.WXK_TAB:
            return
        event.Skip()

    def OnZoom(self, event):
        z = event.GetEventObject().GetZoom()
        if z != 0:
            event.GetEventObject().SetZoom(0)

    def OnLoseFocus(self, event):
        if self.isInlineEditing:
            self.StopInlineEditing()
        event.Skip()

    def StartInlineEditing(self):
        pass

    def StopInlineEditing(self, notify=True):
        pass

    @staticmethod
    def FamilyForName(name):
        if name == "Serif":
            return wx.FONTFAMILY_ROMAN
        if name == "Sans-Serif":
            return wx.FONTFAMILY_SWISS
        if name == "Fancy":
            return wx.FONTFAMILY_DECORATIVE
        if name == "Script":
            return wx.FONTFAMILY_SCRIPT
        if name == "Modern":
            return wx.FONTFAMILY_MODERN
        if name == "Mono":
            return wx.FONTFAMILY_TELETYPE
        return wx.FONTFAMILY_DEFAULT


class TextBaseModel(ViewModel):
    """
    This is the model for a TextLabel object.
    """

    def __init__(self, stackManager):
        super().__init__(stackManager)
        self.proxyClass = None

        self.properties["text"] = "Text"
        self.properties["alignment"] = "Left"
        self.properties["textColor"] = "black"
        self.properties["font"] = "Default"
        self.properties["fontSize"] = 18

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["textColor"] = "color"
        self.propertyTypes["font"] = "choice"
        self.propertyTypes["fontSize"] = "uint"
        self.propertyChoices["alignment"] = ["Left", "Center", "Right"]
        self.propertyChoices["font"] = ["Default", "Serif", "Sans-Serif", "Mono"]

        # Custom property order and mask for the inspector
        self.propertyKeys = ["name", "text", "alignment", "font", "fontSize", "textColor", "position", "size"]


class TextBaseProxy(ViewProxy):
    """
    TextBaseProxy objects are the abstract base class of the user-accessible objects exposed to event handler code for
    text labels and text fields.
    """

    @property
    def text(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("text")
    @text.setter
    def text(self, val):
        model = self._model
        if not model: return
        model.SetProperty("text", str(val))

    @property
    def alignment(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("alignment")
    @alignment.setter
    def alignment(self, val):
        if not isinstance(val, str):
            raise TypeError("alignment must be a string")
        model = self._model
        if not model: return
        model.SetProperty("alignment", val)

    @property
    def textColor(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("textColor")
    @textColor.setter
    def textColor(self, val):
        if not isinstance(val, str):
            raise TypeError("textColor must be a string")
        model = self._model
        if not model: return
        model.SetProperty("textColor", val)

    @property
    def font(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("font")
    @font.setter
    def font(self, val):
        if not isinstance(val, str):
            raise TypeError("font must be a string")
        model = self._model
        if not model: return
        model.SetProperty("font", val)

    @property
    def fontSize(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("fontSize")
    @fontSize.setter
    def fontSize(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("fontSize must be a number")
        model = self._model
        if not model: return
        model.SetProperty("fontSize", val)

    def AnimateTextColor(self, duration, endVal, onFinished=None, *args, **kwargs):
        if not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("endColor must be a string")

        model = self._model
        if not model: return

        endColor = wx.Colour(endVal)
        if endColor.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.textColor)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [endColor.Red(), endColor.Green(), endColor.Blue(), endColor.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("textColor", wx.Colour([animDict["origParts"][i] + animDict["offsets"][i] * progress for i in range(4)]))

            def internalOnFinished(animDict):
                if onFinished: self._model.stackManager.runner.EnqueueFunction(onFinished, *args, **kwargs)

            model.AddAnimation("textColor", duration, onUpdate, onStart, internalOnFinished)
