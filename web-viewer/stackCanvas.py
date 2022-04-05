from browser import window, document, worker, bind, timer
import sys

stackWorker = worker.Worker("stackWorker")


class StackCanvas(object):
    def __init__(self):
        self.waitSAB = window.SharedArrayBuffer.new(4)
        self.waitSA32 = window.Int32Array.new(self.waitSAB)
        self.countsSAB = window.SharedArrayBuffer.new(8)
        self.countsSA32 = window.Int32Array.new(self.countsSAB)
        self.dataSAB = window.SharedArrayBuffer.new(32768)
        self.dataSA16 = window.Int16Array.new(self.dataSAB)

        self.canvas = window.fabric.Canvas.new('c')
        self.canvas.preserveObjectStacking = True
        self.canvas.selection = False
        self.canvas.renderOnAddRemove = False
        self.canvas.on('mouse:down', self.OnFabricMouseDown)
        self.canvas.on('mouse:move', self.OnFabricMouseMove)
        self.canvas.on('mouse:up', self.OnFabricMouseUp)
        self.canvas.on('text:changed', self.OnTextChanged)
        document.onkeydown = self.OnKeyDown
        document.onkeyup = self.OnKeyUp

        self.fabObjs = {0: self.canvas}
        self.canvasSize = (500, 500)
        self.soundCache = {}
        self.imgCache = {}
        self.lastMousePos = (0,0)
        self.isLoading = False
        self.needsRender = False

        stackWorker.bind("message", self.OnMessageM)

        stackWorker.send(('setup', self.waitSAB, self.countsSAB, self.dataSAB))
        stackWorker.send(('load', window.stackJSON))

        timer.request_animation_frame(self.OnAnimationFrame)

    def LoadFromStr(self, s):
        stackWorker.send(('loadStr', s))

    def OnMessageM(self, evt):
        """Handles the messages sent by the worker."""
        self.HandleMessageM(evt.data)

    def Render(self):
        if not self.isLoading:
            self.needsRender = True

    def HandleMessageM(self, messages):
        for vals in messages:
            msg = vals[0]
            args = vals[1:]

            # if msg != "write": print("Main", msg, args)

            if msg == "canvasSetSize":  # x, y
                self.canvasSize = args

                self.canvas.setWidth(args[0])
                self.canvas.setHeight(args[1])

            elif msg == "didLoad":
                self.isLoading = False
                self.Render()

            elif msg == "willUnload":
                self.isLoading = True

            elif msg == "fabNew":  # uid, type, options
                uid = args[0]
                fabClass = window.fabric[args[1]]
                options = {'csid': uid,
                           'isType': args[1],
                           'centeredRotation': True,
                           'selectable': False,
                           'hoverCursor': "arrow"}
                options.update(args[-1].to_dict())
                fabObj = fabClass.new(*(args[2:-1]), options)
                fabObj.set()
                self.fabObjs[uid] = fabObj
                self.canvas.add(fabObj)

            elif msg == "imgNew":  # uid, filePath
                uid = args[0]
                filePath = args[1]

                # Set up placeholder rect
                fabObj = window.fabric.Rect.new(
                    {'csid': uid,
                     'isType': "Rect",
                     'strokeWidth': 0,
                     'selectable': False,
                     'hoverCursor': "arrow",
                     'filePath': filePath})
                self.fabObjs[uid] = fabObj
                self.canvas.add(fabObj)

                def didLoad(img, failed):
                    if not failed:
                        if filePath not in self.imgCache:
                            self.imgCache[filePath] = img
                        s = self.imgCache[filePath].getOriginalSize()
                        stackWorker.send(("imgSize", uid, s.width, s.height))

                if filePath in self.imgCache:
                    s = self.imgCache[filePath].getOriginalSize()
                    stackWorker.send(("imgSize", uid, s.width, s.height))
                else:
                    window.fabric.Image.fromURL(filePath, didLoad)

            elif msg == "imgReplace":  # uid, filePath
                uid = args[0]
                filePath = args[1]
                oldObj = self.fabObjs[uid]
                oldObj['filePath'] = filePath
                index = [o.csid for o in self.canvas.getObjects()].index(oldObj.csid)

                def didLoad(img, failed):
                    if not failed:
                        if filePath not in self.imgCache:
                            self.imgCache[filePath] = img
                        s = self.imgCache[filePath].getOriginalSize()
                        stackWorker.send(("imgSize", uid, s.width, s.height))

                if filePath in self.imgCache:
                    s = self.imgCache[filePath].getOriginalSize()
                    stackWorker.send(("imgSize", uid, s.width, s.height))
                else:
                    window.fabric.Image.fromURL(filePath, didLoad)

            elif msg == "imgRefit":  # uid, options
                uid = args[0]
                options = args[1]
                oldObj = self.fabObjs[uid]
                origImage = self.imgCache[oldObj.filePath]
                index = [o.csid for o in self.canvas.getObjects()].index(oldObj.csid)
                self.canvas.remove(oldObj)

                def setImg(img):
                    img.set({'csid': uid,
                             'isType': "Image",
                             'scaleX': options['scaleX'], 'scaleY': options['scaleY'],
                             'centeredRotation': True,
                             'selectable': False,
                             'hoverCursor': "arrow",
                             'filePath': oldObj.filePath,
                             'left': options['left'], 'top': options['top'],
                             'visible': options['visible']
                             })
                    img.rotate(options['angle'])
                    self.fabObjs[uid] = img
                    self.canvas.insertAt(img, index, False)
                    img.setCoords()
                    self.Render()

                origImage.cloneAsImage(setImg, {'left': int(options['clipLeft']), 'top': int(options['clipTop']),
                                                'width': int(options['clipWidth']), 'height': int(options['clipHeight'])})

            elif msg == "tboxNew":  # uid, text, options
                uid = args[0]
                text = args[1]
                fabObj = window.fabric.Textbox.new(text, args[2])

                fabObj.set({'csid': uid,
                            'isType': 'TextField',
                            'hasControls': False,
                            'lockMovementX': True,
                            'lockMovementY': True,
                            'centeredRotation': True,
                            'hoverCursor': "text"})
                self.fabObjs[uid] = fabObj

                self.canvas.add(fabObj)
                fabObj.on('selected', self.OnTextboxSelected)
                fabObj.on('deselected', self.OnTextboxDeselected)
                fabObj.oldOnKeyDown = fabObj.onKeyDown
                fabObj.onKeyDown = self.OnTextboxKeyDown

            elif msg == "fabReplace":  # uid, type, options
                uid = args[0]

                oldObj = self.fabObjs[uid]
                index = [o.csid for o in self.canvas.getObjects()].index(oldObj.csid)
                self.canvas.remove(oldObj)

                fabClass = window.fabric[args[1]]
                fabObj = fabClass.new(*args[2:])
                fabObj.set({'csid':uid,
                            'isType': args[1],
                            'hasControls': False,
                            'lockMovementX': True,
                            'lockMovementY': True,
                            'centeredRotation': True,
                            'selectable': False,
                            'hoverCursor': "arrow"})
                self.fabObjs[uid] = fabObj
                self.canvas.insertAt(fabObj, index, False)

            elif msg == "fabDel":  # uid, [more uids...]
                for uid in args:
                    fabObj = self.fabObjs[uid]
                    del self.fabObjs[uid]
                    if fabObj.isType == 'TextField':
                        fabObj.off('selected', self.OnTextboxSelected)
                        fabObj.off('deselected', self.OnTextboxDeselected)
                    self.canvas.remove(fabObj)

            elif msg == "fabFunc":  # uid, funcName, [args...]
                uid = args[0]
                fabObj = self.fabObjs[uid]
                fabFunc = fabObj[args[1]]
                fabFunc(*args[2:])

            elif msg == "fabSet":  # uid, options
                uid = args[0]
                options = args[1]
                fabObj = self.fabObjs[uid]
                fabObj.set(options)
                options = options.to_dict()
                if 'left' in options or 'width' in options:
                    fabObj.setCoords()

            elif msg == "fabReorder":  # uid, index
                uid = args[0]
                index = args[1]
                fabObj = self.fabObjs[uid]
                self.canvas.moveTo(fabObj, index)

            elif msg == "render":  # No args
                self.Render()

            elif msg == "focus":  # uid
                uid = args[0]
                fabObj = self.fabObjs[uid]
                self.canvas.setActiveObject(fabObj)

            elif msg == "alert":  # text
                self.canvas.requestRenderAll()
                timer.set_timeout(self.HandleMessageM, 20, (("alertInternal", *args),))
            elif msg == "alertInternal":
                text = args[0]
                window.alert(text)
                self.dataSA16[0] = 0
                self.waitSA32[0] = 1
                window.Atomics.notify(self.waitSA32, 0)

            elif msg == "confirm":  # text
                self.canvas.requestRenderAll()
                timer.set_timeout(self.HandleMessageM, 20, (("confirmInternal", *args),))
            elif msg == "confirmInternal":
                text = args[0]
                result = window.confirm(text)
                self.dataSA16[0] = result
                self.waitSA32[0] = 1
                window.Atomics.notify(self.waitSA32, 0)

            elif msg == "prompt":  # text, [defaultResponseText]
                self.canvas.requestRenderAll()
                timer.set_timeout(self.HandleMessageM, 20, (("promptInternal", *args),))
            elif msg == "promptInternal":
                text = args[0]
                default = "" if len(args) < 2 else args[1]
                result = window.prompt(text, default)
                if result is not None:
                    self.dataSA16[0] = len(result)
                    for i in range(len(result)):
                        self.dataSA16[i+1] = ord(result[i])
                else:
                    self.dataSA16[0] = -1  # Flag to return None
                self.waitSA32[0] = 1
                window.Atomics.notify(self.waitSA32, 0)

            elif msg == "playAudio":  # filePath
                file = args[0]
                if file in self.soundCache:
                    snd = self.soundCache[file]
                else:
                    path = "Resources/" + file
                    snd = window.Audio.new(path)
                    snd.load()
                if snd:
                    self.soundCache[file] = snd
                    snd.currentTime = 0
                    snd.play()

            elif msg == "stopAudio":  # No args
                for snd in self.soundCache.values():
                    snd.pause()

            elif msg == "write":  # text
                print(args[0], end='')

    def ConvPoint(self, x, y):
        return (x, self.canvasSize[1] - y)

    def OnFabricMouseDown(self, options):
        uid = 0
        if options.target:
            uid = options.target.csid
        pos = self.ConvPoint(options.e.pageX, options.e.pageY)
        self.lastMousePos = pos
        stackWorker.send(("mouseDown", uid, pos))

    def OnFabricMouseMove(self, options):
        uid = 0
        if options.target:
            uid = options.target.csid
        pos = self.ConvPoint(options.e.pageX, options.e.pageY)
        if pos[0] != self.lastMousePos[0] or pos[1] != self.lastMousePos[1]:
            self.lastMousePos = pos
            window.Atomics.add(self.countsSA32, 1, 1)
            stackWorker.send(("mouseMove", uid, pos))

    def OnFabricMouseUp(self, options):
        uid = 0
        if options.target:
            uid = options.target.csid
        pos = self.ConvPoint(options.e.pageX, options.e.pageY)
        self.lastMousePos = pos
        stackWorker.send(("mouseUp", uid, pos))

    def OnKeyDown(self, e):
        if e.key == "Tab":
            e.preventDefault()
        if not e.repeat:
            stackWorker.send(("keyDown", e.key))

    def OnKeyUp(self, e):
        stackWorker.send(("keyUp", e.key))

    def OnAnimationFrame(self, _dummy):
        timer.request_animation_frame(self.OnAnimationFrame)
        if not self.isLoading and self.needsRender:
            self.needsRender = False
            self.canvas.requestRenderAll()
        window.Atomics.add(self.countsSA32, 0, 1)
        stackWorker.send(("frame",))

    def OnTextboxKeyDown(self, e):
        fabObj = self.canvas.getActiveObject()
        if fabObj and fabObj.isType == 'TextField':
            fabObj.oldOnKeyDown(e)
            if not e.repeat:
                if "Arrow" in e.key:
                    self.OnKeyDown(e)
                if e.key in ("Enter", "Return"):
                    if not fabObj.isMultiline:
                        e.preventDefault()
                    stackWorker.send(("textEnter", fabObj.csid))

    def OnTextboxSelected(self, options):
        fabObj = options.target
        fabObj.enterEditing()
        end = len(fabObj.text)
        fabObj.setSelectionStart(end)
        fabObj.setSelectionEnd(end)
        stackWorker.send(("objectFocus", fabObj.csid))

    def OnTextChanged(self, options):
        uid = options.target.csid
        textbox = self.fabObjs[uid]
        stackWorker.send(("textChanged", uid, textbox.text))

    def OnTextboxDeselected(self, options):
        fabObj = options.target
        fabObj.exitEditing()
        fabObj = self.canvas.getActiveObject()
        if not fabObj:
            stackWorker.send(("objectFocus", 0))


