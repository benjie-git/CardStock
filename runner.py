import traceback
import sys
import wx
from wx.adv import Sound

class Runner():
    def __init__(self, stackView, sb=None):
        self.stackView = stackView
        self.locals = {}
        self.statusBar = sb
        self.globals = None

        self.keyCodeStringMap = {
            wx.WXK_RETURN:"Return",
            wx.WXK_NUMPAD_ENTER:"Enter",
            wx.WXK_TAB:"Tab",
            wx.WXK_SPACE:"Space",
            wx.WXK_NUMPAD_SPACE:"Space",
            wx.WXK_NUMPAD_TAB:"Tab",
            wx.WXK_ESCAPE:"Escape",
            wx.WXK_LEFT:"Left",
            wx.WXK_RIGHT:"Right",
            wx.WXK_UP:"Up",
            wx.WXK_DOWN:"Down",
            wx.WXK_SHIFT: "Shift",
            wx.WXK_ALT: "Alt",
            wx.WXK_CONTROL: "Control",
        }
        if wx.GetOsVersion()[0] == wx.OS_MAC_OSX_DARWIN:
            self.keyCodeStringMap[wx.WXK_ALT] = "Option"
            self.keyCodeStringMap[wx.WXK_CONTROL] = "Command"
            self.keyCodeStringMap[wx.WXK_RAW_CONTROL] = "Control"

    def RunHandler(self, uiModel, handlerName, event, message=None):
        if not self.globals:
            self.globals = {}
            self.globals["page"] = self.stackView.uiPage.model
            self.globals["Alert"] = Alert
            self.globals["Ask"] = Ask
            self.globals["PlaySound"] = PlaySound
            self.globals["StopSound"] = StopSound
            self.globals["BroadcastMessage"] = self.BroadcastMessage

            for ui in self.stackView.uiViews:
                self.globals[ui.model.GetProperty("name")] = ui.model

        handlerStr = uiModel.handlers[handlerName]

        error_class = None
        line_number = None
        detail = None

        self.locals["self"] = uiModel
        if message:
            self.locals["message"] = message

        if event and handlerName.startswith("OnMouse"):
            mouseX, mouseY = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            self.locals["mouseX"] = mouseX
            self.locals["mouseY"] = mouseY

        if event and handlerName.startswith("OnKey"):
            code = event.GetKeyCode()
            if code in self.keyCodeStringMap:
                self.locals["key"] = self.keyCodeStringMap[code]
            elif event.GetUnicodeKey() != wx.WXK_NONE:
                self.locals["key"] = chr(event.GetUnicodeKey())
            else:
                return

        try:
            exec(handlerStr, self.globals, self.locals)
        except SyntaxError as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = err.lineno
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]

        if "mouseX" in self.locals:
            self.locals.pop("mouseX")
        if "mouseY" in self.locals:
            self.locals.pop("mouseY")
        if "key" in self.locals:
            self.locals.pop("key")
        if "message" in self.locals:
            self.locals.pop("message")

        if error_class:
            msg = f"{error_class} in {uiModel.GetProperty('name')}.{handlerName}(), line {line_number}: {detail}"
            print(msg)
            if self.statusBar:
                self.statusBar.SetStatusText(msg)

    def StopRunning(self):
        Sound.Stop()

    def BroadcastMessage(self, message):
        self.RunHandler(self.stackView.uiPage.model, "OnMessage", None, message)
        for ui in self.stackView.uiViews:
            self.RunHandler(ui.model, "OnMessage", None, message)


def Alert(title, message=""):
    wx.MessageDialog(None, str(message), str(title), wx.OK).ShowModal()


def Ask(title, message=""):
    r = wx.MessageDialog(None, str(message), str(title), wx.YES_NO).ShowModal()
    return (r == wx.ID_YES)


def PlaySound(filepath):
    Sound.PlaySound(filepath)


def StopSound(filepath):
    Sound.Stop()
