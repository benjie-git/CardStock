import traceback
import sys
import os
import wx
from wx.adv import Sound
from time import sleep, time


class Runner():
    def __init__(self, stackView, sb=None):
        self.stackView = stackView
        self.statusBar = sb
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card
        self.pressedKeys = []
        self.soundCache = {}
        self.timers = []

        self.clientVars = {
            "Wait": self.Wait,
            "RunAfterDelay": self.RunAfterDelay,
            "Time": self.Time,
            "Paste": self.Paste,
            "Alert": self.Alert,
            "Ask": self.Ask,
            "GotoCard": self.GotoCard,
            "GotoNextCard": self.GotoNextCard,
            "GotoPreviousCard": self.GotoPreviousCard,
            "GotoCardNumber": self.GotoCardNumber,
            "PlaySound": self.PlaySound,
            "StopSound": self.StopSound,
            "BroadcastMessage": self.BroadcastMessage,
            "IsKeyPressed": self.IsKeyPressed,
            "stack": self.stackView.stackModel.GetProxy(),
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
        self.clientVars["card"] = self.stackView.uiCard.model.GetProxy()
        for k in self.cardVarKeys.copy():
            self.clientVars.pop(k)
            self.cardVarKeys.remove(k)
        for ui in self.stackView.GetAllUiViews():
            name = ui.model.GetProperty("name")
            self.clientVars[name] = ui.model.GetProxy()
            self.cardVarKeys.append(name)

    def CleanupFromRun(self):
        for t in self.timers:
            t.Stop()
        self.timers = []

    def RunHandler(self, uiModel, handlerName, event, arg=None):
        handlerStr = uiModel.handlers[handlerName].strip()

        if handlerStr == "": return

        error_class = None
        line_number = None
        detail = None

        noValue = ("no", "value")  # Use this if this var didn't exist/had no value (not even None)

        # Keep this method re-entrant, by storing old values (or lack thereof) of anything we set here,
        # (like self, key, etc.) and replacing or deleting them at the end of the run.
        oldVars = {}

        if "self" in self.clientVars:
            oldVars["self"] = self.clientVars["self"]
        else:
            oldVars["self"] = noValue
        self.clientVars["self"] = uiModel.GetProxy()

        if arg and handlerName == "OnMessage":
            if "message" in self.clientVars:
                oldVars["message"] = self.clientVars["message"]
            else:
                oldVars["message"] = noValue
            self.clientVars["message"] = arg

        if arg and handlerName == "OnIdle":
            if "elapsedTime" in self.clientVars:
                oldVars["elapsedTime"] = self.clientVars["elapsedTime"]
            else:
                oldVars["elapsedTime"] = noValue
            self.clientVars["elapsedTime"] = arg

        if event and handlerName.startswith("OnMouse"):
            mousePos = self.stackView.ScreenToClient(wx.GetMousePosition())
            if "mousePos" in self.clientVars:
                oldVars["mousePos"] = self.clientVars["mousePos"]
            else:
                oldVars["mousePos"] = noValue
            self.clientVars["mousePos"] = mousePos

        if event and handlerName.startswith("OnKey"):
            if "keyName" in self.clientVars:
                oldVars["keyName"] = self.clientVars["keyName"]
            else:
                oldVars["keyName"] = noValue
            keyName = self.KeyNameForEvent(event)
            if keyName:
                self.clientVars["keyName"] = keyName
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

    def KeyNameForEvent(self, event):
        code = event.GetKeyCode()
        if code in self.keyCodeStringMap:
            return self.keyCodeStringMap[code]
        elif event.GetUnicodeKey() != wx.WXK_NONE:
            return chr(event.GetUnicodeKey())
        return None

    def OnKeyDown(self, event):
        keyName = self.KeyNameForEvent(event)
        if keyName and keyName not in self.pressedKeys:
            self.pressedKeys.append(keyName)

    def OnKeyUp(self, event):
        keyName = self.KeyNameForEvent(event)
        if keyName and keyName in self.pressedKeys:
            self.pressedKeys.remove(keyName)

    def StopRunning(self):
        self.soundCache = {}
        Sound.Stop()

    def SetFocus(self, obj):
        uiView = self.stackView.GetUiViewByModel(obj._model)
        if uiView:
            uiView.view.SetFocus()

    # --------- User-accessible view functions -----------

    def BroadcastMessage(self, message):
        self.RunHandler(self.stackView.uiCard.model, "OnMessage", None, message)
        for ui in self.stackView.GetAllUiViews():
            self.RunHandler(ui.model, "OnMessage", None, message)

    def GotoCard(self, cardName):
        index = None
        for m in self.stackView.stackModel.childModels:
            if m.GetProperty("name") == cardName:
                index = self.stackView.stackModel.childModels.index(m)
        if index is not None:
            self.stackView.LoadCardAtIndex(index)

    def GotoCardNumber(self, cardIndex):
        if cardIndex > 0 and cardIndex <= len(self.stackView.stackModel.childModels):
            self.stackView.LoadCardAtIndex(cardIndex-1)

    def GotoNextCard(self):
        cardIndex = self.stackView.cardIndex + 1
        if cardIndex >= len(self.stackView.stackModel.childModels): cardIndex = 0
        self.stackView.LoadCardAtIndex(cardIndex)

    def GotoPreviousCard(self):
        cardIndex = self.stackView.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackView.stackModel.childModels) - 1
        self.stackView.LoadCardAtIndex(cardIndex)

    def Wait(self, delay):
        self.stackView.RefreshNow()
        sleep(delay)

    def Time(self):
        return time()

    def Alert(self, message):
        self.stackView.RefreshNow()
        wx.MessageDialog(None, str(message), "", wx.OK).ShowModal()

    def Ask(self, message):
        self.stackView.RefreshNow()
        r = wx.MessageDialog(None, str(message), "", wx.YES_NO).ShowModal()
        return (r == wx.ID_YES)

    def PlaySound(self, filepath):
        if filepath and self.stackView.filename:
            dir = os.path.dirname(self.stackView.filename)
            filepath = os.path.join(dir, filepath)
        if filepath in self.soundCache:
            s = self.soundCache[filepath]
        else:
            s = Sound(filepath)
            self.soundCache[filepath] = s
        if s.IsOk():
            s.Play()

    def StopSound(self):
        Sound.Stop()

    def Paste(self):
        models = self.stackView.PasteViews(False)
        return [m.GetProxy() for m in models]

    def IsKeyPressed(self, name):
        return name in self.pressedKeys

    def RunAfterDelay(self, duration, func):
        timer = wx.Timer()
        def onTimer(event):
            func()
        timer.Bind(wx.EVT_TIMER, onTimer)
        timer.StartOnce(int(duration*1000))
        self.timers.append(timer)
