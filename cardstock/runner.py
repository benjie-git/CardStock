# This file is part of CardStock.
#     https://github.com/benjie-git/CardStock
#
# Copyright Ben Levitt 2020-2023
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.  If a copy
# of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re
import sys
import os
import traceback

import requests
import wx
import types
from uiCard import Card
import colorsys
from time import sleep, time
import math
from errorListWindow import CardStockError
import threading
from codeRunnerThread import CodeRunnerThread, RunOnMainSync, RunOnMainAsync
import queue
import sanitizer
from enum import Enum
import simpleaudio
import tones
import consoleWindow

try:
    from streamp3 import MP3Decoder
except ImportError:
    MP3Decoder = None


class TaskType (Enum):
    """ Types of tasks in the handlerQueue """
    Wake = 1            # Wake up the handler thread
    SetupCard = 2       # Set up for the card we just switched to
    Handler = 3         # Run an event handler
    Func = 4            # Run an arbitrary function with args and kwargs
    Code = 5            # Run an arbitrary string as code
    StopHandlingMouseEvent = 6  # Stop propagating the current mouse event
    CallbackMain = 7    # Run a callback func on the main thread.  Used for synchronization.


class Runner():
    """
    The Runner object runs all of the stack's user-written event handlers.  It keeps track of user variables, so that they
    can be shared between handlers, offers global variables and functions, and makes event arguments (message,
    mouse_pos, etc.) available to the handlers that expect them, and then restores any old values of those variables upon
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
        self.shouldUpdateVars = False
        self.tonePlayers = {}

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
        self.generatingThumbnail = False
        self.compileCache = {}

        self.soundCache = {}

        self.stackStartTime = time()

        self.initialClientVars = {
            "wait": self.wait,
            "run_after_delay": self.run_after_delay,
            "time": self.time,
            "distance": self.distance,
            "angle_from_points": self.angle_from_points,
            "rotate_point": self.rotate_point,
            "alert": self.alert,
            "ask_yes_no": self.ask_yes_no,
            "ask_text": self.ask_text,
            "input": self.input,
            "goto_card": self.goto_card,
            "goto_next_card": self.goto_next_card,
            "goto_previous_card": self.goto_previous_card,
            "run_stack": self.run_stack,
            "open_url": self.open_url,
            "request_url": self.request_url,
            "play_sound": self.play_sound,
            "play_tone": self.play_tone,
            "play_note": self.play_note,
            "play_notes": self.play_notes,
            "stop_sound": self.stop_sound,
            "is_key_pressed": self.is_key_pressed,
            "is_mouse_pressed": self.is_mouse_pressed,
            "is_using_touch_screen": self.is_using_touch_screen,
            "get_mouse_pos": self.get_mouse_pos,
            "clear_focus": self.clear_focus,
            "quit":self.quit,
            "color_rgb": self.color_rgb,
            "color_hsb": self.color_hsb,
            "Point": self.MakePoint,
            "Size": self.MakeSize,
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
        self.keyCodeStringReverseMap = None

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

    def AddCallbackToMain(self, func, *args):
        self.handlerQueue.put((TaskType.CallbackMain, func, *args))

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
        self.clientVars["stack"] = self.stackManager.stackModel.GetProxy()
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

    def EnableUpdateVars(self, enable):
        self.shouldUpdateVars = enable

    def HandlerChanged(self, model, handlerName):
        path = model.GetPath() + "." + handlerName
        if path in self.compileCache:
            del self.compileCache[path]

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
            self.stackReturnQueue.put(None)  # Stop waiting for a run_stack() call to return
            self.handlerQueue.put((TaskType.Wake, )) # Wake up the runner thread get() call so it can see that we're stopping

            def waitAndYield(duration):
                # wait up to duration seconds for the stack to finish running
                # run wx.YieldIfNeeded() to process main thread events while waiting, to allow @RunOnMainSync* methods to complete
                if self.generatingThumbnail: return
                endTime = time() + duration
                while time() < endTime:
                    breakpoint = time() + 0.05
                    if len(self.lastHandlerStack) == 0:
                        return
                    while time() < breakpoint:
                        wx.YieldIfNeeded()

            # Wait a bit before force-killing the thread
            waitAndYield(0.2)

            for i in range(4):
                # Try a few times, on the off chance that someone has a long/infinite loop in their code,
                # inside a try block, with another long/infinite loop inside the exception handler
                self.runnerThread.terminate()
                waitAndYield(0.2)
                self.runnerThread.join(0.05)
                if not self.runnerThread.is_alive():
                    break
            if self.runnerThread.is_alive() and not self.generatingThumbnail:
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
        self.stop_sound()
        self.soundCache = None
        self.cardVarKeys = None
        self.clientVars = None
        self.timers = None
        self.varUpdateTimer = None
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
        This is used to send run_after_delay(), and animation on_finished functions
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

        # Allow a few last events to run while shutting down, to make sure we got to running any on_exit_stack events
        exitCountdown = 4

        try:
            while True:
                runningOnExitStack = False
                args = self.handlerQueue.get()
                if args[0] == TaskType.Wake:
                    # This is an enqueued task meant to Refresh after running all other tasks,
                    # and also serves to wake up the runner thread for stopping.
                    if not self.stopRunnerThread:
                        self.stackManager.view.Refresh()  # TODO: This should not need to be called?
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
                    self.RunFuncWithExceptionHandling(args[1], *args[2], **args[3])
                elif args[0] == TaskType.Code:
                    # Run the given code
                    self.RunCodeWithExceptionHandling(args[1])
                elif args[0] == TaskType.CallbackMain:
                    @RunOnMainAsync
                    def f(a, b):
                        a(*b)
                    f(args[1], args[2:])
                elif args[0] == TaskType.Handler:
                    # Run this handler
                    self.lastCard = args[1].GetCard()
                    self.RunHandlerInternal(*args[1:])
                    if args[2] == "on_exit_stack":
                        runningOnExitStack = True
                    if args[2] == "on_periodic":
                        self.numOnPeriodicsQueued -= 1

                if self.stopRunnerThread:
                    exitCountdown -= 1
                if exitCountdown == 0 and not runningOnExitStack:
                    break

        except SystemExit:
            # The runnerThread got killed, because we told it to stop.
            if self.lastHandlerStack and len(self.lastHandlerStack) > 0 and not self.generatingThumbnail:
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

        mouse_pos = None
        key_name = None
        if event and handlerName.startswith("on_mouse"):
            mouse_pos = wx.RealPoint(*self.stackManager.view.ScreenToClient(wx.GetMousePosition()))
        elif arg and handlerName == "on_key_hold":
            key_name = arg
        elif event and handlerName.startswith("on_key"):
            key_name = self.KeyNameForEvent(event)
            if not key_name:
                return False

        if threading.current_thread() == self.runnerThread:
            self.RunHandlerInternal(uiModel, handlerName, handlerStr, mouse_pos, key_name, arg)
        else:
            if handlerName == "on_periodic":
                self.numOnPeriodicsQueued += 1
            self.handlerQueue.put((TaskType.Handler, uiModel, handlerName, handlerStr, mouse_pos, key_name, arg))
        return True

    def RunHandlerInternal(self, uiModel, handlerName, handlerStr, mouse_pos, key_name, arg):
        """ Run an eventHandler.  This always runs on the runnerThread. """
        if not self.didSetup:
            return

        if handlerName in ["on_mouse_press", "on_mouse_move", "on_mouse_release"] and self.stopHandlingMouseEvent:
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
        path = uiModel.GetPath() + "." + handlerName

        self.lastHandlerStack.append((uiModel, handlerName))

        error = None
        error_class = None
        line_number = None
        errModel = None
        errHandlerName = None
        in_func = []
        detail = None

        try:
            isNew = False
            if path in self.compileCache:
                ast = self.compileCache[path]
            else:
                handlerStr = self.RewriteHandler(handlerStr)
                ast = compile(handlerStr, "<string>", "exec")
                self.compileCache[path] = ast
                isNew = True
            # Use this for noticing user-definitions of new functions
            if isNew:
                oldClientVars = self.clientVars.copy()

            exec(ast, self.clientVars)
            if isNew:
                self.ScrapeNewFuncDefs(oldClientVars, self.clientVars, uiModel, handlerName)
        except SyntaxError as err:
            if isNew:
                self.ScrapeNewFuncDefs(oldClientVars, self.clientVars, uiModel, handlerName)
            detail = err.msg
            error_class = err.__class__.__name__
            line_number = err.lineno
            errModel = uiModel
            errHandlerName = handlerName
        except Exception as err:
            if isNew:
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
                        if errModel.clonedFrom: errModel = errModel.clonedFrom
                        errHandlerName = handlerName
                        line_number = trace[i].lineno
                        in_func.append((handlerName, trace[i].lineno))
                    elif line_number and trace[i].filename == "<string>" and trace[i].name != "<module>":
                        if trace[i].name in self.funcDefs:
                            errModel = self.funcDefs[trace[i].name][0]
                            if errModel.clonedFrom: errModel = errModel.clonedFrom
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

        if self.shouldUpdateVars:
            self.stackManager.UpdateVars()

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

    def RunCodeWithExceptionHandling(self, code):
        self.RunWithExceptionHandling(code, None)

    def RunFuncWithExceptionHandling(self, func, *args, **kwargs):
        self.RunWithExceptionHandling(None, func, *args, **kwargs)

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
                        if isinstance(result, str):
                            print(f"'{result}'")
                        else:
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
                            if errModel.clonedFrom: errModel = errModel.clonedFrom
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

        if self.shouldUpdateVars:
            self.stackManager.UpdateVars()

    def ScrapeNewFuncDefs(self, oldVars, newVars, model, handlerName):
        # Keep track of where each user function has been defined, so we can send you to the right handler's code in
        # the Designer when the user clicks on an error in the ErrorList.
        for (k, v) in newVars.items():
            if isinstance(v, types.FunctionType) and (k not in oldVars or oldVars[k] != v):
                self.funcDefs[k] = (model, handlerName)

    def HandlerPath(self, model, handlerName, card=None):
        if model.type in ["card", "stack"]:
            return f"{model.GetProperty('name')}.{handlerName}()"
        else:
            if card is None:
                card = model.GetCard()
            return f"{model.GetProperty('name')}.{handlerName}() on card '{card.GetProperty('name')}'"

    def KeyNameForEvent(self, event):
        code = event.GetKeyCode()
        if code in self.keyCodeStringMap:
            return self.keyCodeStringMap[code]
        elif event.GetUnicodeKey() != wx.WXK_NONE:
            return chr(event.GetUnicodeKey())
        return None

    def KeyCodeForName(self, name):
        if not self.keyCodeStringReverseMap:
            self.keyCodeStringReverseMap = {value:key for key,value in self.keyCodeStringMap.items()}
        if name in self.keyCodeStringReverseMap:
            return self.keyCodeStringReverseMap[name]
        else:
            return ord(name)

    def OnKeyDown(self, event):
        key_name = self.KeyNameForEvent(event)
        if key_name and key_name not in self.pressedKeys:
            self.pressedKeys.append(key_name)
            self.keyTimings[key_name] = time()
            return True
        return False

    def OnKeyUp(self, event):
        key_name = self.KeyNameForEvent(event)
        if key_name and key_name in self.pressedKeys:
            self.pressedKeys.remove(key_name)
            del self.keyTimings[key_name]

    def ClearPressedKeys(self):
        self.pressedKeys = []
        self.keyTimings = {}

    def UpdateClientVar(self, k, v):
        if k in self.clientVars:
            self.clientVars[k] = v

    def GetClientVars(self):
        # Update the analyzer for autocomplete
        if not self.clientVars:
            return {}
        vars = self.clientVars.copy()
        for v in self.initialClientVars:
            vars.pop(v)
        if '__builtins__' in vars:
            vars.pop('__builtins__')
        if '__warningregistry__' in vars:
            vars.pop('__warningregistry__')
        return vars

    def EnqueueSyncPressedKeys(self):
        for name in self.pressedKeys:
            e = wx.KeyEvent()
            code = self.KeyCodeForName(name)
            e.SetKeyCode(code)
            self.stackManager.uiCard.OnKeyUp(e)

    @RunOnMainAsync
    def SetFocus(self, obj):
        if obj:
            uiView = self.stackManager.GetUiViewByModel(obj._model)
            if uiView:
                if uiView.model.type == "textfield":
                    sel = uiView.view.GetSelection()
                uiView.view.SetFocus()
                if uiView.model.type == "textfield":
                    uiView.view.SetSelection(sel[0], sel[1])
        else:
            self.stackManager.uiCard.view.SetFocus()


    # --------- User-accessible view functions -----------

    def goto_card(self, card):
        index = None
        if isinstance(card, str):
            cardName = card
        elif isinstance(card, Card):
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
        if self.stopRunnerThread or self.generatingThumbnail or not self.viewer:
            return None
        success = self.viewer.GosubStack(filename, cardNumber-1, sanitizer.SanitizeValue(setupValue, []))
        if success:
            result = self.stackReturnQueue.get()
            if not self.stopRunnerThread:
                return result
            else:
                raise RuntimeError("Return")
        else:
            raise RuntimeError(f"run_stack(): Couldn't find stack '{filename}'.")

    def return_from_stack(self, result=None):
        if not self.viewer:
            return
        self.RunHandler(self.stackManager.stackModel, "on_exit_stack", None)
        stackReturnValue = sanitizer.SanitizeValue(result, [])
        if self.viewer.GosubStack(None,-1, stackReturnValue):
            raise RuntimeError('Return')

    def GetStackSetupValue(self):
        return self.stackSetupValue

    def wait(self, delay):
        try:
            delay = float(delay)
        except ValueError:
            raise TypeError("wait(): delay must be a number")

        self.stackManager.view.RefreshIfNeeded()
        endTime = time() + delay
        while time() < endTime:
            remaining = endTime - time()
            if self.stopRunnerThread or self.generatingThumbnail:
                break
            sleep(min(remaining, 0.03))
            self.stackManager.OnPeriodicTimer(None)
            self.stackManager.view.RefreshIfNeeded()
            wx.YieldIfNeeded()

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

    def angle_from_points(self, pointA, pointB):
        try:
            pointA = wx.RealPoint(pointA[0], pointA[1])
        except:
            raise ValueError("angle_from_points(): pointA must be a Point object or a list of two numbers")
        try:
            pointB = wx.RealPoint(pointB[0], pointB[1])
        except:
            raise ValueError("angle_from_points(): pointB must be a Point object or a list of two numbers")
        return (math.degrees(math.atan2(*(tuple(pointB - pointA))))-90)%360

    def rotate_point(self, point, angle):
        try:
            point = wx.RealPoint(point[0], point[1])
        except:
            raise ValueError("rotate_point(): point must be a Point object or a list of two numbers")
        try:
            angle = float(angle)
        except ValueError:
            raise TypeError("rotate_point(): angle must be a number")

        angle = math.radians(angle)
        px, py = point
        return self.MakePoint(-(math.cos(angle) * -px - math.sin(angle) * py),
                math.sin(angle) * -px + math.cos(angle) * py)

    def alert(self, message):
        if self.stopRunnerThread or self.generatingThumbnail:
            return

        @RunOnMainSync
        def func():
            wx.MessageDialog(None, str(message), "", wx.OK).ShowModal()

        self.EnqueueSyncPressedKeys()
        func()

    def ask_yes_no(self, message):
        if self.stopRunnerThread or self.generatingThumbnail:
            return None

        @RunOnMainSync
        def func():
            return wx.MessageDialog(None, str(message), "", wx.YES_NO).ShowModal() == wx.ID_YES

        self.EnqueueSyncPressedKeys()
        return func()

    def ask_text(self, message, defaultResponse=None):
        if self.stopRunnerThread or self.generatingThumbnail:
            return None

        @RunOnMainSync
        def func():
            dlg = wx.TextEntryDialog(None, str(message), '')
            if defaultResponse is not None:
                dlg.SetValue(str(defaultResponse))
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
            return None

        self.EnqueueSyncPressedKeys()
        return func()

    def input(self, prompt=""):
        if self.stopRunnerThread or self.generatingThumbnail:
            return None

        self.inputText = None

        def gotInput(text):
            self.inputText = text

        @RunOnMainSync
        def f():
            self.viewer.consoleWindow.RemovePrompt()
            self.viewer.consoleWindow.AppendText(prompt, consoleWindow.OUTPUT_STYLE, True)
            self.viewer.consoleWindow.inputFunc = gotInput

            self.viewer.consoleWindow.Show()
            self.viewer.consoleWindow.Focus()

        f()
        self.stackManager.analyzer.disableAC = True
        while True:
            if self.inputText is not None:
                break
            sleep(0.1)

        self.stackManager.analyzer.disableAC = False
        t = self.inputText
        del self.inputText
        return t

    def open_url(self, URL, in_place=False):
        if not isinstance(URL, str):
            raise TypeError("open_url(): URL must be a string")

        wx.LaunchDefaultBrowser(URL)

    def request_url(self, URL, params=None, headers=None, method="GET", timeout=None, on_done=None):
        if not on_done:
            response = requests.request(method, url=URL, params=params, headers=headers, timeout=timeout)
            return response.text
        else:
            def do_request():
                response = requests.request(method, url=URL, params=params, headers=headers, timeout=timeout)
                @RunOnMainAsync
                def f(code, text):
                    self.RunWithExceptionHandling(None, on_done, code, text)
                    self.stackManager.view.Refresh()
                f(response.status_code, response.text)
            CodeRunnerThread(target=do_request).start()

    def play_tone(self, frequency, duration, wait=False):
        if not isinstance(frequency, (int, float)):
            raise TypeError('play_tone(): frequency must be a number')
        if not isinstance(duration, (int, float)) or duration > 60:
            raise ValueError('play_tone(): duration must be a number less than 60 (one minute)')

        filepath = f"::TONE::{frequency}::{duration}"

        if frequency in self.tonePlayers:
            self.tonePlayers[frequency].stop()
            del self.tonePlayers[frequency]

        if duration <= 0:
            return

        if filepath in self.soundCache:
            s = self.soundCache[filepath]
        else:
            b = tones.get_tone_data(frequency, duration)
            s = simpleaudio.WaveObject(b, 1, 2, 44100)
            self.soundCache[filepath] = s
        if s:
            p = s.play()
            self.tonePlayers[frequency] = p
            if wait:
                p.wait_done()
                del self.tonePlayers[frequency]


    def play_note(self, note, duration, wait=False):
        if not isinstance(note, str) or not re.match(r'[a-gA-G]#?[1-6]*', note):
            raise TypeError('play_note(): note must be a note name of the format "<Note letter>" optionally followed '
                            'by a "#" and optional octave number 1-6.  For example: "A", "C#", "D2", or "F#3".')
        if not isinstance(duration, (int, float)) or duration > 60:
            raise ValueError('play_note(): duration must be a number less than 60 (one minute)')

        self.play_tone(tones.note_frequency(note), duration, wait)

    def play_notes(self, notes, tempo, wait=False):
        if not isinstance(notes, str):
            raise TypeError('play_notes(): notes must be a string of note names, separated by spaces, each of the format "<Note letter>" optionally followed '
                            'by a "#" and optional octave number 1-6.  Each note name can also be followed by an optional note length after a "/" character.  '
                            'For example: "A3/8 C#3/2" would play an eighth note at A3 followed by a half note at C#3.  Notes are quarter notes by default.')
        if not isinstance(tempo, (int, float)):
            raise ValueError('play_notes(): tempo must be a number')

        def play_remaining_notes(note_list):
            if len(note_list) == 0:
                return

            note = note_list[0]

            if "/" in note:
                n, b = note.split("/")
                b = int(b)
            else:
                n = note
                b = 4  # Default to 1/4 note

            # get duration in seconds of this note
            # 60 s/min * 2 half_notes/whole / tempo / fraction_of_beat
            d = 60.0 * 2 / tempo / b

            if n.upper() != "R":
                self.play_note(n, d * 0.95)

            note_list = note_list[1:]
            if wait:
                self.wait(d)
                play_remaining_notes(note_list)
            else:
                self.run_after_delay(d, lambda nl=note_list: play_remaining_notes(nl))

        play_remaining_notes(notes.split(" "))

    def play_sound(self, filepath, wait=False):
        if not isinstance(filepath, str):
            raise TypeError("play_sound(): filepath must be a string")

        if self.stopRunnerThread or self.generatingThumbnail:
            return

        filepath = self.stackManager.resPathMan.GetAbsPath(filepath)

        if not os.path.exists(filepath):
            raise ValueError("play_sound(): No file at '" + filepath + "'")

        if filepath in self.soundCache:
            s = self.soundCache[filepath]
        else:
            if filepath.lower().endswith(".mp3"):
                if MP3Decoder:
                    decoded = bytearray()
                    with open(filepath, 'rb') as mp3_file:
                        decoder = MP3Decoder(mp3_file)
                        for chunk in decoder:
                            decoded.extend(chunk)
                        s = simpleaudio.WaveObject(decoded, decoder.num_channels, 2, decoder.sample_rate)
                else:
                    raise ValueError("play_sound(): Python module streamp3 not found, so playing mp3 files is not supported.")
            else:
                s = simpleaudio.WaveObject.from_wave_file(filepath)
            if s:
                self.soundCache[filepath] = s
            else:
                raise ValueError("play_sound(): Couldn't read audio file at '" + filepath + "'")

        if s:
            p = s.play()
            if wait:
                p.wait_done()

    def stop_sound(self):
        simpleaudio.stop_all()

    def is_key_pressed(self, name):
        if not isinstance(name, str):
            raise TypeError("is_key_pressed(): name must be a string")

        return name in self.pressedKeys

    @RunOnMainSync
    def is_mouse_pressed(self):
        return wx.GetMouseState().LeftIsDown()

    def is_using_touch_screen(self):
        return False  # Only implemented in web viewer

    @RunOnMainSync
    def get_mouse_pos(self):
        return wx.RealPoint(*self.stackManager.view.ScreenToClient(*wx.GetMousePosition()))

    def clear_focus(self):
        self.SetFocus(None)

    @staticmethod
    def color_rgb(red, green, blue):
        if not isinstance(red, (float, int)) or not 0 <= red <= 1:
            raise TypeError("color_rgb(): red must be a number between 0 and 1")
        if not isinstance(green, (float, int)) or not 0 <= green <= 1:
            raise TypeError("color_rgb(): green must be a number between 0 and 1")
        if not isinstance(blue, (float, int)) or not 0 <= blue <= 1:
            raise TypeError("color_rgb(): blue must be a number between 0 and 1")
        red, green, blue = (int(red * 255), int(green * 255), int(blue * 255))
        return f"#{red:02X}{green:02X}{blue:02X}"

    @staticmethod
    def color_hsb(hue, saturation, brightness):
        if not isinstance(hue, (float, int)) or not 0 <= hue <= 1:
            raise TypeError("color_hsb(): hue must be a number between 0 and 1")
        if not isinstance(saturation, (float, int)) or not 0 <= saturation <= 1:
            raise TypeError("color_hsb(): saturation must be a number between 0 and 1")
        if not isinstance(brightness, (float, int)) or not 0 <= brightness <= 1:
            raise TypeError("color_hsb(): brightness must be a number between 0 and 1")
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

    def run_after_delay(self, duration, func):
        try:
            duration = float(duration)
        except ValueError:
            raise TypeError("run_after_delay(): duration must be a number")

        startTime = time()

        @RunOnMainAsync
        def f():
            if self.stopRunnerThread or self.generatingThumbnail: return

            adjustedDuration = duration + startTime - time()
            if adjustedDuration > 0.010:
                timer = wx.Timer()
                def onTimer(event):
                    if self.stopRunnerThread: return
                    self.EnqueueFunction(func)
                timer.Bind(wx.EVT_TIMER, onTimer)
                timer.StartOnce(int(adjustedDuration*1000))
                self.timers.append(timer)
            else:
                self.EnqueueFunction(func)

        f()

    @RunOnMainAsync
    def quit(self):
        if self.stopRunnerThread or self.stackManager.isEditing: return
        self.stackManager.view.TopLevelParent.OnMenuClose(None)

    def ResetStopHandlingMouseEvent(self):
        if self.handlerQueue:
            self.handlerQueue.put((TaskType.StopHandlingMouseEvent, ))

    def stop_handling_mouse_event(self):
        self.stopHandlingMouseEvent = True

    def DidStopHandlingMouseEvent(self):
        return self.stopHandlingMouseEvent
