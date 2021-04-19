import sys
import os
import traceback
import wx
import uiView
from uiCard import Card
from wx.adv import Sound
from time import sleep, time
from errorListWindow import CardStockError
import threading
from killableThread import KillableThread, RunOnMain
import queue

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

    Keep the UI responsive even if an event handler runs an infinite loop.  Do this by running all handler code in the
    runnerThread.  From there, run all UI calls synchronously on the main thread, as required by wxPython.
    """

    def __init__(self, stackManager, sb=None):
        self.stackManager = stackManager
        self.statusBar = sb
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card
        self.pressedKeys = []
        self.timers = []
        self.errors = []
        self.lastHandlerStack = []
        self.didSetup = False
        self.runnerDepth = 0
        self.missedIdleCount = 0
        self.numOnIdlesQueued = 0

        # queue of tasks to run on the runnerThread
        # each task is put onto the queue as a list.
        # single item list means run SetupForCard
        # 5-item list means run a handler
        # 0-item list means just wake up to check if the thread is supposed to stop
        self.handlerQueue = queue.Queue()

        self.runnerThread = KillableThread(target=self.StartRunLoop)
        self.runnerThread.start()
        self.stopRunnerThread = False

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
            "SoundPlay": self.SoundPlay,
            "SoundStop": self.SoundStop,
            "BroadcastMessage": self.BroadcastMessage,
            "IsKeyPressed": self.IsKeyPressed,
            "IsMouseDown": self.IsMouseDown,
            "Quit":self.Quit,
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
            wx.WXK_CONTROL: "Control",
            wx.WXK_BACK: "Backspace",
            wx.WXK_CAPITAL: "CapsLock"
        }
        if wx.GetOsVersion()[0] == wx.OS_MAC_OSX_DARWIN:
            self.keyCodeStringMap[wx.WXK_ALT] = "Option"
            self.keyCodeStringMap[wx.WXK_CONTROL] = "Command"
            self.keyCodeStringMap[wx.WXK_RAW_CONTROL] = "Control"

    def SetupForCard(self, cardModel):
        if threading.currentThread() == self.runnerThread:
            self.SetupForCardInternal(cardModel)
        else:
            self.handlerQueue.put((cardModel,))

    def SetupForCardInternal(self, cardModel):
        """
        Setup clientVars with the current card's view names as variables.
        This always runs on the runnerThread.
        """
        self.clientVars["card"] = cardModel.GetProxy()
        for k in self.cardVarKeys.copy():
            if k in self.clientVars:
                self.clientVars.pop(k)
            self.cardVarKeys.remove(k)
        for m in cardModel.GetAllChildModels():
            name = m.GetProperty("name")
            self.clientVars[name] = m.GetProxy()
            self.cardVarKeys.append(name)
        self.didSetup = True

    def ApplyPendingUpdatesIfBusy(self):
        """
        Keep track of whether we're still running the previous OnIdle.  If so, ApplyAllPending now.
        """
        if self.missedIdleCount > 1:
            self.stackManager.uiCard.model.ApplyAllPending()
        self.missedIdleCount += 1

    def EnqueueApplyPendingUpdates(self):
        """
        Add a task into the queue to apply pending model updates after the queue finishes running.
        """
        self.handlerQueue.put([])

    def CleanupFromRun(self):
        # On Main thread
        print("Start Cleanup", time())
        if self.runnerThread:
            self.stopRunnerThread = True
            for t in self.timers:
                t.Stop()
            self.timers = []
            self.SoundStop()
            self.soundCache = {}
            self.handlerQueue.put([]) # Wake up the runner thread get() call

            # Wait up to 1.0 sec for the stack to finish
            # run wx.Yield() to process main thread events while waiting, to allow @RunOnMain methods to complete
            endTime = time() + 1.0
            while time() < endTime:
                self.runnerThread.hasRunOnMain = False
                breakpoint = time() + 0.05
                while time() < breakpoint:
                    wx.YieldIfNeeded()
                if not self.runnerThread.hasRunOnMain:
                    break
            self.runnerThread.join(max(endTime - time(), 0.01))

            if self.runnerThread.is_alive():
                self.runnerThread.terminate()
                self.runnerThread.join(0.01)
            self.runnerThread = None
        self.lastHandlerStack = []

    def StartRunLoop(self):
        """
        This is the runnerThread's run loop.  Start waiting for queued handlers, and process them until
        the runnerThread is told to stop.
        """
        try:
            while True:
                args = self.handlerQueue.get()
                if len(args) == 0:
                    # This is an enqueued task meant to ApplyAllPending() after running all other tasks,
                    # and also serves to wake up the runner thread for stopping.
                    if not self.stopRunnerThread:
                        self.stackManager.uiCard.model.ApplyAllPending()
                        self.missedIdleCount = 0
                elif len(args) == 1:
                    self.SetupForCardInternal(*args)
                elif len(args) == 6:
                    self.RunHandlerInternal(*args)
                    if args[1] == "OnIdle":
                        self.numOnIdlesQueued -= 1

                if self.stopRunnerThread:
                    break

        except SystemExit:
            # The killableThread got killed, because we told it to stop.
            if len(self.lastHandlerStack):
                model = self.lastHandlerStack[-1][0]
                handlerName = self.lastHandlerStack[-1][1]
                msg = f"Exited while {self.HandlerPath(model, handlerName)} was still running.  Maybe you have a long or infinite loop?"
                error = CardStockError(model.GetCard(), model, handlerName, 0, msg)
                error.count = 1
                self.errors.append(error)
            else:
                error = CardStockError(None, None, None, 0,
                                       "Exited while code was still running.  Maybe you have a long or infinite loop?")
                error.count = 1
                self.errors.append(error)

    def RunHandler(self, uiModel, handlerName, event, arg=None):
        """
        If we're on the main thread, that means we just got called from a UI event, so enqueue this on the runnerThread.
        If we're already on the runnerThread, that means an object's event code called another event, so run that
        immediately.
        """
        handlerStr = uiModel.handlers[handlerName].strip()
        if handlerStr == "":
            return

        mousePos = None
        keyName = None
        if event and handlerName.startswith("OnMouse"):
            mousePos = self.stackManager.view.ScreenToClient(wx.GetMousePosition())
        if event and handlerName.startswith("OnKey"):
            keyName = self.KeyNameForEvent(event)
            if not keyName:
                return

        if threading.currentThread() == self.runnerThread:
            self.RunHandlerInternal(uiModel, handlerName, handlerStr, mousePos, keyName, arg)
        else:
            if handlerName == "OnIdle":
                self.numOnIdlesQueued += 1
            self.handlerQueue.put((uiModel, handlerName, handlerStr, mousePos, keyName, arg))

    def RunHandlerInternal(self, uiModel, handlerName, handlerStr, mousePos, keyName, arg):
        """ Run an eventHandler.  This always runs on the runnerThread. """
        if not self.didSetup:
            return

        self.runnerDepth += 1
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

        if mousePos and handlerName.startswith("OnMouse"):
            if "mousePos" in self.clientVars:
                oldVars["mousePos"] = self.clientVars["mousePos"]
            else:
                oldVars["mousePos"] = noValue
            self.clientVars["mousePos"] = mousePos

        if keyName and handlerName.startswith("OnKey"):
            if "keyName" in self.clientVars:
                oldVars["keyName"] = self.clientVars["keyName"]
            else:
                oldVars["keyName"] = noValue
            self.clientVars["keyName"] = keyName

        self.lastHandlerStack.append((uiModel, handlerName))

        error = None
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

        del self.lastHandlerStack[-1]

        # restore the old values from before this handler was called
        for k, v in oldVars.items():
            if v == noValue:
                if k in self.clientVars:
                    self.clientVars.pop(k)
            else:
                self.clientVars[k] = v

        if error_class:
            msg = f"{error_class} in {self.HandlerPath(uiModel, handlerName)}, line {line_number}: {detail}"

            for e in self.errors:
                if e.msg == msg:
                    error = e
                    break
            if not error:
                error = CardStockError(uiModel.GetCard(), uiModel, handlerName, line_number, msg)
                self.errors.append(error)
            error.count += 1

            sys.stderr.write(msg + os.linesep)

            if self.statusBar:
                self.statusBar.SetStatusText(msg)

        self.runnerDepth -= 1
        # Changes from OnIdle handlers get applied after all of them run, by EnqueueApplyPendingUpdates
        if self.runnerDepth == 0 and handlerName != "OnIdle":
            self.stackManager.stackModel.ApplyAllPending()

    def HandlerPath(self, model, handlerName):
        if model.type == "card":
            return f"{model.GetProperty('name')}.{handlerName}()"
        else:
            return f"{model.GetProperty('name')}.{handlerName}() on card '{model.GetCard().GetProperty('name')}'"

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

    @RunOnMain
    def GotoCard(self, card):
        if isinstance(card, str):
            cardName = card
        elif isinstance(card, Card):
            cardName = card._model.GetProperty("name")
        else:
            raise TypeError("card must be card object or a string")

        index = None
        for m in self.stackManager.stackModel.childModels:
            if m.GetProperty("name") == cardName:
                index = self.stackManager.stackModel.childModels.index(m)
        if index is not None:
            self.stackManager.LoadCardAtIndex(index)
        else:
            raise ValueError("cardName '" + cardName + "' does not exist")

    @RunOnMain
    def GotoCardIndex(self, cardIndex):
        if not isinstance(cardIndex, int):
            raise TypeError("cardIndex must be an int")

        if cardIndex >= 0 and cardIndex <= len(self.stackManager.stackModel.childModels)-1:
            self.stackManager.LoadCardAtIndex(cardIndex)
        else:
            raise TypeError("cardIndex " + str(cardIndex) + " is out of range")

    @RunOnMain
    def GotoNextCard(self):
        cardIndex = self.stackManager.cardIndex + 1
        if cardIndex >= len(self.stackManager.stackModel.childModels): cardIndex = 0
        self.stackManager.LoadCardAtIndex(cardIndex)

    @RunOnMain
    def GotoPreviousCard(self):
        cardIndex = self.stackManager.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackManager.stackModel.childModels) - 1
        self.stackManager.LoadCardAtIndex(cardIndex)

    def Wait(self, delay):
        try:
            delay = float(delay)
        except ValueError:
            raise TypeError("delay must be a number")

        self.stackManager.uiCard.model.ApplyAllPending()
        sleep(delay)

    def Time(self):
        return time()

    @RunOnMain
    def Alert(self, message):
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        self.stackManager.uiCard.model.ApplyAllPending()
        wx.MessageDialog(None, str(message), "", wx.OK).ShowModal()

    @RunOnMain
    def Ask(self, message):
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        self.stackManager.uiCard.model.ApplyAllPending()
        r = wx.MessageDialog(None, str(message), "", wx.YES_NO).ShowModal()
        return (r == wx.ID_YES)

    def SoundPlay(self, filepath):
        if not isinstance(filepath, str):
            raise TypeError("filepath must be a string")

        filepath = self.stackManager.resPathMan.GetAbsPath(filepath)

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

    def SoundStop(self):
        if SIMPLE_AUDIO_AVAILABLE:
            simpleaudio.stop_all()
        else:
            for (filepath, s) in self.soundCache.items():
                s.Stop()

    @RunOnMain
    def Paste(self):
        models = self.stackManager.Paste(False)
        for model in models:
            # Hide now and defer an unHide, so the handler code can modify the clone before it displays
            model.SetProperty("hidden", True, notify=False, noDeferred=True)
            model.SetProperty("hidden", False)
            model.RunSetup(self)
        return [m.GetProxy() for m in models]

    def IsKeyPressed(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        return name in self.pressedKeys

    @RunOnMain
    def IsMouseDown(self):
        return wx.GetMouseState().LeftIsDown()

    @RunOnMain
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

    @RunOnMain
    def Quit(self):
        self.stackManager.stackModel.ApplyAllPending()
        self.stackManager.view.TopLevelParent.OnMenuClose(None)
