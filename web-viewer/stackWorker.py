from browser import self as worker
import sys
import cardstock

_LastId = 0
def NextId():
    global _LastId
    _LastId += 1
    return _LastId


class StackWorker(object):
    def __init__(self):
        worker.importScripts(worker.location.origin + '/lib/fabric.worker.js')
        worker.importScripts(worker.location.origin + '/lib/SAT.js')

        self.waitSAB = None
        self.waitSA32 = None
        self.countsSAB = None
        self.countsSA32 = None
        self.dataSAB = None
        self.dataSA16 = None

        self.stackManager = cardstock.StackManager()

        self.isMouseDown = False
        self.focusedFabId = 0

        worker.bind("message", self.OnMessageW)

    def OnMessageW(self, evt):
        msg = evt.data[0]
        values = evt.data[1:]

        # if msg != "frame": print("Worker", msg, values)

        if msg == "frame":
            numFrames = worker.Atomics.sub(self.countsSA32, 0, 1)
            if numFrames == 1:
                self.stackManager.OnFrame()
            self.stackManager.RunDelayedSetDowns()

        elif msg == 'setup':
            self.waitSAB = values[0]
            self.countsSAB = values[1]
            self.dataSAB = values[2]
            self.waitSA32 = worker.Int32Array.new(self.waitSAB)
            self.countsSA32 = worker.Int32Array.new(self.countsSAB)
            self.dataSA16 = worker.Int16Array.new(self.dataSAB)

        elif msg == 'load':
            json = values[0]
            self.stackManager.Load(json.to_dict())
            self.SendAsync(("render",))

        elif msg == 'loadStr':
            jsonStr = values[0]
            self.stackManager.LoadFromStr(jsonStr)
            self.SendAsync(("render",))

        elif msg == 'mouseDown':
            self.isMouseDown = True
            uid, pos = values
            self.stackManager.uiCard.OnFabricMouseDown(uid, pos)

        elif msg == 'mouseMove':
            numMoves = worker.Atomics.sub(self.countsSA32, 1, 1)
            if numMoves == 1:
                uid, pos = values
                self.stackManager.uiCard.OnFabricMouseMove(uid, pos)

        elif msg == 'mouseUp':
            self.isMouseDown = False
            uid, pos = values
            self.stackManager.uiCard.OnFabricMouseUp(uid, pos)

        elif msg == 'keyDown':
            self.stackManager.uiCard.OnKeyDown(*values)

        elif msg == 'keyUp':
            self.stackManager.uiCard.OnKeyUp(*values)

        elif msg == 'textChanged':
            self.stackManager.uiCard.OnTextChanged(*values)

        elif msg == 'textEnter':
            self.stackManager.uiCard.OnTextEnter(*values)

        elif msg == 'objectFocus':
            self.focusedFabId = values[0]

        elif msg == "windowSized":
            self.stackManager.WindowDidResize(*values)

        elif msg == 'imgSize':
            uid = values[0]
            uiImage = self.stackManager.uiCard.FindTargetUi(uid)
            if uiImage:
                uiImage.SetImageSize(values[1], values[2])

    def Wait(self, durationSec):
        self.waitSA32[0] = 0
        worker.Atomics.wait(self.waitSA32, 0, 0, durationSec * 1000)

    def SendAsync(self, *args):
        worker.send(args)

    def SendSync(self, returnType, *args):
        self.waitSA32[0] = 0
        worker.send(args)
        worker.Atomics.wait(self.waitSA32, 0, 0)
        if returnType == bool:
            return bool(self.dataSA16[0])
        elif returnType == str:
            length = self.dataSA16[0] # first int holds length
            if length == -1:
                return None
            s = ""
            for i in range(1, length+1):
                s += chr(self.dataSA16[i])
            return s

    def CreateFab(self, *args, replace=None):
        if replace == None:
            i = NextId()
            worker.send((("fabNew", i, *args),))
        else:
            i = replace
            worker.send((("fabReplace", replace, *args),))
        return i

    def CreateTextbox(self, *args):
        i = NextId()
        worker.send((("tboxNew", i, *args),))
        return i

    def CreateImage(self, *args, replace=None):
        if replace == None:
            i = NextId()
            worker.send((("imgNew", i, *args),))
        else:
            i = replace
            worker.send((("imgReplace", replace, *args),))
        return i

    def write(self, text):
        worker.send((("write", text),))

# Start up the worker class
worker.stackWorker = StackWorker()

sys.stdout = worker.stackWorker
sys.stderr = worker.stackWorker
