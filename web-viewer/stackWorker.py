from browser import self as worker
from browser import timer
import sys
from time import time
import stackManager
from settings import *

"""
This StackWorker class, which runs on a worker thread, works tightly with the StackCanvas class back on the main thread,
communicating by posting messages back and forth.  The StackWorker hosts the StackManager which itself runs the 
cardstock stack and code, and sends messages back to the StackCanvas to update the UI.
"""


# We generate our own ids to recognize individual UI objects on the fabric canvas, back on the main thread.  These are
# passed back and forth as identifiers in mesasges.
_LastId = 0
def NextId():
    global _LastId
    _LastId += 1
    return _LastId


class StackWorker(object):
    def __init__(self):
        worker.importScripts(worker.location.origin + LIB_PREFIX + 'fabric.worker.js')
        worker.importScripts(worker.location.origin + LIB_PREFIX + 'SAT.js')
        worker.importScripts(worker.location.origin + LIB_PREFIX + 'decomp.min.js')

        self.waitSAB = None
        self.waitSA32 = None
        self.countsSAB = None
        self.countsSA32 = None
        self.dataSAB = None
        self.dataSA16 = None

        self.stackManager = stackManager.StackManager()

        self.isMouseDown = False
        self.usingTouchScreen = False
        self.focusedFabId = 0

        worker.bind("message", self.OnMessageW)

    def OnMessageW(self, evt):
        msg = evt.data[0]
        args = evt.data[1:]

        # print("Worker", msg, args)

        if msg == 'setup':
            # Set up the shared memory for sync calls (alert, prompt, confirm)
            self.waitSAB = args[0]
            self.countsSAB = args[1]
            self.dataSAB = args[2]
            self.waitSA32 = worker.Int32Array.new(self.waitSAB)
            self.countsSA32 = worker.Int32Array.new(self.countsSAB)
            self.dataSA16 = worker.Int16Array.new(self.dataSAB)
            # This is our main interval timer for running OnPeriodic, animations, etc.  This fires at ~60 Hz.
            timer.set_interval(self.stackManager.OnPeriodic, 16.666)

        elif msg == 'load':
            # Load a stack from a dict object
            json = args[0]
            self.stackManager.Load(json.to_dict())
            self.SendAsync(("render",))

        elif msg == 'loadStr':
            # load a stack from a json string
            jsonStr = args[0]
            self.stackManager.LoadFromStr(jsonStr)
            self.SendAsync(("render",))

        elif msg == 'mouseDown':
            # handle a mouseDown
            uid, pos, isTouch = args
            self.isMouseDown = True
            self.usingTouchScreen = isTouch
            self.stackManager.uiCard.OnFabricMouseDown(uid, pos, isTouch)

        elif msg == 'mouseMove':
            # handle a mouseMove
            numMoves = worker.Atomics.sub(self.countsSA32, 0, 1)
            if numMoves == 1:
                uid, pos, isTouch = args
                self.stackManager.uiCard.OnFabricMouseMove(uid, pos, isTouch)

        elif msg == 'mouseUp':
            # handle a mouseUp
            self.isMouseDown = False
            uid, pos, isTouch = args
            self.stackManager.uiCard.OnFabricMouseUp(uid, pos, isTouch)

        elif msg == 'keyDown':
            # handle a keyDown
            self.stackManager.uiCard.OnKeyDown(*args)

        elif msg == 'keyUp':
            # handle a keyUp
            self.stackManager.uiCard.OnKeyUp(*args)

        elif msg == "runAnimationsFinished":
            # This got echoed back to us, originally from this thread,
            # to enqueue it to happen now, after the previous handler finished.
            self.stackManager.RunAnimationsFinished()

        elif msg == 'textChanged':
            self.stackManager.uiCard.OnTextChanged(*args)

        elif msg == 'textEnter':
            self.stackManager.uiCard.OnTextEnter(*args)

        elif msg == 'objectFocus':
            self.focusedFabId = args[0]

        elif msg == "windowSized":
            self.stackManager.WindowDidResize(*args)

        elif msg == 'imgSize':
            # when we tell the StackCanvas to add an image object, it downloads the image and tells us the size(w,h)
            # now we can crop/scale the image to fit where it's supposed to go.
            uid = args[0]
            uiImage = self.stackManager.uiCard.FindTargetUi(uid)
            if uiImage:
                uiImage.SetImageSize(args[1], args[2])

    def Wait(self, durationSec):
        # no sleep() allowed, so use Atomics.wait() to wait for a thing that will never happen, but with a timeout!
        start = time()
        endTime = start + durationSec
        while time() < endTime:
            self.stackManager.Yield()
            remaining = (endTime - time()) * 1000
            self.waitSA32[0] = 0
            # wait up to 15ms at a time, or ~1 frame at 60Hz
            worker.Atomics.wait(self.waitSA32, 0, 0, max(0, min(15, remaining)))

    def SendAsync(self, *args):
        # Send a message and don't wait
        worker.send(args)

    def SendSync(self, returnType, *args):
        # Send a message and wait for a response
        self.waitSA32[0] = 0
        worker.send(args)
        # wait for the waitSA32[0] value to be set to a 1, which means the main thread is done, so we can stop waiting
        worker.Atomics.wait(self.waitSA32, 0, 0)
        if returnType == bool:
            # if we're expecting a bool, just look at the first val
            return bool(self.dataSA16[0])
        elif returnType == str:
            # if we're expecting a string, read the first val as length, and then get the rest as 16bit unicode chars
            length = self.dataSA16[0] # first int holds length
            if length == -1:
                return None
            s = ""
            for i in range(1, length+1):
                s += chr(self.dataSA16[i])
            return s

    def CreateFab(self, *args, replace=None):
        # Tell the StackCanvas to create o new fabric object, or replace an existing one
        if replace == None:
            i = NextId()
            worker.send((("fabNew", i, *args),))
        else:
            i = replace
            worker.send((("fabReplace", replace, *args),))
        return i

    def CreateTextField(self, *args):
        # Tell the StackCanvas to create o new fabric TextField object
        i = NextId()
        worker.send((("fieldNew", i, *args),))
        return i

    def CreateImageStatic(self, path, options, replace=None):
        # Tell the StackCanvas to create o new static Image, or replace an existing one
        if replace == None:
            i = NextId()
            worker.send((("imgNewStatic", i, path, options),))
        else:
            i = replace
            worker.send((("imgReplaceStatic", replace, path, options),))
        return i

    def CreateImage(self, *args, replace=None):
        # Tell the StackCanvas to create o new fabric Image object, or replace an existing one
        if replace == None:
            i = NextId()
            worker.send((("imgNew", i, *args),))
        else:
            i = replace
            worker.send((("imgReplace", replace, *args),))
        return i

    def write(self, text):
        # stderr and stdout will write here on print, errors, etc.
        worker.send((("write", text),))

# Start up the worker class
worker.stackWorker = StackWorker()
sys.stdout = worker.stackWorker
sys.stderr = worker.stackWorker
