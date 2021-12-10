import re
import sys
import os
import traceback
import wx
import uiView
import types
from uiCard import Card
from wx.adv import Sound
from time import sleep, time
import math
from errorListWindow import CardStockError
import threading
from codeRunnerThread import CodeRunnerThread, RunOnMainSync, RunOnMainAsync
import queue
import sanitizer
from enum import Enum

try:
    import simpleaudio
    SIMPLE_AUDIO_AVAILABLE = True
except ModuleNotFoundError:
    SIMPLE_AUDIO_AVAILABLE = False


class TaskType (Enum):
    """ Types of tasks in the handlerQueue """
    Wake = 1       # Wake up the handler thread
    SetupCard = 2  # Set up for the card we just switched to
    Handler = 3    # Run an event handler
    Func = 4       # Run an arbitrary function with args and kwargs
    Code = 5       # Run an arbitrary string as code
    StopHandlingMouseEvent = 6  # Stop propagating the current mouse event


class Runner():
    """
    The Runner object runs all of the stack's user-written event handlers.  It keeps track of user variables, so that they
    can be shared between handlers, offers global variables and functions, and makes event arguments (message,
    mousePos, etc.) available to the handlers that expect them, and then restores any old values of those variables upon
    finishing those events.

    Keep the UI responsive even if an event handler runs an infinite loop.  Do this by running all handler code in the
    runnerThread.  From there, run all UI calls on the main thread, as required by wxPython.  If we need a return value
    from the main thread call, then run the call synchronously using @RunOnMainSync, and pause the runner thread until the
    main thread call returns a value.  Otherwise, just fire off the main thread call using @RunOnMainAsync and keep on
    truckin'.  In general, the stack model is modified on the runnerThread, and uiView and other UI changes are made on
    the Main thread.  This lets us consolidate many model changes made quickly, into one UI update, to avoid flickering
    the screen as the stack makes changes to multiple objects.  We try to minimize UI updates, and only display changes
    once per frame (~60Hz), and then only if something actually changed.  Exceptions are that we will update immediately
    if the stack changes to another card, or actual native views (buttons and text fields) get created or destroyed.

    When we want to stop the stack running, but a handler is still going, then we tell the thread to terminate, which
    injects a SystemExit("Return") exception into the runnerThread, so it will stop and allow us to close viewer.
    """

    def __init__(self, stackManager, viewer):
        self.stackManager = stackManager
        self.viewer = viewer
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card
        self.pressedKeys = []
        self.keyTimings = {}
        self.timers = []
        self.errors = []
        self.lastHandlerStack = []
        self.didSetup = False
        self.runnerDepth = 0
        self.numOnPeriodicsQueued = 0
        self.rewrittenHandlerMap = {}
        self.onRunFinished = None
        self.funcDefs = {}
        self.lastCard = None
        self.stopHandlingMouseEvent = False

        self.stackSetupValue = None
        self.stackReturnQueue = queue.Queue()

        # queue of tasks to run on the runnerThread
        # each task is put onto the queue as a list.
        # single item list means run SetupForCard
        # 5-item list means run a handler
        # 0-item list means just wake up to check if the thread is supposed to stop
        self.handlerQueue = queue.Queue()

        self.runnerThread = CodeRunnerThread(target=self.StartRunLoop)
        self.runnerThread.start()
        self.stopRunnerThread = False

        self.soundCache = {}

        self.stackStartTime = time()

        self.initialClientVars = {
            "Wait": self.Wait,
            "RunAfterDelay": self.RunAfterDelay,
            "Time": self.Time,
            "Distance": self.Distance,
            "Paste": self.Paste,
            "Alert": self.Alert,
            "AskYesNo": self.AskYesNo,
            "AskText": self.AskText,
            "GotoCard": self.GotoCard,
            "GotoNextCard": self.GotoNextCard,
            "GotoPreviousCard": self.GotoPreviousCard,
            "RunStack": self.RunStack,
            "PlaySound": self.PlaySound,
            "StopSound": self.StopSound,
            "BroadcastMessage": self.BroadcastMessage,
            "IsKeyPressed": self.IsKeyPressed,
            "IsMouseDown": self.IsMouseDown,
            "Quit":self.Quit,
            "stack": self.stackManager.stackModel.GetProxy(),
            "StopHandlingMouseEvent": self.StopHandlingMouseEvent,
            "ReturnFromStack": self.ReturnFromStack,
            "GetStackSetupValue": self.GetStackSetupValue,
            "MakeColor": self.MakeColor,
        }

        self.clientVars = self.initialClientVars.copy()

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

    def AddSyntaxErrors(self, analyzerSyntaxErrors):
        for path, e in analyzerSyntaxErrors.items():
            parts = path.split('.')
            modelPath = '.'.join(path.split('.')[:-1])
            model = self.stackManager.stackModel.GetModelFromPath(modelPath)
            handlerName = parts[-1]
            lineNum = e[2]
            msg = f"SyntaxError in {self.HandlerPath(model, handlerName)}, line {lineNum}: {e[0]}"
            error = CardStockError(model.GetCard(), model, handlerName, lineNum, msg)
            self.errors.append(error)

    def SetupForCard(self, cardModel):
        """
        This request comes in on the main thread, so we dispatch it to the runner thread,
        which synchronizes this with any running event handler code.
        """
        if threading.currentThread() == self.runnerThread:
            self.SetupForCardInternal(cardModel)
        else:
            self.handlerQueue.put((TaskType.SetupCard, cardModel))

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

    def IsRunningHandler(self):
        return len(self.lastHandlerStack) > 0

    def StopTimers(self):
        for t in self.timers:
            t.Stop()
        self.timers = []

    def DoReturnFromStack(self, stackReturnVal):
        self.stackReturnQueue.put(stackReturnVal)

    def CleanupFromRun(self):
        # On Main thread
        if self.runnerThread:
            self.stopRunnerThread = True
            self.StopTimers()
            for card in self.stackManager.stackModel.childModels:
                self.RunHandler(card, "OnExitStack", None)
            self.stackReturnQueue.put(None)  # Stop waiting for a RunStack() call to return
            self.handlerQueue.put((TaskType.Wake, )) # Wake up the runner thread get() call so it can see that we're stopping

            def waitAndYield(duration):
                # Wait up to duration seconds for the stack to finish running
                # run wx.YieldIfNeeded() to process main thread events while waiting, to allow @RunOnMainSync* methods to complete
                endTime = time() + duration
                while time() < endTime:
                    breakpoint = time() + 0.05
                    if len(self.lastHandlerStack) == 0:
                        break
                    while time() < breakpoint:
                        wx.YieldIfNeeded()

            waitAndYield(0.7) # wait 0.7 sec for the stack to finish
            self.runnerThread.join(0.05) # try to join the finished thread

            if self.runnerThread.is_alive():
                # Thread didn't finish.  So kill it and wait for the thread to stop
                for i in range(4):
                    # Try a few times, on the off chance that someone has a long/infinite loop in their code,
                    # inside a try block, with another long/infinite loop inside the exception handler
                    self.runnerThread.terminate()
                    waitAndYield(0.15)
                    self.runnerThread.join(0.05)
                    if not self.runnerThread.is_alive():
                        break
                if self.runnerThread.is_alive():
                    # If the runnerThread is still going now, something went wrong
                    if len(self.lastHandlerStack) > 0:
                        model = self.lastHandlerStack[-1][0]
                        handlerName = self.lastHandlerStack[-1][1]
                        msg = f"Exited while {self.HandlerPath(model, handlerName, self.lastCard)} was still running, and " \
                              f"could not be stopped.  Maybe you have a long or infinite loop?"
                        error = CardStockError(self.lastCard, model, handlerName, 1, msg)
                        self.errors.append(error)

            self.runnerThread = None

        self.StopTimers()
        self.lastHandlerStack = None
        self.lastCard = None
        self.StopSound()
        self.soundCache = None
        self.cardVarKeys = None
        self.clientVars = None
        self.timers = None
        self.rewrittenHandlerMap = None
        self.funcDefs = None
        self.handlerQueue = None
        self.stackManager = None
        if self.onRunFinished:
            self.onRunFinished(self)
        self.errors = None
        self.onRunFinished = None
        self.keyTimings = None
        self.viewer = None
        self.stackReturnQueue = None
        self.stackSetupValue = None

    def EnqueueRefresh(self):
        self.handlerQueue.put((TaskType.Wake, ))

    def EnqueueFunction(self, func, *args, **kwargs):
        """
        Add an arbitrary callable to the runner queue.
        This is used to send RunAfterDelay(), and animation onFinished functions
        from the main thread, back onto the runner thread, where we can properly
        catch errors in RunWithExceptionHandling(), to display to the user
        and avoid totally blowing up the app.
        """
        if not args: args = ()
        if not kwargs: kwargs = {}
        self.handlerQueue.put((TaskType.Func, func, args, kwargs))

    def EnqueueCode(self, code, *args, **kwargs):
        """
        Add a code string to be run on the runner queue.
        This is used to run code from the Console window in the viewer app.
        """
        self.handlerQueue.put((TaskType.Code, code))

    def StartRunLoop(self):
        """
        This is the runnerThread's run loop.  Start waiting for queued handlers, and process them until
        the runnerThread is told to stop.
        """

        # Allow a few last events to run while shutting down, to make sure we got to running any OnExitStack events
        exitCountdown = 4

        try:
            while True:
                runningOnExitStack = False
                args = self.handlerQueue.get()
                if args[0] == TaskType.Wake:
                    # This is an enqueued task meant to Refresh after running all other tasks,
                    # and also serves to wake up the runner thread for stopping.
                    if not self.stopRunnerThread:
                        self.stackManager.view.RefreshIfNeeded()
                    if self.stopRunnerThread:
                        break
                elif args[0] == TaskType.SetupCard:
                    # Run Setup for the given card
                    self.SetupForCardInternal(args[1])
                elif args[0] == TaskType.StopHandlingMouseEvent:
                    # Reset StopHandlingMouseEvent
                    self.stopHandlingMouseEvent = False
                elif args[0] == TaskType.Func:
                    # Run the given function with optional args, kwargs
                    self.RunWithExceptionHandling(func=args[1], *args[2], **args[3])
                elif args[0] == TaskType.Code:
                    # Run the given code
                    self.RunWithExceptionHandling(code=args[1])
                elif args[0] == TaskType.Handler:
                    # Run this handler
                    self.lastCard = args[1].GetCard()
                    self.RunHandlerInternal(*args[1:])
                    if args[2] == "OnExitStack":
                        runningOnExitStack = True
                    if args[2] == "OnPeriodic":
                        self.numOnPeriodicsQueued -= 1

                if self.stopRunnerThread:
                    exitCountdown -= 1
                if exitCountdown == 0 and not runningOnExitStack:
                    break

        except SystemExit:
            # The runnerThread got killed, because we told it to stop.
            if self.lastHandlerStack and len(self.lastHandlerStack) > 0:
                model = self.lastHandlerStack[-1][0]
                handlerName = self.lastHandlerStack[-1][1]
                msg = f"Exited while {self.HandlerPath(model, handlerName, self.lastCard)} was still running.  Maybe you have a long or infinite loop?"
                error = CardStockError(self.lastCard, model, handlerName, 0, msg)
                error.count = 1
                if self.errors is not None:
                    self.errors.append(error)

    def RunHandler(self, uiModel, handlerName, event, arg=None):
        """
        If we're on the main thread, that means we just got called from a UI event, so enqueue this on the runnerThread.
        If we're already on the runnerThread, that means an object's event code called another event, so run that
        immediately.
        """
        handlerStr = uiModel.handlers[handlerName].strip()
        if handlerStr == "":
            return False

        mousePos = None
        keyName = None
        if event and handlerName.startswith("OnMouse"):
            mousePos = self.stackManager.view.ScreenToClient(wx.GetMousePosition())
        elif arg and handlerName == "OnKeyHold":
            keyName = arg
        elif event and handlerName.startswith("OnKey"):
            keyName = self.KeyNameForEvent(event)
            if not keyName:
                return False

        if threading.currentThread() == self.runnerThread:
            self.RunHandlerInternal(uiModel, handlerName, handlerStr, mousePos, keyName, arg)
        else:
            if handlerName == "OnPeriodic":
                self.numOnPeriodicsQueued += 1
            self.handlerQueue.put((TaskType.Handler, uiModel, handlerName, handlerStr, mousePos, keyName, arg))
        return True

    def RunHandlerInternal(self, uiModel, handlerName, handlerStr, mousePos, keyName, arg):
        """ Run an eventHandler.  This always runs on the runnerThread. """
        if not self.didSetup:
            return

        if handlerName in ["OnMouseDown", "OnMouseMove", "OnMouseUp"] and self.stopHandlingMouseEvent:
            return

        self.runnerDepth += 1

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

        if handlerName == "OnPeriodic":
            if "elapsedTime" in self.clientVars:
                oldVars["elapsedTime"] = self.clientVars["elapsedTime"]
            else:
                oldVars["elapsedTime"] = noValue
            now = time()
            if uiModel.lastOnPeriodicTime:
                elapsedTime = now - uiModel.lastOnPeriodicTime
            else:
                elapsedTime = now - self.stackStartTime
            uiModel.lastOnPeriodicTime = now
            self.clientVars["elapsedTime"] = elapsedTime

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

        if arg and handlerName == "OnKeyHold":
            if "elapsedTime" in self.clientVars:
                oldVars["elapsedTime"] = self.clientVars["elapsedTime"]
            else:
                oldVars["elapsedTime"] = noValue
            if keyName in self.keyTimings:
                now = time()
                elapsedTime = now - self.keyTimings[keyName]
                self.keyTimings[keyName] = now
                self.clientVars["elapsedTime"] = elapsedTime
            else:
                # Shouldn't happen!  But just in case, return something that won't crash if the users divides by it
                self.clientVars["elapsedTime"] = 0.01

        if arg and handlerName == "OnBounce":
            if "otherObject" in self.clientVars:
                oldVars["otherObject"] = self.clientVars["otherObject"]
            else:
                oldVars["otherObject"] = noValue
            self.clientVars["otherObject"] = arg[0]
            if "edge" in self.clientVars:
                oldVars["edge"] = self.clientVars["edge"]
            else:
                oldVars["edge"] = noValue
            self.clientVars["edge"] = arg[1]

        # rewrite handlers that use return outside of a function, and replace with an exception that we catch, to
        # act like a return.
        handlerStr = self.RewriteHandler(handlerStr)

        self.lastHandlerStack.append((uiModel, handlerName))

        error = None
        error_class = None
        line_number = None
        errModel = None
        errHandlerName = None
        in_func = []
        detail = None

        # Use this for noticing user-definitions of new functions
        oldClientVars = self.clientVars.copy()

        try:
            exec(handlerStr, self.clientVars)
            self.ScrapeNewFuncDefs(oldClientVars, self.clientVars, uiModel, handlerName)
        except SyntaxError as err:
            self.ScrapeNewFuncDefs(oldClientVars, self.clientVars, uiModel, handlerName)
            detail = err.msg
            error_class = err.__class__.__name__
            line_number = err.lineno
            errModel = uiModel
            errHandlerName = handlerName
        except Exception as err:
            self.ScrapeNewFuncDefs(oldClientVars, self.clientVars, uiModel, handlerName)
            if err.__class__.__name__ == "RuntimeError" and err.args[0] == "Return":
                # Catch our exception-based return calls
                pass
            else:
                error_class = err.__class__.__name__
                detail = err.args[0]
                cl, exc, tb = sys.exc_info()
                trace = traceback.extract_tb(tb)
                for i in range(len(trace)):
                    if trace[i].filename == "<string>" and trace[i].name == "<module>":
                        errModel = uiModel
                        errHandlerName = handlerName
                        line_number = trace[i].lineno
                        in_func.append((handlerName, trace[i].lineno))
                    elif line_number and trace[i].filename == "<string>" and trace[i].name != "<module>":
                        if trace[i].name in self.funcDefs:
                            errModel = self.funcDefs[trace[i].name][0]
                            errHandlerName = self.funcDefs[trace[i].name][1]
                            line_number = trace[i].lineno
                        in_func.append((trace[i].name, trace[i].lineno))

        del self.lastHandlerStack[-1]

        # restore the old values from before this handler was called
        for k, v in oldVars.items():
            if v == noValue:
                if k in self.clientVars:
                    self.clientVars.pop(k)
            else:
                self.clientVars[k] = v

        if error_class and self.errors is not None:
            msg = f"{error_class} in {self.HandlerPath(errModel, errHandlerName)}, line {line_number}: {detail}"
            if len(in_func) > 1:
                frames = [f"{f[0]}():{f[1]}" for f in in_func]
                msg += f" (from {' => '.join(frames)})"

            for e in self.errors:
                if e.msg == msg:
                    error = e
                    break
            if not error:
                error = CardStockError(uiModel.GetCard(), errModel, errHandlerName, line_number, msg)
                self.errors.append(error)
            error.count += 1

            sys.stderr.write(msg + os.linesep)

        self.runnerDepth -= 1

    def RewriteHandler(self, handlerStr):
        # rewrite handlers that use return outside of a function, and replace with an exception that we catch, to
        # act like a return.
        if "return" in handlerStr:
            if handlerStr in self.rewrittenHandlerMap:
                # we cache the rewritten handlers
                return self.rewrittenHandlerMap[handlerStr]
            else:
                lines = handlerStr.split('\n')
                funcIndent = None
                updatedLines = []
                for line in lines:
                    if funcIndent is not None:
                        # if we were inside a function definition, check if it's done
                        m = re.match(rf"^(\s{{{funcIndent}}})\b", line)
                        if m:
                            funcIndent = None
                    if funcIndent is None:
                        m = re.match(r"^(\s*)def ", line)
                        if m:
                            # mark that we're inside a function def now, so don't replace returns.
                            funcIndent = len(m.group(1))
                            updatedLines.append(line)
                        else:
                            # not inside a function def, so replace returns with a RuntimeError('Return')
                            # and catch these later, while running the handler
                            u = re.sub(r"^(\s*)return\b", r"\1raise RuntimeError('Return')", line)
                            u = re.sub(r":\s+return\b", ": raise RuntimeError('Return')", u)
                            updatedLines.append(u)
                    else:
                        # now we're inside a function def, so don't replace returns.  they're valid here!
                        updatedLines.append(line)

                updated = '\n'.join(updatedLines)
                self.rewrittenHandlerMap[handlerStr] = updated  # cache the updated handler
                return updated
        else:
            # No return used, so keep the handler as-is
            return handlerStr

    def RunWithExceptionHandling(self, code=None, func=None, *args, **kwargs):
        """ Run a function with exception handling.  This always runs on the runnerThread. """
        error = None
        error_class = None
        line_number = None
        errModel = None
        errHandlerName = None
        in_func = []
        detail = None

        uiModel = None
        oldCard = None
        oldSelf = None
        funcName = None
        if func:
            funcName = func.__name__
            if funcName in self.funcDefs:
                uiModel = self.funcDefs[funcName][0]
                if self.lastCard != uiModel.GetCard():
                    self.oldCard = self.lastCard
                    self.SetupForCard(uiModel.GetCard())
                if "self" in self.clientVars:
                    oldSelf = self.clientVars["self"]
                self.clientVars["self"] = uiModel.GetProxy()

        try:
            if func:
                func(*args, **kwargs)
            elif code:
                try:
                    result = eval(code, self.clientVars)
                    if result is not None:
                        print(result)
                except SyntaxError:
                    exec(code, self.clientVars)
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            trace = traceback.extract_tb(tb)
            if func:
                for i in range(len(trace)):
                    if trace[i].filename == "<string>" and trace[i].name != "<module>":
                        if trace[i].name in self.funcDefs:
                            errModel = self.funcDefs[trace[i].name][0]
                            errHandlerName = self.funcDefs[trace[i].name][1]
                            line_number = trace[i].lineno
                        in_func.append((trace[i].name, trace[i].lineno))
            elif code:
                print(f"{error_class}: {detail}", file=sys.stderr)

        if error_class and errModel and self.errors is not None:
            msg = f"{error_class} in {self.HandlerPath(errModel, errHandlerName)}, line {line_number}: {detail}"
            if len(in_func) > 1:
                frames = [f"{f[0]}():{f[1]}" for f in in_func]
                msg += f" (from {' => '.join(frames)})"

            for e in self.errors:
                if e.msg == msg:
                    error = e
                    break
            if not error:
                error = CardStockError(errModel.GetCard() if errModel else None,
                                       errModel, errHandlerName, line_number, msg)
                self.errors.append(error)
            error.count += 1

            sys.stderr.write(msg + os.linesep)

        if oldCard:
            self.SetupForCard(oldCard)
        if oldSelf:
            self.clientVars["self"] = oldSelf
        else:
            if "self" in self.clientVars:
                self.clientVars.pop("self")

    def ScrapeNewFuncDefs(self, oldVars, newVars, model, handlerName):
        # Keep track of where each user function has been defined, so we can send you to the right handler's code in
        # the Designer when the user clicks on an error in the ErrorList.
        for (k, v) in newVars.items():
            if isinstance(v, types.FunctionType) and (k not in oldVars or oldVars[k] != v):
                self.funcDefs[k] = (model, handlerName)

    def HandlerPath(self, model, handlerName, card=None):
        if model.type == "card":
            return f"{model.GetProperty('name')}.{handlerName}()"
        else:
            if card == None:
                card = model.GetCard()
            return f"{model.GetProperty('name')}.{handlerName}() on card '{card.GetProperty('name')}'"

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
            self.keyTimings[keyName] = time()
            return True
        return False

    def OnKeyUp(self, event):
        keyName = self.KeyNameForEvent(event)
        if keyName and keyName in self.pressedKeys:
            self.pressedKeys.remove(keyName)
            del self.keyTimings[keyName]

    def ClearPressedKeys(self):
        self.pressedKeys = []
        self.keyTimings = {}

    @RunOnMainAsync
    def SetFocus(self, obj):
        uiView = self.stackManager.GetUiViewByModel(obj._model)
        if uiView:
            if uiView.model.type == "textfield":
                sel = uiView.view.GetSelection()
            uiView.view.SetFocus()
            if uiView.model.type == "textfield":
                uiView.view.SetSelection(sel[0], sel[1])


    # --------- User-accessible view functions -----------

    def BroadcastMessage(self, message):
        if not isinstance(message, str):
            raise TypeError("message must be a string")

        self.RunHandler(self.stackManager.uiCard.model, "OnMessage", None, message)
        for ui in self.stackManager.uiCard.GetAllUiViews():
            self.RunHandler(ui.model, "OnMessage", None, message)

    def GotoCard(self, card):
        index = None
        if isinstance(card, str):
            cardName = card
        elif isinstance(card, Card):
            cardName = card._model.GetProperty("name")
        elif isinstance(card, int):
            index = card-1
        else:
            raise TypeError("card must be card object, a string, or an int")

        if index is None:
            for m in self.stackManager.stackModel.childModels:
                if m.GetProperty("name") == cardName:
                    index = self.stackManager.stackModel.childModels.index(m)
        if index is not None:
            if index < 0 or index >= len(self.stackManager.stackModel.childModels):
                # Modify index back to 1 based for user visible error message
                raise ValueError(f'card number {index + 1} does not exist')
            self.stackManager.LoadCardAtIndex(index)
        else:
            raise ValueError("cardName '" + cardName + "' does not exist")

    def GotoNextCard(self):
        cardIndex = self.stackManager.cardIndex + 1
        if cardIndex >= len(self.stackManager.stackModel.childModels): cardIndex = 0
        self.stackManager.LoadCardAtIndex(cardIndex)

    def GotoPreviousCard(self):
        cardIndex = self.stackManager.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackManager.stackModel.childModels) - 1
        self.stackManager.LoadCardAtIndex(cardIndex)

    def RunStack(self, filename, cardNumber=1, setupValue=None):
        if self.stopRunnerThread:
            return None
        success = self.viewer.GosubStack(filename, cardNumber-1, sanitizer.SanitizeValue(setupValue, []))
        if success:
            result = self.stackReturnQueue.get()
            if not self.stopRunnerThread:
                return result
            else:
                raise RuntimeError("Return")
        else:
            raise RuntimeError(f"Couldn't find stack '{filename}'.")

    def ReturnFromStack(self, result=None):
        stackReturnValue = sanitizer.SanitizeValue(result, [])
        if self.viewer.GosubStack(None,-1, stackReturnValue):
            raise RuntimeError('Return')

    def GetStackSetupValue(self):
        return self.stackSetupValue

    def Wait(self, delay):
        try:
            delay = float(delay)
        except ValueError:
            raise TypeError("delay must be a number")

        endTime = time() + delay
        while time() < endTime:
            remaining = endTime - time()
            if self.stopRunnerThread:
                break
            sleep(min(remaining, 0.25))

    def Time(self):
        return time()

    def Distance(self, pointA, pointB):
        try:
            pointA = wx.RealPoint(pointA[0], pointA[1])
        except:
            raise ValueError("pointA must be a point or a list of two numbers")
        try:
            pointB = wx.RealPoint(pointB[0], pointB[1])
        except:
            raise ValueError("pointB must be a point or a list of two numbers")
        return math.sqrt((pointB[0] - pointA[0]) ** 2 + (pointB[1] - pointA[1]) ** 2)

    def Alert(self, message):
        if self.stopRunnerThread:
            return

        @RunOnMainSync
        def func():
            wx.MessageDialog(None, str(message), "", wx.OK).ShowModal()
        func()

    def AskYesNo(self, message):
        if self.stopRunnerThread:
            return None

        @RunOnMainSync
        def func():
            return wx.MessageDialog(None, str(message), "", wx.YES_NO).ShowModal() == wx.ID_YES

        return func()

    def AskText(self, message, defaultResponse=None):
        if self.stopRunnerThread:
            return None

        @RunOnMainSync
        def func():
            dlg = wx.TextEntryDialog(None, str(message), '')
            if defaultResponse is not None:
                dlg.SetValue(str(defaultResponse))
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
            return None

        return func()

    def PlaySound(self, filepath):
        if not isinstance(filepath, str):
            raise TypeError("filepath must be a string")

        if self.stopRunnerThread:
            return

        filepath = self.stackManager.resPathMan.GetAbsPath(filepath)

        if not os.path.exists(filepath):
            raise ValueError("No readable audio file at '" + filepath + "'")

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
            Sound.Stop()

    @RunOnMainSync
    def Paste(self):
        models = self.stackManager.Paste(False)
        for model in models:
            model.RunSetup(self)
        return [m.GetProxy() for m in models]

    def IsKeyPressed(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        return name in self.pressedKeys

    @RunOnMainSync
    def IsMouseDown(self):
        return wx.GetMouseState().LeftIsDown()

    def MakeColor(self, r, g, b):
        if not isinstance(r, (float, int)) or not 0 <= r <= 1:
            raise TypeError("r must be a number between 0 and 1")
        if not isinstance(g, (float, int)) or not 0 <= g <= 1:
            raise TypeError("g must be a number between 0 and 1")
        if not isinstance(b, (float, int)) or not 0 <= b <= 1:
            raise TypeError("b must be a number between 0 and 1")
        r, g, b = (int(r * 255), int(g * 255), int(b * 255))
        return f"#{r:02X}{g:02X}{b:02X}"

    def RunAfterDelay(self, duration, func, *args, **kwargs):
        try:
            duration = float(duration)
        except ValueError:
            raise TypeError("duration must be a number")

        startTime = time()

        @RunOnMainAsync
        def f():
            if self.stopRunnerThread: return

            adjustedDuration = duration + startTime - time()
            if adjustedDuration > 0.010:
                timer = wx.Timer()
                def onTimer(event):
                    if self.stopRunnerThread: return
                    self.EnqueueFunction(func, *args, **kwargs)
                timer.Bind(wx.EVT_TIMER, onTimer)
                timer.StartOnce(int(adjustedDuration*1000))
                self.timers.append(timer)
            else:
                self.EnqueueFunction(func, *args, **kwargs)

        f()

    @RunOnMainAsync
    def Quit(self):
        if self.stopRunnerThread: return
        self.stackManager.view.TopLevelParent.OnMenuClose(None)

    def ResetStopHandlingMouseEvent(self):
        self.handlerQueue.put((TaskType.StopHandlingMouseEvent, ))

    def StopHandlingMouseEvent(self):
        self.stopHandlingMouseEvent = True

    def DidStopHandlingMouseEvent(self):
        return self.stopHandlingMouseEvent
