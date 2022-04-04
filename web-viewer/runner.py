import re
import sys
from browser import self as worker
import traceback
import wx_compat as wx
import models
import types
import math

def time():
    return worker.Date.now() / 1000.0


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

    def __init__(self, stackManager):
        self.stackManager = stackManager
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card
        self.lastMousePos = wx.Point(0,0)
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
        self.shouldUpdateVars = False

        self.stackSetupValue = None

        self.stopRunnerThread = False

        self.soundCache = {}

        self.stackStartTime = None

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
            "GetMousePos": self.GetMousePos,
            "Quit":self.Quit,
            "Color": self.MakeColor,
            "Point": self.MakePoint,
            "Size": self.MakeSize,
        }

        self.clientVars = None

        self.keyCodeStringMap = {
            " ": "Space",
            "ArrowLeft": "Left",
            "ArrowRight": "Right",
            "ArrowUp": "Up",
            "ArrowDown": "Down",
            "Enter": "Return"
        }

    def SetDown(self):
        self.stackManager = None
        self.cardVarKeys = None
        self.lastMousePos = None
        self.pressedKeys = None
        self.keyTimings = None
        self.StopTimers()
        self.errors = None
        self.lastHandlerStack = None
        self.didSetup = False
        self.runnerDepth = 0
        self.numOnPeriodicsQueued = 0
        self.rewrittenHandlerMap = None
        self.onRunFinished = None
        self.funcDefs = None
        self.lastCard = None
        self.stopHandlingMouseEvent = False
        self.shouldUpdateVars = False
        self.stackSetupValue = None
        self.stopRunnerThread = False
        self.soundCache = None
        self.stackStartTime = None
        self.clientVars = None

    def StartStack(self):
        self.stackStartTime = time()
        self.clientVars = self.initialClientVars.copy()
        self.cardVarKeys = []
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
        self.shouldUpdateVars = False

    def SetupForCard(self, cardModel):
        """
        Setup clientVars with the current card's view names as variables.
        This always runs on the runnerThread.
        """
        self.clientVars["card"] = cardModel.GetProxy()
        self.clientVars["stack"] = cardModel.parent.GetProxy()
        for k in self.cardVarKeys.copy():
            if k in self.clientVars:
                self.clientVars.pop(k)
            self.cardVarKeys.remove(k)
        for m in cardModel.GetAllChildModels():
            name = m.GetProperty("name")
            self.clientVars[name] = m.GetProxy()
            self.cardVarKeys.append(name)
        self.didSetup = True

    def StopTimers(self):
        for t in self.timers:
            worker.clearTimeout(t)
        self.timers = []

    def DoReturnFromStack(self, stackReturnVal):
        pass
        # self.stackReturnQueue.put(stackReturnVal)

    def RunHandler(self, uiModel, handlerName, eventVal, arg=None):
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
        if eventVal and handlerName.startswith("OnMouse"):
            mousePos = eventVal
        elif arg and handlerName == "OnKeyHold":
            keyName = arg
        elif eventVal and handlerName.startswith("OnKey"):
            keyName = self.KeyNameForCode(eventVal)
            if not keyName:
                return False

        self.RunHandlerInternal(uiModel, handlerName, handlerStr, mousePos, keyName, arg)
        worker.stackWorker.SendAsync(("render",))
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

        if arg and handlerName == "OnDoneLoading":
            if "URL" in self.clientVars:
                oldVars["URL"] = self.clientVars["URL"]
            else:
                oldVars["URL"] = noValue
            self.clientVars["URL"] = arg[0]
            if "didLoad" in self.clientVars:
                oldVars["didLoad"] = self.clientVars["didLoad"]
            else:
                oldVars["didLoad"] = noValue
            self.clientVars["didLoad"] = arg[1]

        if handlerName == "OnCardStockLink":
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
            print(f"{error_class}: {detail} in {errModel.properties['name']}:{errHandlerName}:{line_number}\n{handlerStr}", file=sys.stderr)
        except Exception as err:
            if err.__class__.__name__ == "RuntimeError" and err.args[0] == "Return":
                # Catch our exception-based return calls
                pass
            else:
                self.ScrapeNewFuncDefs(oldClientVars, self.clientVars, uiModel, handlerName)
                error_class = err.__class__.__name__
                detail = err.args[0]
                errHandlerName = ""
                line_number = None
                errModel = None
                cl, exc, tb = sys.exc_info()
                trace = traceback.extract_tb(tb)
                for i in range(len(trace)):
                    if trace[i].filename == "<string>" and trace[i].name == "<module>":
                        errModel = uiModel
                        if errModel.clonedFrom: errModel = errModel.clonedFrom
                        errHandlerName = handlerName
                        line_number = trace[i].lineno
                    elif line_number and trace[i].filename == "<string>" and trace[i].name != "<module>":
                        if trace[i].name in self.funcDefs:
                            errModel = self.funcDefs[trace[i].name][0]
                            if errModel.clonedFrom: errModel = errModel.clonedFrom
                            errHandlerName = self.funcDefs[trace[i].name][1]
                            line_number = trace[i].lineno
                if errModel:
                    print(f"{error_class}: {detail} in {errModel.properties['name']}:{errHandlerName}:{line_number}\n{handlerStr}", file=sys.stderr)
                else:
                    print(f"{error_class}: {detail}:{errHandlerName}:{line_number}\n{handlerStr}", file=sys.stderr)

        del self.lastHandlerStack[-1]

        # restore the old values from before this handler was called
        for k, v in oldVars.items():
            if v == noValue:
                if k in self.clientVars:
                    self.clientVars.pop(k)
            else:
                self.clientVars[k] = v

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

    def EnqueueFunction(self, func=None, *args, **kwargs):
        self.RunWithExceptionHandling(func, *args, **kwargs)

    def RunWithExceptionHandling(self, func=None, *args, **kwargs):
        """ Run a function with exception handling.  This always runs on the runnerThread. """
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
        except Exception as err:
            if err.__class__.__name__ == "RuntimeError" and err.args[0] == "Return":
                # Catch our exception-based return calls
                pass
            else:
                error_class = err.__class__.__name__
                detail = err.args[0]
                print(f"{error_class}: {detail} in:\n{funcName}", file=sys.stderr)

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

    def GetUserClientVars(self, clientVars):
        vars = {}
        for k,v in clientVars.items():
            if k not in self.initialClientVars:
                vars[k] = v
        return vars

    def HandlerPath(self, model, handlerName, card=None):
        if model.type == "card":
            return f"{model.GetProperty('name')}.{handlerName}()"
        else:
            if card is None:
                card = model.GetCard()
            return f"{model.GetProperty('name')}.{handlerName}() on card '{card.GetProperty('name')}'"

    def KeyNameForCode(self, code):
        if code in self.keyCodeStringMap:
            return self.keyCodeStringMap[code]
        elif len(code) == 1:
            code = code.upper()
        return code

    def OnKeyDown(self, code):
        keyName = self.KeyNameForCode(code)
        if keyName and keyName not in self.pressedKeys:
            self.pressedKeys.append(keyName)
            self.keyTimings[keyName] = time()
            return True
        return False

    def OnKeyUp(self, code):
        keyName = self.KeyNameForCode(code)
        if keyName and keyName in self.pressedKeys:
            self.pressedKeys.remove(keyName)
            del self.keyTimings[keyName]

    def ClearPressedKeys(self):
        self.pressedKeys = []
        self.keyTimings = {}

    def UpdateClientVar(self, k, v):
        if k in self.clientVars:
            self.clientVars[k] = v

    def SetFocus(self, obj):
        uiView = self.stackManager.GetUiViewByModel(obj._model)
        if uiView and uiView.model.type == "textfield":
            worker.stackWorker.SendAsync(("focus", uiView.textbox))


    # --------- User-accessible view functions -----------

    def BroadcastMessage(self, message):
        if not isinstance(message, str):
            raise TypeError("BroadcastMessage(): message must be a string")

        self.RunHandler(self.stackManager.uiCard.model, "OnMessage", None, message)
        for ui in self.stackManager.uiCard.GetAllUiViews():
            self.RunHandler(ui.model, "OnMessage", None, message)

    def GotoCard(self, card):
        index = None
        if isinstance(card, str):
            cardName = card
        elif isinstance(card, models.Card):
            cardName = card._model.GetProperty("name")
        elif isinstance(card, int):
            index = card-1
        else:
            raise TypeError("GotoCard(): card must be card object, a string, or an int")

        if index is None:
            for m in self.stackManager.stackModel.childModels:
                if m.GetProperty("name") == cardName:
                    index = self.stackManager.stackModel.childModels.index(m)
        if index is not None:
            if index < 0 or index >= len(self.stackManager.stackModel.childModels):
                # Modify index back to 1 based for user visible error message
                raise ValueError(f'GotoCard(): card number {index + 1} does not exist')
            self.stackManager.LoadCardAtIndex(index)
        else:
            raise ValueError("GotoCard(): cardName '" + cardName + "' does not exist")

    def GotoNextCard(self):
        cardIndex = self.stackManager.cardIndex + 1
        if cardIndex >= len(self.stackManager.stackModel.childModels): cardIndex = 0
        self.stackManager.LoadCardAtIndex(cardIndex)

    def GotoPreviousCard(self):
        cardIndex = self.stackManager.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackManager.stackModel.childModels) - 1
        self.stackManager.LoadCardAtIndex(cardIndex)

    def RunStack(self, filename, cardNumber=1, setupValue=None):
        print("RunStack(): unsupported on web")

    def ReturnFromStack(self, result=None):
        print("ReturnFromStack(): unsupported on web")

    def GetStackSetupValue(self):
        print("GetStackSetupValue(): unsupported on web")
        return None

    def Wait(self, delay):
        try:
            delay = float(delay)
        except ValueError:
            raise TypeError("Wait(): delay must be a number")

        worker.stackWorker.SendAsync(("render",))
        worker.stackWorker.Wait(delay)

    def Time(self):
        return time()

    def Distance(self, pointA, pointB):
        try:
            pointA = wx.RealPoint(pointA[0], pointA[1])
        except:
            raise ValueError("Distance(): pointA must be a point or a list of two numbers")
        try:
            pointB = wx.RealPoint(pointB[0], pointB[1])
        except:
            raise ValueError("Distance(): pointB must be a point or a list of two numbers")
        return math.sqrt((pointB[0] - pointA[0]) ** 2 + (pointB[1] - pointA[1]) ** 2)

    def Alert(self, message):
        if self.stopRunnerThread:
            return
        worker.stackWorker.SendSync(None, ("alert", message))

    def AskYesNo(self, message):
        if self.stopRunnerThread:
            return None
        return worker.stackWorker.SendSync(bool, ("confirm", message))

    def AskText(self, message, defaultResponse=""):
        if self.stopRunnerThread:
            return None
        return worker.stackWorker.SendSync(str, ("prompt", message, defaultResponse))

    def PlaySound(self, filepath):
        worker.stackWorker.SendAsync(("playAudio", filepath))

    def StopSound(self):
        worker.stackWorker.SendAsync(("playAudio",))

    def Paste(self):
        return []

    def IsKeyPressed(self, name):
        if not isinstance(name, str):
            raise TypeError("IsKeyPressed(): name must be a string")

        return name in self.pressedKeys

    def IsMouseDown(self):
        return worker.stackWorker.isMouseDown

    def GetMousePos(self):
        return self.lastMousePos

    @staticmethod
    def MakeColor(r, g, b):
        if not isinstance(r, (float, int)) or not 0 <= r <= 1:
            raise TypeError("Color(): r must be a number between 0 and 1")
        if not isinstance(g, (float, int)) or not 0 <= g <= 1:
            raise TypeError("Color(): g must be a number between 0 and 1")
        if not isinstance(b, (float, int)) or not 0 <= b <= 1:
            raise TypeError("Color(): b must be a number between 0 and 1")
        r, g, b = (int(r * 255), int(g * 255), int(b * 255))
        return f"#{r:02X}{g:02X}{b:02X}"

    @staticmethod
    def MakePoint(x, y):
        if not isinstance(x, (float, int)):
            raise TypeError("Point(): x must be a number")
        if not isinstance(y, (float, int)):
            raise TypeError("Point(): y must be a number")
        return wx.RealPoint(x, y)

    @staticmethod
    def MakeSize(width, height):
        if not isinstance(width, (float, int)):
            raise TypeError("Size(): width must be a number")
        if not isinstance(height, (float, int)):
            raise TypeError("Size(): height must be a number")
        return wx.Size(width, height)

    def RunAfterDelay(self, duration, func, *args, **kwargs):
        try:
            duration = float(duration)
        except ValueError:
            raise TypeError("RunAfterDelay(): duration must be a number")

        startTime = time()

        if self.stopRunnerThread: return

        adjustedDuration = duration + startTime - time()
        if adjustedDuration > 0.010:
            def onTimer():
                if self.stopRunnerThread: return
                func(*args, **kwargs)
            t = worker.setTimeout(onTimer, int(adjustedDuration*1000))
            self.timers.append(t)
        else:
            func(*args, **kwargs)

    def Quit(self):
        pass

    def ResetStopHandlingMouseEvent(self):
        self.stopHandlingMouseEvent = False

    def StopHandlingMouseEvent(self):
        self.stopHandlingMouseEvent = True

    def DidStopHandlingMouseEvent(self):
        return self.stopHandlingMouseEvent
