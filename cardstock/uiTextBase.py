# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
        self.text_color = None
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
        elif key in ["font", "font_size", "text_color", "can_auto_shrink", "rotation", "is_bold", "is_italic", "is_underlined"]:
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

    def ScaleFontSize(self, font_size, view):
        # Adjust font sizes by platform
        if wx.Platform == '__WXMAC__':
            platformScale = 1.2 if isinstance(view, stc.StyledTextCtrl) else 1.4
        elif wx.Platform == '__WXMSW__':
            platformScale = 1.0 if isinstance(view, stc.StyledTextCtrl) else 1.2
        else:
            platformScale = 0.9 if isinstance(view, stc.StyledTextCtrl) else 1.4
        return max(1, int(font_size * platformScale))

    def UpdateFont(self, model, view):
        familyName = model.GetProperty("font")

        fd = self.stackManager.view.FromDIP
        td = self.stackManager.view.ToDIP
        size = fd(self.ScaleFontSize(model.GetProperty("font_size"), view))
        font = wx.Font(wx.FontInfo(wx.Size(0, int(size)))
                       .Family(self.FamilyForName(familyName))
                       .Bold(model.properties["is_bold"])
                       .Italic(model.properties["is_italic"])
                       .Underlined(model.properties["is_underlined"]))
        color = wx.Colour(model.GetProperty("text_color"))
        if color.IsOk():
            colorStr = color.GetAsString(flags=wx.C2S_HTML_SYNTAX)
        else:
            colorStr = 'black'

        if view is None:
            self.font = font
            self.text_color = colorStr
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
            spec = f"fore:{colorStr},face:{fontName},size:{td(size)}"
            view.StyleSetSpec(stc.STC_STYLE_DEFAULT, spec)
            view.StyleClearAll()

    def OnKeyDown(self, event):
        if self.stackManager.isEditing:
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.StopInlineEditing()
                return
            elif event.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER] and event.ShiftDown():
                self.StopInlineEditing()
                return
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
        self.properties["text_color"] = "black"
        self.properties["font"] = "Default"
        self.properties["font_size"] = 18
        self.properties["is_bold"] = False
        self.properties["is_italic"] = False
        self.properties["is_underlined"] = False

        self.propertyTypes["text"] = "string"
        self.propertyTypes["alignment"] = "choice"
        self.propertyTypes["text_color"] = "color"
        self.propertyTypes["font"] = "choice"
        self.propertyTypes["font_size"] = "uint"
        self.propertyTypes["is_bold"] = "bool"
        self.propertyTypes["is_italic"] = "bool"
        self.propertyTypes["is_underlined"] = "bool"


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
    def text_color(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("text_color")
    @text_color.setter
    def text_color(self, val):
        if not isinstance(val, str):
            raise TypeError("text_color must be a string")
        model = self._model
        if not model: return
        model.SetProperty("text_color", val)

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
    def font_size(self):
        model = self._model
        if not model: return 0
        return model.GetProperty("font_size")
    @font_size.setter
    def font_size(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("font_size must be a number")
        model = self._model
        if not model: return
        model.SetProperty("font_size", val)

    @property
    def is_bold(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("is_bold")
    @is_bold.setter
    def is_bold(self, val):
        if not isinstance(val, bool):
            raise TypeError("is_bold must be True or False")
        model = self._model
        if not model: return
        model.SetProperty("is_bold", val)

    @property
    def is_italic(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("is_italic")
    @is_italic.setter
    def is_italic(self, val):
        if not isinstance(val, bool):
            raise TypeError("is_italic must be True or False")
        model = self._model
        if not model: return
        model.SetProperty("is_italic", val)

    @property
    def is_underlined(self):
        model = self._model
        if not model: return ""
        return model.GetProperty("is_underlined")
    @is_underlined.setter
    def is_underlined(self, val):
        if not isinstance(val, bool):
            raise TypeError("is_underlined must be True or False")
        model = self._model
        if not model: return
        if model.type == "textfield":
            raise TypeError("Text Field objects do not support underlined text.")
        model.SetProperty("is_underlined", val)

    def animate_font_size(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_font_size(): duration must be a number")
        if not isinstance(endVal, (int, float)):
            raise TypeError("animate_font_size(): end_thickness must be a number")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_font_size(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        def onStart(animDict):
            origVal = self.font_size
            animDict["origVal"] = origVal
            animDict["offset"] = endVal - origVal

        def onUpdate(progress, animDict):
            model.SetProperty("font_size", animDict["origVal"] + animDict["offset"] * ease(progress, easing))

        def internalOnFinished(animDict):
            if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

        model.AddAnimation("font_size", duration, onUpdate, onStart, internalOnFinished)

    def animate_text_color(self, duration, endVal, easing=None, on_finished=None):
        if not isinstance(duration, (int, float)):
            raise TypeError("animate_text_color(): duration must be a number")
        if not isinstance(endVal, str):
            raise TypeError("animate_text_color(): end_color must be a string")
        if easing and not isinstance(easing, str):
            raise TypeError('animate_text_color(): easing, if provided, must be one of "In", "Out", or "InOut"')

        model = self._model
        if not model: return

        if easing:
            easing = easing.lower()

        end_color = wx.Colour(endVal)
        if end_color.IsOk():
            def onStart(animDict):
                origVal = wx.Colour(self.text_color)
                origParts = [origVal.Red(), origVal.Green(), origVal.Blue(), origVal.Alpha()]
                animDict["origParts"] = origParts
                endParts = [end_color.Red(), end_color.Green(), end_color.Blue(), end_color.Alpha()]
                animDict["offsets"] = [endParts[i]-origParts[i] for i in range(4)]

            def onUpdate(progress, animDict):
                model.SetProperty("text_color", wx.Colour([int(animDict["origParts"][i] + animDict["offsets"][i] * ease(progress, easing)) for i in range(4)]))

            def internalOnFinished(animDict):
                if on_finished: self._model.stackManager.runner.EnqueueFunction(on_finished)

            model.AddAnimation("text_color", duration, onUpdate, onStart, internalOnFinished)
