import traceback
import sys
import wx
from wx.adv import Sound
from time import sleep, time


class Runner():
    def __init__(self, stackView, sb=None):
        self.stackView = stackView
        self.statusBar = sb
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card

        self.clientVars = {
            "Wait": self.Wait,
            "Time": self.Time,
            "Alert": self.Alert,
            "Ask": self.Ask,
            "GotoCard": self.GotoCard,
            "GotoNextCard": self.GotoNextCard,
            "GotoPreviousCard": self.GotoPreviousCard,
            "GotoCardNumber": self.GotoCardNumber,
            "PlaySound": self.PlaySound,
            "StopSound": self.StopSound,
            "BroadcastMessage": self.BroadcastMessage
        }

        self.keyCodeStringMap = {
            wx.WXK_RETURN: "Return",
            wx.WXK_NUMPAD_ENTER: "Enter",
            wx.WXK_TAB: "Tab",
            wx.WXK_SPACE: "Space",
            wx.WXK_NUMPAD_SPACE: "Space",
            wx.WXK_NUMPAD_TAB: "Tab",
            wx.WXK_ESCAPE: "Escape",
            wx.WXK_LEFT: "Left",
            wx.WXK_RIGHT: "Right",
            wx.WXK_UP: "Up",
            wx.WXK_DOWN: "Down",
            wx.WXK_SHIFT: "Shift",
            wx.WXK_ALT: "Alt",
            wx.WXK_CONTROL: "Control"
        }
        if wx.GetOsVersion()[0] == wx.OS_MAC_OSX_DARWIN:
            self.keyCodeStringMap[wx.WXK_ALT] = "Option"
            self.keyCodeStringMap[wx.WXK_CONTROL] = "Command"
            self.keyCodeStringMap[wx.WXK_RAW_CONTROL] = "Control"

    def SetupForCurrentCard(self):
        # Setup clientVars with the current card's view names as variables
        self.clientVars["card"] = self.stackView.uiCard.model
        for k in self.cardVarKeys.copy():
            self.clientVars.pop(k)
            self.cardVarKeys.remove(k)
        for ui in self.stackView.GetAllUiViews():
            name = ui.model.GetProperty("name")
            self.clientVars[name] = ui.model
            self.cardVarKeys.append(name)

    def RunHandler(self, uiModel, handlerName, event, message=None):
        handlerStr = uiModel.handlers[handlerName]

        error_class = None
        line_number = None
        detail = None

        noValue = ["no value"]  # Use this if this var didn't exist/had no value (not even None)

        # Keep this method re-entrant, by storing old values (or lack thereof) of anything we set here,
        # (like self, key, etc.) and replacing or deleting them at the end of the run.
        oldVars = {}

        if "self" in self.clientVars:
            oldVars["self"] = self.clientVars["self"]
        else:
            oldVars["self"] = noValue
        self.clientVars["self"] = uiModel

        if message:
            if "message" in self.clientVars:
                oldVars["message"] = self.clientVars["message"]
            else:
                oldVars["message"] = noValue
            self.clientVars["message"] = message

        if event and handlerName.startswith("OnMouse"):
            mouseX, mouseY = self.stackView.ScreenToClient(event.GetEventObject().ClientToScreen(event.GetPosition()))
            if "mouseX" in self.clientVars:
                oldVars["mouseX"] = self.clientVars["mouseX"]
            else:
                oldVars["mouseX"] = noValue
            self.clientVars["mouseX"] = mouseX
            if "mouseY" in self.clientVars:
                oldVars["mouseY"] = self.clientVars["mouseY"]
            else:
                oldVars["mouseY"] = noValue
            self.clientVars["mouseY"] = mouseY

        if event and handlerName.startswith("OnKey"):
            code = event.GetKeyCode()
            if "keyName" in self.clientVars:
                oldVars["keyName"] = self.clientVars["keyName"]
            else:
                oldVars["keyName"] = noValue
            if code in self.keyCodeStringMap:
                self.clientVars["keyName"] = self.keyCodeStringMap[code]
            elif event.GetUnicodeKey() != wx.WXK_NONE:
                self.clientVars["keyName"] = chr(event.GetUnicodeKey())
            else:
                for k,v in oldVars.items():
                    if v == noValue:
                        if k in self.clientVars:
                            self.clientVars.pop(k)
                    else:
                        self.clientVars[k] = v
                return

        try:
            exec(handlerStr, self.clientVars)
        except SyntaxError as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = err.lineno
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            trace = traceback.extract_tb(tb)
            for i in range(len(trace)-1, -1, -1):
                if trace[i][0] == "<string>":
                    line_number = trace[i][1]
                    break

        # restore the old values from before this handler was called
        for k, v in oldVars.items():
            if v == noValue:
                if k in self.clientVars:
                    self.clientVars.pop(k)
            else:
                self.clientVars[k] = v

        if error_class:
            msg = f"{error_class} in {uiModel.GetProperty('name')}.{handlerName}(), line {line_number}: {detail}"
            print(msg)
            if self.statusBar:
                self.statusBar.SetStatusText(msg)

    def SetFocus(self, model):
        uiView = self.stackView.GetUiViewByModel(model)
        if uiView:
            uiView.view.SetFocus()

    def StopRunning(self):
        Sound.Stop()

    def BroadcastMessage(self, message):
        self.RunHandler(self.stackView.uiCard.model, "OnMessage", None, message)
        for ui in self.stackView.GetAllUiViews():
            self.RunHandler(ui.model, "OnMessage", None, message)

    def GotoCard(self, cardName):
        index = None
        for m in self.stackView.stackModel.cardModels:
            if m.GetProperty("name") == cardName:
                index = self.stackView.stackModel.cardModels.index(m)
        if index is not None:
            self.stackView.LoadCardAtIndex(index)

    def GotoCardNumber(self, cardIndex):
        if cardIndex > 0 and cardIndex <= len(self.stackView.stackModel.cardModels):
            self.stackView.LoadCardAtIndex(cardIndex-1)

    def GotoNextCard(self):
        cardIndex = self.stackView.cardIndex + 1
        if cardIndex >= len(self.stackView.stackModel.cardModels): cardIndex = 0
        self.stackView.LoadCardAtIndex(cardIndex)

    def GotoPreviousCard(self):
        cardIndex = self.stackView.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackView.stackModel.cardModels) - 1
        self.stackView.LoadCardAtIndex(cardIndex)

    def Wait(self, delay):
        self.stackView.RefreshNow()
        sleep(delay)

    def Time(self):
        return time()

    def Alert(self, title, message=""):
        self.stackView.RefreshNow()
        wx.MessageDialog(None, str(message), str(title), wx.OK).ShowModal()

    def Ask(self, title, message=""):
        self.stackView.RefreshNow()
        r = wx.MessageDialog(None, str(message), str(title), wx.YES_NO).ShowModal()
        return (r == wx.ID_YES)

    def PlaySound(self, filepath):
        Sound.PlaySound(filepath)

    def StopSound(self):
        Sound.Stop()
