import sys
import os
import traceback
import wx
from wx.adv import Sound
from time import sleep, time

try:
    import simpleaudio
    SIMPLE_AUDIO_AVAILABLE = True
except ModuleNotFoundError:
    SIMPLE_AUDIO_AVAILABLE = False

if wx.Platform == '__WXMAC__':
    SIMPLE_AUDIO_AVAILABLE = False


class Runner():
    """
    The Runner object runs all of the stack's user-written event handlers.  It keeps track of user variables, so that they
    can be shared between handlers, offers global variables and functions, and makes event arguments (message,
    mousePos, etc.) available to the handlers that expect them, and then restores any old values of those variables upon
    finishing those events.
    """

    def __init__(self, stackManager, sb=None):
        self.stackManager = stackManager
        self.statusBar = sb
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card
        self.pressedKeys = []
        self.timers = []

        self.soundCache = {}

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
            "GotoCardIndex": self.GotoCardIndex,
            "PlaySound": self.PlaySound,
            "StopSound": self.StopSound,
            "BroadcastMessage": self.BroadcastMessage,
            "IsKeyPressed": self.IsKeyPressed,
            "IsMouseDown": self.IsMouseDown,
            "stack": self.stackManager.stackModel.GetProxy(),
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

    def SetupForCard(self, cardModel):
        # Setup clientVars with the current card's view names as variables
        self.clientVars["card"] = cardModel.GetProxy()
        for k in self.cardVarKeys.copy():
            self.clientVars.pop(k)
            self.cardVarKeys.remove(k)
        for m in cardModel.GetAllChildModels():
            name = m.GetProperty("name")
            self.clientVars[name] = m.GetProxy()
            self.cardVarKeys.append(name)

    def CleanupFromRun(self):
        for t in self.timers:
            t.Stop()
        self.timers = []
        self.StopSound()
        self.soundCache = {}

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
            mousePos = self.stackManager.view.ScreenToClient(wx.GetMousePosition())
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

    def SetFocus(self, obj):
        uiView = self.stackManager.GetUiViewByModel(obj._model)
        if uiView:
            uiView.view.SetFocus()

    # --------- User-accessible view functions -----------

    def BroadcastMessage(self, message):
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        self.RunHandler(self.stackManager.uiCard.model, "OnMessage", None, message)
        for ui in self.stackManager.GetAllUiViews():
            self.RunHandler(ui.model, "OnMessage", None, message)

    def GotoCard(self, cardName):
        if not isinstance(cardName, str):
            raise TypeError("cardName must be a string")

        index = None
        for m in self.stackManager.stackModel.childModels:
            if m.GetProperty("name") == cardName:
                index = self.stackManager.stackModel.childModels.index(m)
        if index is not None:
            self.stackManager.LoadCardAtIndex(index)
        else:
            raise ValueError("cardName '" + cardName + "' does not exist")

    def GotoCardIndex(self, cardIndex):
        if not isinstance(cardIndex, int):
            raise TypeError("cardIndex must be an int")

        if cardIndex >= 0 and cardIndex <= len(self.stackManager.stackModel.childModels)-1:
            self.stackManager.LoadCardAtIndex(cardIndex)
        else:
            raise TypeError("cardIndex " + str(cardIndex) + " is out of range")


    def GotoNextCard(self):
        cardIndex = self.stackManager.cardIndex + 1
        if cardIndex >= len(self.stackManager.stackModel.childModels): cardIndex = 0
        self.stackManager.LoadCardAtIndex(cardIndex)

    def GotoPreviousCard(self):
        cardIndex = self.stackManager.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackManager.stackModel.childModels) - 1
        self.stackManager.LoadCardAtIndex(cardIndex)

    def Wait(self, delay):
        try:
            delay = float(delay)
        except ValueError:
            raise TypeError("delay must be a number")

        self.stackManager.RefreshNow()
        sleep(delay)

    def Time(self):
        return time()

    def Alert(self, message):
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        self.stackManager.RefreshNow()
        wx.MessageDialog(None, str(message), "", wx.OK).ShowModal()

    def Ask(self, message):
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        self.stackManager.RefreshNow()
        r = wx.MessageDialog(None, str(message), "", wx.YES_NO).ShowModal()
        return (r == wx.ID_YES)

    def PlaySound(self, filepath):
        if not isinstance(filepath, str):
            raise TypeError("filepath must be a string")

        if filepath and self.stackManager.filename:
            dir = os.path.dirname(self.stackManager.filename)
            filepath = os.path.join(dir, filepath)
        if filepath in self.soundCache:
            s = self.soundCache[filepath]
        else:
            if SIMPLE_AUDIO_AVAILABLE:
                s = simpleaudio.WaveObject.from_wave_file(filepath)
            else:
                s = Sound(filepath)
                if not s.IsOk():
                    s = None
            if s:
                self.soundCache[filepath] = s
            else:
                raise ValueError("No readable audio file at '" + filepath + "'")

        if s:
            if SIMPLE_AUDIO_AVAILABLE:
                s.play()
            else:
                s.Play()

    def StopSound(self):
        if SIMPLE_AUDIO_AVAILABLE:
            simpleaudio.stop_all()
        else:
            for (filepath, s) in self.soundCache.items():
                s.Stop()

    def Paste(self):
        models = self.stackManager.Paste(False)
        return [m.GetProxy() for m in models]

    def IsKeyPressed(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        return name in self.pressedKeys

    def IsMouseDown(self):
        return wx.GetMouseState().LeftIsDown()

    def RunAfterDelay(self, duration, func, *args, **kwargs):
        try:
            duration = float(duration)
        except ValueError:
            raise TypeError("duration must be a number")

        timer = wx.Timer()
        def onTimer(event):
            func(*args, **kwargs)
        timer.Bind(wx.EVT_TIMER, onTimer)
        timer.StartOnce(int(duration*1000))
        self.timers.append(timer)
