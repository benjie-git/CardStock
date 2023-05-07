# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

try:
    from browser import window as context
except:
    from browser import self as context

import re
import sys
from browser import timer
import colorsys
import traceback
import wx_compat as wx
from time import time
import models
import types
import math


class Runner():
    """
    The Runner object runs all of the stack's user-written event handlers.  It keeps track of user variables, so that they
    can be shared between handlers, offers global variables and functions, and makes event arguments (message,
    mouse_pos, etc.) available to the handlers that expect them, and then restores any old values of those variables upon
    finishing those events.
    """

    def __init__(self, stackManager):
        self.stackManager = stackManager
        self.cardVarKeys = []  # store names of views on the current card, to remove from clientVars before setting up the next card
        self.lastMousePos = wx.Point(0,0)
        self.pressedKeys = []
        self.keyTimings = {}
        self.timers = []
        self.lastHandlerStack = []
        self.didSetup = False
        self.rewrittenHandlerMap = {}
        self.funcDefs = {}
        self.lastCard = None
        self.stopHandlingMouseEvent = False
        self.stackStartTime = None
        self.broadcastChannel = None
        self.errorMsgs = []

        self.initialClientVars = {
            "wait": self.wait,
            "run_after_delay": self.run_after_delay,
            "time": self.time,
            "distance": self.distance,
            "paste": self.paste,
            "alert": self.alert,
            "ask_yes_no": self.ask_yes_no,
            "ask_text": self.ask_text,
            "goto_card": self.goto_card,
            "goto_next_card": self.goto_next_card,
            "goto_previous_card": self.goto_previous_card,
            "run_stack": self.run_stack,
            "open_url": self.open_url,
            "play_sound": self.play_sound,
            "stop_sound": self.stop_sound,
            "broadcast_message": self.broadcast_message,
            "is_key_pressed": self.is_key_pressed,
            "is_mouse_pressed": self.is_mouse_pressed,
            "is_using_touch_screen": self.is_using_touch_screen,
            "get_mouse_pos": self.get_mouse_pos,
            "clear_focus": self.clear_focus,
            "quit":self.quit,
            "ColorRGB": self.MakeColorRGB,
            "ColorHSB": self.MakeColorHSB,
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
        self.lastHandlerStack = None
        self.didSetup = False
        self.rewrittenHandlerMap = None
        self.funcDefs = None
        self.lastCard = None
        self.stopHandlingMouseEvent = False
        self.stackStartTime = None
        self.clientVars = None

    def StartStack(self):
        self.stackStartTime = time()
        self.clientVars = self.initialClientVars.copy()
        self.cardVarKeys = []
        self.timers = []
        self.lastHandlerStack = []
        self.didSetup = False
        self.rewrittenHandlerMap = {}
        self.funcDefs = {}
        self.lastCard = None
        self.stopHandlingMouseEvent = False

        if "channelName" in context:
            if self.broadcastChannel:
                self.broadcastChannel.close()
            self.broadcastChannel = context.BroadcastChannel.new(context.channelName)
            def onmessage(e):
                if e.data == "close":
                    context.stackWorker.SendAsync(("closeWindow",))
            self.broadcastChannel.onmessage = onmessage

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
        self.lastCard = cardModel

    def AddCardObj(self, model):
        if model.GetCard() == self.lastCard:
            name = model.GetProperty("name")
            self.clientVars[name] = model.GetProxy()
            self.cardVarKeys.append(name)

    def RemoveCardObj(self, model):
        if model.GetCard() == self.lastCard:
            name = model.GetProperty("name")
            del self.clientVars[name]
            self.cardVarKeys.remove(name)

    def StopTimers(self):
        for t in self.timers:
            timer.clear_timeout(t)
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
        if self.stackManager.isEditing:
            return False

        handlerStr = uiModel.handlers[handlerName].strip()
        if handlerStr == "":
            return False

        mouse_pos = None
        key_name = None
        if eventVal and handlerName.startswith("on_mouse"):
            mouse_pos = eventVal
        elif arg and handlerName == "on_key_hold":
            key_name = arg
        elif eventVal and handlerName.startswith("on_key"):
            key_name = self.KeyNameForCode(eventVal)
            if not key_name:
                return False

        self.RunHandlerInternal(uiModel, handlerName, handlerStr, mouse_pos, key_name, arg)
        context.stackWorker.SendAsync(("render",))
        return True

    def RunHandlerInternal(self, uiModel, handlerName, handlerStr, mouse_pos, key_name, arg):
        """ Run an eventHandler.  This always runs on the runnerThread. """
        if not self.didSetup:
            return

        if handlerName in ["on_mouse_press", "on_mouse_move", "on_mouse_release"] and self.stopHandlingMouseEvent:
            return

        noValue = ("no", "value")  # Use this if this var didn't exist/had no value (not even None)

        # Keep this method re-entrant, by storing old values (or lack thereof) of anything we set here,
        # (like self, key, etc.) and replacing or deleting them at the end of the run.
        oldVars = {}

        if "self" in self.clientVars:
            oldVars["self"] = self.clientVars["self"]
        else:
            oldVars["self"] = noValue
        self.clientVars["self"] = uiModel.GetProxy()

        if arg and handlerName == "on_message":
            if "message" in self.clientVars:
                oldVars["message"] = self.clientVars["message"]
            else:
                oldVars["message"] = noValue
            self.clientVars["message"] = arg

        if arg and handlerName == "on_done_loading":
            if "URL" in self.clientVars:
                oldVars["URL"] = self.clientVars["URL"]
            else:
                oldVars["URL"] = noValue
            self.clientVars["URL"] = arg[0]
            if "did_load" in self.clientVars:
                oldVars["did_load"] = self.clientVars["did_load"]
            else:
                oldVars["did_load"] = noValue
            self.clientVars["did_load"] = arg[1]

        if handlerName == "on_card_stock_link":
            if "message" in self.clientVars:
                oldVars["message"] = self.clientVars["message"]
            else:
                oldVars["message"] = noValue
            self.clientVars["message"] = arg

        if handlerName == "on_selection_changed":
            if "is_selected" in self.clientVars:
                oldVars["is_selected"] = self.clientVars["is_selected"]
            else:
                oldVars["is_selected"] = noValue
            self.clientVars["is_selected"] = arg

        if handlerName == "on_resize":
            if "is_initial" in self.clientVars:
                oldVars["is_initial"] = self.clientVars["is_initial"]
            else:
                oldVars["is_initial"] = noValue
            self.clientVars["is_initial"] = arg

        if handlerName == "on_periodic":
            if "elapsed_time" in self.clientVars:
                oldVars["elapsed_time"] = self.clientVars["elapsed_time"]
            else:
                oldVars["elapsed_time"] = noValue
            now = time()
            if uiModel.lastOnPeriodicTime:
                elapsed_time = now - uiModel.lastOnPeriodicTime
            else:
                elapsed_time = now - self.stackStartTime
            uiModel.lastOnPeriodicTime = now
            self.clientVars["elapsed_time"] = elapsed_time

        if mouse_pos and handlerName.startswith("on_mouse"):
            if "mouse_pos" in self.clientVars:
                oldVars["mouse_pos"] = self.clientVars["mouse_pos"]
            else:
                oldVars["mouse_pos"] = noValue
            self.clientVars["mouse_pos"] = mouse_pos

        if mouse_pos and handlerName in ("on_mouse_press", "on_mouse_move", "on_mouse_release"):
            if "fromTouchScreen" in self.clientVars:
                oldVars["fromTouchScreen"] = self.clientVars["fromTouchScreen"]
            else:
                oldVars["fromTouchScreen"] = noValue
            self.clientVars["fromTouchScreen"] = arg

        if key_name and handlerName.startswith("on_key"):
            if "key_name" in self.clientVars:
                oldVars["key_name"] = self.clientVars["key_name"]
            else:
                oldVars["key_name"] = noValue
            self.clientVars["key_name"] = key_name

        if arg and handlerName == "on_key_hold":
            if "elapsed_time" in self.clientVars:
                oldVars["elapsed_time"] = self.clientVars["elapsed_time"]
            else:
                oldVars["elapsed_time"] = noValue
            if key_name in self.keyTimings:
                now = time()
                elapsed_time = now - self.keyTimings[key_name]
                self.keyTimings[key_name] = now
                self.clientVars["elapsed_time"] = elapsed_time
            else:
                # Shouldn't happen!  But just in case, return something that won't crash if the users divides by it
                self.clientVars["elapsed_time"] = 0.01

        if arg and handlerName == "on_bounce":
            if "other_object" in self.clientVars:
                oldVars["other_object"] = self.clientVars["other_object"]
            else:
                oldVars["other_object"] = noValue
            self.clientVars["other_object"] = arg[0]
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
            errMsg = f"{error_class}: {detail} in {errModel.properties['name']}:{errHandlerName}:{line_number}"
            self.ReportError(errModel, errHandlerName, line_number, errMsg)
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
                    errMsg = f"{error_class}: {detail} in {errModel.properties['name']}:{errHandlerName}:{line_number}"
                else:
                    errMsg = f"{error_class}: {detail}:{errHandlerName}:{line_number}\n{handlerStr}"
                self.ReportError(errModel, errHandlerName, line_number, errMsg)

        del self.lastHandlerStack[-1]

        # restore the old values from before this handler was called
        for k, v in oldVars.items():
            if v == noValue:
                if k in self.clientVars:
                    self.clientVars.pop(k)
            else:
                self.clientVars[k] = v

    def CullRewrittenHandlerMap(self, handlers):
        self.rewrittenHandlerMap = {k:v for k,v in self.rewrittenHandlerMap.items() if k in handlers}

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
        line_number = None
        errModel = None
        errHandlerName = None

        oldCard = None
        oldSelf = None
        in_func = []

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
            func(*args, **kwargs)
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            trace = traceback.extract_tb(tb)
            for i in range(len(trace)):
                if trace[i].filename == "<string>" and trace[i].name != "<module>":
                    if trace[i].name in self.funcDefs:
                        errModel = self.funcDefs[trace[i].name][0]
                        if errModel.clonedFrom: errModel = errModel.clonedFrom
                        errHandlerName = self.funcDefs[trace[i].name][1]
                        line_number = trace[i].lineno
                    in_func.append((trace[i].name, trace[i].lineno))

            if error_class and errModel:
                msg = f"{error_class} in {self.HandlerPath(errModel, errHandlerName)}, line {line_number}: {detail}"
                if len(in_func) > 1:
                    frames = [f"{f[0]}():{f[1]}" for f in in_func]
                    trail = ' => '.join(frames)
                    msg += f" (from {trail})"
                self.ReportError(errModel, errHandlerName, line_number, msg)
            else:
                self.ReportError("", "", 0, detail)

        if oldCard:
            self.SetupForCard(oldCard)
        if oldSelf:
            self.clientVars["self"] = oldSelf
        else:
            if "self" in self.clientVars:
                self.clientVars.pop("self")

    def ReportError(self, errModel, errHandlerName, errLineNum, errMsg):
        print(errMsg, file = sys.stderr)

        if "channelName" in context:
            if errMsg not in self.errorMsgs:
                if errModel:
                    self.errorMsgs.append(errMsg)
                    path = errModel.GetPath()
                    errData = (path, errHandlerName, errLineNum, errMsg)
                else:
                    errData = ("", "", 0, errMsg)
                if self.broadcastChannel:
                    self.broadcastChannel.postMessage(errData)

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
        key_name = self.KeyNameForCode(code)
        if key_name and key_name not in self.pressedKeys:
            self.pressedKeys.append(key_name)
            self.keyTimings[key_name] = time()
            return True
        return False

    def OnKeyUp(self, code):
        key_name = self.KeyNameForCode(code)
        if key_name and key_name in self.pressedKeys:
            self.pressedKeys.remove(key_name)
            del self.keyTimings[key_name]

    def ClearPressedKeys(self):
        self.pressedKeys = []
        self.keyTimings = {}

    def UpdateClientVar(self, k, v):
        if k in self.clientVars:
            self.clientVars[k] = v

    def SetFocus(self, obj):
        if obj:
            uiView = self.stackManager.GetUiViewByModel(obj._model)
            if uiView and uiView.model.type == "textfield":
                context.stackWorker.SendAsync(("focus", uiView.textbox))
        else:
            context.stackWorker.SendAsync(("focus", 0))

    # --------- User-accessible view functions -----------

    def broadcast_message(self, message):
        if not isinstance(message, str):
            raise TypeError("broadcast_message(): message must be a string")

        self.RunHandler(self.stackManager.uiCard.model, "on_message", None, message)
        for ui in self.stackManager.uiCard.GetAllUiViews():
            self.RunHandler(ui.model, "on_message", None, message)

    def goto_card(self, card):
        index = None
        if isinstance(card, str):
            cardName = card
        elif isinstance(card, models.Card):
            cardName = card._model.GetProperty("name")
        elif isinstance(card, int):
            index = card-1
        else:
            raise TypeError("goto_card(): card must be card object, a string, or an int")

        if index is None:
            for m in self.stackManager.stackModel.childModels:
                if m.GetProperty("name") == cardName:
                    index = self.stackManager.stackModel.childModels.index(m)
        if index is not None:
            if index < 0 or index >= len(self.stackManager.stackModel.childModels):
                # Modify index back to 1 based for user visible error message
                raise ValueError(f'goto_card(): card number {index + 1} does not exist')
            self.stackManager.LoadCardAtIndex(index)
        else:
            raise ValueError("goto_card(): cardName '" + cardName + "' does not exist")

    def goto_next_card(self):
        cardIndex = self.stackManager.cardIndex + 1
        if cardIndex >= len(self.stackManager.stackModel.childModels): cardIndex = 0
        self.stackManager.LoadCardAtIndex(cardIndex)

    def goto_previous_card(self):
        cardIndex = self.stackManager.cardIndex - 1
        if cardIndex < 0: cardIndex = len(self.stackManager.stackModel.childModels) - 1
        self.stackManager.LoadCardAtIndex(cardIndex)

    def run_stack(self, filename, cardNumber=1, setupValue=None):
        print("run_stack(): unsupported on web")

    def return_from_stack(self, result=None):
        print("return_from_stack(): unsupported on web")

    def GetStackSetupValue(self):
        print("GetStackSetupValue(): unsupported on web")
        return None

    def wait(self, delay):
        try:
            delay = float(delay)
        except ValueError:
            raise TypeError("wait(): delay must be a number")

        context.stackWorker.SendAsync(("render",))
        context.stackWorker.Wait(delay)

    def time(self):
        return time()

    def distance(self, pointA, pointB):
        try:
            pointA = wx.RealPoint(pointA[0], pointA[1])
        except:
            raise ValueError("distance(): pointA must be a point or a list of two numbers")
        try:
            pointB = wx.RealPoint(pointB[0], pointB[1])
        except:
            raise ValueError("distance(): pointB must be a point or a list of two numbers")
        return math.sqrt((pointB[0] - pointA[0]) ** 2 + (pointB[1] - pointA[1]) ** 2)

    def alert(self, message):
        context.stackWorker.EnqueueSyncPressedKeys()
        context.stackWorker.SendSync(None, ("alert", message))

    def ask_yes_no(self, message):
        context.stackWorker.EnqueueSyncPressedKeys()
        return context.stackWorker.SendSync(bool, ("confirm", message))

    def ask_text(self, message, defaultResponse=""):
        context.stackWorker.EnqueueSyncPressedKeys()
        return context.stackWorker.SendSync(str, ("prompt", message, defaultResponse))

    def open_url(self, URL, in_place=False):
        context.stackWorker.SendAsync(("open_url", URL, in_place))

    def play_sound(self, filepath):
        context.stackWorker.SendAsync(("playAudio", filepath))

    def stop_sound(self):
        context.stackWorker.SendAsync(("playAudio",))

    def paste(self):
        return []

    def is_key_pressed(self, name):
        if not isinstance(name, str):
            raise TypeError("is_key_pressed(): name must be a string")

        return name in self.pressedKeys

    def is_mouse_pressed(self):
        return context.stackWorker.isMouseDown

    def is_using_touch_screen(self):
        return context.stackWorker.usingTouchScreen

    def get_mouse_pos(self):
        return self.lastMousePos

    def clear_focus(self):
        self.SetFocus(None)

    @staticmethod
    def MakeColorRGB(red, green, blue):
        if not isinstance(red, (float, int)) or not 0 <= red <= 1:
            raise TypeError("ColorRGB(): red must be a number between 0 and 1")
        if not isinstance(green, (float, int)) or not 0 <= green <= 1:
            raise TypeError("ColorRGB(): green must be a number between 0 and 1")
        if not isinstance(blue, (float, int)) or not 0 <= blue <= 1:
            raise TypeError("ColorRGB(): blue must be a number between 0 and 1")
        red, green, blue = (int(red * 255), int(green * 255), int(blue * 255))
        return f"#{red:02X}{green:02X}{blue:02X}"

    @staticmethod
    def MakeColorHSB(hue, saturation, brightness):
        if not isinstance(hue, (float, int)) or not 0 <= hue <= 1:
            raise TypeError("ColorHSB(): hue must be a number between 0 and 1")
        if not isinstance(saturation, (float, int)) or not 0 <= saturation <= 1:
            raise TypeError("ColorHSB(): saturation must be a number between 0 and 1")
        if not isinstance(brightness, (float, int)) or not 0 <= brightness <= 1:
            raise TypeError("ColorHSB(): brightness must be a number between 0 and 1")
        red, green, blue = colorsys.hsv_to_rgb(hue, saturation, brightness)
        red, green, blue = (int(red * 255), int(green * 255), int(blue * 255))
        return f"#{red:02X}{green:02X}{blue:02X}"

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

    def run_after_delay(self, duration, func, *args, **kwargs):
        try:
            duration = float(duration)
        except ValueError:
            raise TypeError("run_after_delay(): duration must be a number")

        if duration > 0.010:
            def onTimer():
                func(*args, **kwargs)
            t = timer.set_timeout(onTimer, int(duration*1000))
            self.timers.append(t)
        else:
            func(*args, **kwargs)

    def quit(self):
        pass

    def ResetStopHandlingMouseEvent(self):
        self.stopHandlingMouseEvent = False

    def stop_handling_mouse_event(self):
        self.stopHandlingMouseEvent = True

    def DidStopHandlingMouseEvent(self):
        return self.stopHandlingMouseEvent