class ConsoleOutput:
    def __init__(self, console, consoleLabel):
        self.console = console
        self.consoleLabel = consoleLabel
        self.text = ""
        self.dirty = False
        self.isShown = False

    def write(self, text):
        self.text += text
        self.dirty = True

    def update(self, force=False):
        if console and console.style.display == "block" and (force or self.dirty):
            self.console.text = self.text
            self.console.scrollTop = self.console.scrollHeight
            self.dirty = False

    def toggleConsole(self):
        self.isShown = not self.isShown
        console.style.display = "block" if (self.isShown) else "none"
        if self.isShown:
            self.consoleLabel.text = " (-) Hide Output"
            window.console.update(force=True)
        else:
            self.consoleLabel.text = " (+) Show Output"



if __name__ == "__main__":
    console = None
    consoleLabel = None
    if "console" in document and "consoleLabel" in document:
        console = document['console']
        consoleLabel = document['consoleLabel']
        cOutput = ConsoleOutput(console, consoleLabel)
        sys.stdout = cOutput
        sys.stderr = cOutput
        timer.set_interval(cOutput.update, 1000)
        window.console = cOutput
        window.toggleConsole = cOutput.toggleConsole

    window.stackCanvas = StackCanvas()

    print("window.crossOriginIsolated:", window.crossOriginIsolated)
